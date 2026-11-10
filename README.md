# Terms & Conditions Summarizer

A Flask web app that summarizes terms-of-service and other legal text. It runs fully offline with open Hugging Face models, so no API keys are needed.

## Features

- Paste text, upload a `.txt`, `.pdf` or `.docx` file, or give a URL.
- Abstractive summaries with a DistilBART model fine-tuned on ToS;DR (`ml6team/distilbart-tos-summarizer-tosdr`), BART-large-CNN or T5-small.
- Extractive summaries with LexRank, Luhn or LSA (`sumy`).
- Long documents are split into 1024-word chunks, each chunk is summarized, and the partial summaries are summarized again.
- If a transformer model fails, the app falls back to LexRank.
- The result page shows the summary, up to five key sentences, word counts, the compression ratio and the processing time.

## Run with Docker

```bash
docker compose up --build
```

- Web app: http://localhost:5000
- REST API: http://localhost:8000 (interactive docs at `/docs`)

Models are downloaded on first use and cached in a Docker volume. Summary history is stored in SQLite in a second volume.

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py                   # web app on port 5000
uvicorn api:app --port 8000     # REST API on port 8000
```

## REST API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/v1/summarize` | Summarize text. Body: `{"text": "...", "model": "legal", "sentences": 3}` |
| GET | `/api/v1/history?limit=20` | Most recent summaries |
| GET | `/api/v1/stats` | Request count and average latency per model (SQL aggregate) |

```bash
curl -X POST localhost:8000/api/v1/summarize -H "Content-Type: application/json" \
     -d '{"text": "Paste the terms here ...", "model": "lexrank", "sentences": 3}'
```

Requests are validated with Pydantic. Unknown models or texts under 10 words return HTTP 422.

## Tests and CI

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```

- **Isolation:** the tests replace the models with a fake summarizer, so they run in under a second without loading any transformer model.
- **Coverage:** they test the web routes, file upload, the REST API, input validation and the SQLite history.
- **CI:** GitHub Actions runs linting and tests on every push, and builds the Docker image on `main`.

## Structure

```
app.py                   Flask web app
api.py                   FastAPI REST API
storage.py               SQLite summary history
models/summarizer.py     lazy model loading, chunking, abstractive and extractive summaries, key sentences
utils/file_handler.py    text extraction from txt, pdf, docx and web pages
utils/text_processor.py  text cleaning
templates/, static/      front end
tests/                   pytest suite
Dockerfile, docker-compose.yml, .github/workflows/ci.yml
```

The summaries are for quick reading and are not legal advice.
