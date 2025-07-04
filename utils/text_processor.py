import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import string

class TextProcessor:
    """Text preprocessing and cleaning utilities"""
    
    def __init__(self):
        # Download required NLTK data
        self._download_nltk_data()
        self.stop_words = set(stopwords.words('english'))
    
    def _download_nltk_data(self):
        """Download required NLTK datasets"""
        datasets = ['punkt', 'stopwords', 'averaged_perceptron_tagger']
        for dataset in datasets:
            try:
                nltk.data.find(f'tokenizers/{dataset}')
            except LookupError:
                nltk.download(dataset, quiet=True)
    
    def preprocess(self, text):
        """
        Comprehensive text preprocessing
        
        Args:
            text (str): Raw input text
            
        Returns:
            str: Cleaned and preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Basic cleaning
        text = self._clean_text(text)
        
        # Remove extra whitespace
        text = self._normalize_whitespace(text)
        
        # Fix common encoding issues
        text = self._fix_encoding(text)
        
        # Ensure proper sentence structure
        text = self._fix_sentences(text)
        
        return text.strip()
    
    def _clean_text(self, text):
        """Remove unwanted characters and formatting"""
        # Remove HTML tags if present
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{2,}', '.', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()"\'-]', ' ', text)
        
        return text
    
    def _normalize_whitespace(self, text):
        """Normalize whitespace and remove extra spaces"""
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)
        
        # Remove spaces at beginning and end of lines
        text = '\n'.join(line.strip() for line in text.split('\n'))
        
        return text
    
    def _fix_encoding(self, text):
        """Fix common encoding issues"""
        # Replace common encoding artifacts
        replacements = {
            ''': "'", ''': "'", '"': '"', '"': '"',
            '–': '-', '—': '-', '…': '...',
            '\u00a0': ' ',  # Non-breaking space
            '\u2019': "'",  # Right single quotation mark
            '\u201c': '"',  # Left double quotation mark
            '\u201d': '"',  # Right double quotation mark
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _fix_sentences(self, text):
        """Ensure proper sentence structure"""
        # Split into sentences
        sentences = sent_tokenize(text)
        
        # Clean each sentence
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            
            # Skip very short sentences
            if len(sentence.split()) < 3:
                continue
            
            # Ensure sentence ends with punctuation
            if sentence and sentence[-1] not in '.!?':
                sentence += '.'
            
            # Capitalize first letter
            if sentence:
                sentence = sentence[0].upper() + sentence[1:]
            
            cleaned_sentences.append(sentence)
        
        return ' '.join(cleaned_sentences)
    
    def extract_keywords(self, text, top_n=10):
        """Extract important keywords from text"""
        # Tokenize and clean
        words = word_tokenize(text.lower())
        
        # Remove stopwords and punctuation
        words = [word for word in words 
                if word not in self.stop_words 
                and word not in string.punctuation 
                and len(word) > 2]
        
        # Calculate frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top keywords
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in top_words[:top_n]]
    
    def split_into_sections(self, text, max_length=1000):
        """Split text into manageable sections"""
        sentences = sent_tokenize(text)
        sections = []
        current_section = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > max_length and current_section:
                sections.append(' '.join(current_section))
                current_section = [sentence]
                current_length = sentence_length
            else:
                current_section.append(sentence)
                current_length += sentence_length
        
        if current_section:
            sections.append(' '.join(current_section))
        
        return sections
