# Terms & Conditions Summarizer

A Flask web app that turns long terms-of-service and legal text into a short summary and a few key points. Everything runs locally with open Hugging Face models. It needs no API keys and no paid service.

## What it does

- **Input:** paste text, upload a `.txt` / `.pdf` / `.docx` file, or give a URL. Text is pulled out with PyPDF2, python-docx or BeautifulSoup.
- **Cleanup:** the input is cleaned before summarizing (encoding fixes, whitespace, broken sentences). See `utils/text_processor.py`.
- **Choose a summarizer:**

| Option | Model | Type |
|---|---|---|
| Legal (default in the UI) | `ml6team/distilbart-tos-summarizer-tosdr`, a DistilBART fine-tuned on ToS;DR | abstractive |
| BART | `facebook/bart-large-cnn` | abstractive |
| T5 | `t5-small` | abstractive |
| LexRank / Luhn / LSA | `sumy` | extractive |

- **Long documents:** split into 1024-word chunks, each chunk is summarized, and the partial summaries are summarized again.
- **Fallback:** if a transformer model fails, the app falls back to LexRank.
- **Output:** the summary, up to 5 key sentences picked by keyword frequency, word counts, the compression ratio and the processing time.

## Run it

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py                   # open http://localhost:5000
```

The first run downloads the three models (about 2 GB in total).

## Tests

```bash
python -m unittest test_app.py test_summary_accuracy.py
```

`test_app.py` checks `.txt` and `.pdf` uploads. `test_summary_accuracy.py` compares a LexRank summary with a reference summary using TF-IDF cosine similarity.

## Project layout

```
app.py                  Flask routes (text / file / URL input -> summary page)
models/summarizer.py    model loading, chunking, abstractive + extractive summaries, key points
utils/file_handler.py   text extraction from txt, pdf, docx and web pages
utils/text_processor.py text cleaning
templates/, static/     UI
```

## Limitations

- The models summarize text; they do not interpret it legally. Do not rely on the output as legal advice.
- The repo does not include a summary-quality benchmark (for example ROUGE on ToS;DR).
