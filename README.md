# Terms & Conditions Summarizer

A Flask web app that summarizes terms-of-service and other legal text. It runs fully offline with open Hugging Face models, so no API keys are needed.

## Features

- Paste text, upload a `.txt`, `.pdf` or `.docx` file, or give a URL.
- Abstractive summaries with a DistilBART model fine-tuned on ToS;DR (`ml6team/distilbart-tos-summarizer-tosdr`), BART-large-CNN or T5-small.
- Extractive summaries with LexRank, Luhn or LSA (`sumy`).
- Long documents are split into 1024-word chunks, each chunk is summarized, and the partial summaries are summarized again.
- If a transformer model fails, the app falls back to LexRank.
- The result page shows the summary, up to five key sentences, word counts, the compression ratio and the processing time.

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The app runs at http://localhost:5000. The first run downloads the models (about 2 GB).

## Tests

```bash
python -m unittest test_app.py test_summary_accuracy.py
```

- `test_app.py` covers file uploads.
- `test_summary_accuracy.py` compares a LexRank summary with a reference summary using TF-IDF cosine similarity.

## Structure

```
app.py                   Flask routes
models/summarizer.py     model loading, chunking, abstractive and extractive summaries, key sentences
utils/file_handler.py    text extraction from txt, pdf, docx and web pages
utils/text_processor.py  text cleaning
templates/, static/      front end
```

The summaries are for quick reading and are not legal advice.
