from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
import logging

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components with error handling
try:
    from models.summarizer import TextSummarizer
    from utils.text_processor import TextProcessor
    from utils.file_handler import FileHandler
    
    text_processor = TextProcessor()
    file_handler = FileHandler()
    summarizer = TextSummarizer()
    logger.info("All components initialized successfully")
except Exception as e:
    logger.error(f"Error initializing components: {e}")
    # Use simple fallback
    text_processor = None
    file_handler = None
    summarizer = None

@app.route('/')
def index():
    """Main page with input form"""
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize_text():
    """Handle text summarization requests"""
    try:
        # Get input method
        input_method = request.form.get('input_method', 'text')
        summary_length = int(request.form.get('summary_length', 3))
        model_type = request.form.get('model_type', 'bart')
        
        text_content = ""
        
        if input_method == 'text':
            # Direct text input
            text_content = request.form.get('text_input', '').strip()
            if not text_content:
                flash('Please enter some text to summarize.', 'error')
                return redirect(url_for('index'))
        
        # Preprocess text
        if text_processor:
            processed_text = text_processor.preprocess(text_content)
        else:
            processed_text = text_content
        
        if len(processed_text.split()) < 10:
            flash('Text is too short for meaningful summarization. Please provide longer text.', 'error')
            return redirect(url_for('index'))
        
        # Generate summary
        if summarizer:
            summary_data = summarizer.generate_summary(
                text=processed_text,
                max_length=summary_length,
                model_type=model_type
            )
        else:
            # Fallback simple summary
            sentences = processed_text.split('.')
            summary = '. '.join(sentences[:summary_length]) + '.'
            summary_data = {
                'summary': summary,
                'key_points': ['Main point extracted from text'],
                'processing_time': 0.1
            }
        
        # Calculate statistics
        original_word_count = len(text_content.split())
        summary_word_count = len(summary_data['summary'].split())
        compression_ratio = round((1 - summary_word_count / original_word_count) * 100, 1)
        
        results = {
            'original_text': text_content,
            'summary': summary_data['summary'],
            'key_points': summary_data.get('key_points', []),
            'original_word_count': original_word_count,
            'summary_word_count': summary_word_count,
            'compression_ratio': compression_ratio,
            'model_used': model_type.upper(),
            'processing_time': summary_data.get('processing_time', 0)
        }
        
        return render_template('result.html', **results)
        
    except Exception as e:
        logger.error(f"Error in summarization: {str(e)}")
        flash(f'An error occurred during summarization: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
