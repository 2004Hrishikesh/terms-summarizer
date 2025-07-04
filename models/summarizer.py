import time
import logging

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
import torch

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class TextSummarizer:
    """Comprehensive text summarization class with multiple model support"""
    
    def __init__(self):
        self.models = {}
        self.logger = logging.getLogger(__name__)
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all available summarization models"""
        try:
            # BART model for abstractive summarization
            self.models['bart'] = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # T5 model for versatile summarization
            self.models['t5'] = pipeline(
                "summarization",
                model="t5-small",
                device=0 if torch.cuda.is_available() else -1
            )
            
            # DistilBART specifically for legal documents
            tokenizer = AutoTokenizer.from_pretrained("ml6team/distilbart-tos-summarizer-tosdr")
            model = AutoModelForSeq2SeqLM.from_pretrained("ml6team/distilbart-tos-summarizer-tosdr")
            
            self.models['legal'] = pipeline(
                "summarization",
                model=model,
                tokenizer=tokenizer,
                device=0 if torch.cuda.is_available() else -1
            )
            
            self.logger.info("All models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing models: {str(e)}")
    
    def generate_summary(self, text, max_length=3, model_type='bart'):
        """
        Generate comprehensive summary with multiple approaches
        
        Args:
            text (str): Input text to summarize
            max_length (int): Maximum number of sentences in summary
            model_type (str): Model to use ('bart', 't5', 'legal', 'extractive')
        
        Returns:
            dict: Summary results with metadata
        """
        start_time = time.time()
        
        try:
            if model_type in ['bart', 't5', 'legal']:
                summary = self._abstractive_summary(text, max_length, model_type)
            else:
                summary = self._extractive_summary(text, max_length, model_type)
            
            # Extract key points
            key_points = self._extract_key_points(text)
            
            processing_time = round(time.time() - start_time, 2)
            
            return {
                'summary': summary,
                'key_points': key_points,
                'processing_time': processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Summarization error: {str(e)}")
            raise
    
    def _abstractive_summary(self, text, max_length, model_type):
        """Generate abstractive summary using transformer models"""
        try:
            model = self.models.get(model_type)
            if not model:
                raise ValueError(f"Model {model_type} not available")
            
            # Handle long texts by chunking
            max_chunk_length = 1024
            chunks = self._chunk_text(text, max_chunk_length)
            
            summaries = []
            for chunk in chunks:
                result = model(
                    chunk,
                    max_length=min(150, len(chunk.split()) // 3),
                    min_length=30,
                    do_sample=False,
                    length_penalty=2.0,
                    num_beams=4,
                    early_stopping=True
                )
                summaries.append(result[0]['summary_text'])
            
            # If multiple chunks, summarize the summaries
            if len(summaries) > 1:
                combined_summary = " ".join(summaries)
                if len(combined_summary.split()) > max_length * 20:
                    final_result = model(
                        combined_summary,
                        max_length=max_length * 20,
                        min_length=max_length * 10,
                        do_sample=False
                    )
                    return final_result[0]['summary_text']
                return combined_summary
            
            return summaries[0]
            
        except Exception as e:
            self.logger.error(f"Abstractive summarization error: {str(e)}")
            # Fallback to extractive
            return self._extractive_summary(text, max_length, 'lexrank')
    
    def _extractive_summary(self, text, max_length, algorithm='lexrank'):
        """Generate extractive summary using traditional algorithms"""
        try:
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            
            if algorithm == 'lexrank':
                summarizer = LexRankSummarizer()
            elif algorithm == 'luhn':
                summarizer = LuhnSummarizer()
            elif algorithm == 'lsa':
                summarizer = LsaSummarizer()
            else:
                summarizer = LexRankSummarizer()  # Default
            
            sentences = summarizer(parser.document, max_length)
            return ' '.join([str(sentence) for sentence in sentences])
            
        except Exception as e:
            self.logger.error(f"Extractive summarization error: {str(e)}")
            # Simple fallback
            sentences = text.split('.')[:max_length]
            return '. '.join(sentences) + '.'
    
    def _chunk_text(self, text, max_length):
        """Split text into manageable chunks for processing"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), max_length):
            chunk = ' '.join(words[i:i + max_length])
            chunks.append(chunk)
        
        return chunks
    
    def _extract_key_points(self, text):
        """Extract key points and important phrases from text"""
        try:
            # Simple keyword extraction based on frequency
            words = text.lower().split()
            
            # Remove common words
            stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'shall', 'can'])
            
            filtered_words = [word.strip('.,!?;:"()[]') for word in words if word.lower() not in stop_words and len(word) > 3]
            
            # Count frequency
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Get top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Extract sentences containing top keywords
            sentences = text.split('.')
            key_sentences = []
            
            for sentence in sentences[:20]:  # Limit to first 20 sentences
                sentence = sentence.strip()
                if len(sentence) > 30:  # Minimum sentence length
                    for keyword, _ in top_keywords[:5]:
                        if keyword.lower() in sentence.lower():
                            key_sentences.append(sentence + '.')
                            break
            
            return key_sentences[:5]  # Return top 5 key points
            
        except Exception as e:
            self.logger.error(f"Key point extraction error: {str(e)}")
            return []

# Initialize the summarizer (downloaded automatically if not cached)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_with_local_model(text, max_length=150, min_length=40):
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']
