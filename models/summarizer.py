"""Summarization models: abstractive (Hugging Face) and extractive (sumy)."""

import logging
import threading
import time

import nltk
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.luhn import LuhnSummarizer

ABSTRACTIVE_MODELS = {
    "legal": "ml6team/distilbart-tos-summarizer-tosdr",
    "bart": "facebook/bart-large-cnn",
    "t5": "t5-small",
}
EXTRACTIVE_METHODS = ("lexrank", "luhn", "lsa")
SUPPORTED_MODELS = tuple(ABSTRACTIVE_MODELS) + EXTRACTIVE_METHODS


def _ensure_punkt():
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt", quiet=True)


class TextSummarizer:
    """Summarizer with lazy model loading.

    Transformer models are loaded the first time they are requested, so the
    app starts quickly and only keeps the models that are actually used.
    """

    def __init__(self):
        self.models = {}
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()

    def _get_model(self, model_type):
        """Load a Hugging Face summarization pipeline once and cache it."""
        if model_type not in ABSTRACTIVE_MODELS:
            raise ValueError(f"Unknown abstractive model: {model_type}")
        with self._lock:
            if model_type not in self.models:
                import torch
                from transformers import pipeline

                device = 0 if torch.cuda.is_available() else -1
                self.logger.info("Loading %s", ABSTRACTIVE_MODELS[model_type])
                self.models[model_type] = pipeline(
                    "summarization", model=ABSTRACTIVE_MODELS[model_type], device=device
                )
        return self.models[model_type]

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
            if model_type in ABSTRACTIVE_MODELS:
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
            model = self._get_model(model_type)

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
            _ensure_punkt()
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
