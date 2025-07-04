import os
import requests
from bs4 import BeautifulSoup
import PyPDF2
from docx import Document
import logging

class FileHandler:
    """Handle file uploads and text extraction from various sources"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.allowed_extensions = {'txt', 'pdf', 'doc', 'docx'}
    
    def allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def extract_text(self, filepath):
        """
        Extract text from uploaded file
        
        Args:
            filepath (str): Path to the uploaded file
            
        Returns:
            str: Extracted text content
        """
        try:
            file_extension = filepath.rsplit('.', 1)[1].lower()
            
            if file_extension == 'txt':
                return self._extract_from_txt(filepath)
            elif file_extension == 'pdf':
                return self._extract_from_pdf(filepath)
            elif file_extension in ['doc', 'docx']:
                return self._extract_from_docx(filepath)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
        except Exception as e:
            self.logger.error(f"Error extracting text from {filepath}: {str(e)}")
            return ""
    
    def _extract_from_txt(self, filepath):
        """Extract text from TXT file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(filepath, 'r', encoding='latin-1') as file:
                return file.read()
    
    def _extract_from_pdf(self, filepath):
        """Extract text from PDF file"""
        try:
            text = ""
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Error reading PDF: {str(e)}")
            return ""
    
    def _extract_from_docx(self, filepath):
        """Extract text from DOCX file"""
        try:
            doc = Document(filepath)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"Error reading DOCX: {str(e)}")
            return ""
    
    def extract_from_url(self, url):
        """
        Extract text content from a web URL
        
        Args:
            url (str): URL to extract text from
            
        Returns:
            str: Extracted text content
        """
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Make request with headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract text from specific elements that usually contain main content
            content_selectors = [
                'article', 'main', '.content', '.post-content', 
                '.entry-content', '.article-content', '#content'
            ]
            
            text = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        text += element.get_text(separator=' ', strip=True) + "\n"
                    break
            
            # If no specific content found, extract from body
            if not text.strip():
                body = soup.find('body')
                if body:
                    text = body.get_text(separator=' ', strip=True)
            
            # Clean up the text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
            
            return text
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching URL {url}: {str(e)}")
            return ""
        except Exception as e:
            self.logger.error(f"Error processing URL content: {str(e)}")
            return ""
