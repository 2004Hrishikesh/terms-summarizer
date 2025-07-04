# Terms & Conditions Summarizer

This Flask-based web app summarizes long legal documents using a locally deployed Hugging Face model (e.g., BART or LED).

## Features
- Upload PDF or text files
- Summarizes legal-style documents
- No API keys required
- Works offline

## Setup

```bash
git clone https://github.com/yourusername/terms-summarizer.git
cd terms-summarizer
python -m venv venv
source venv/bin/activate  # or venv\\Scripts\\activate on Windows
pip install -r requirements.txt
python app.py
