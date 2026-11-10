FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/models \
    SUMMARIZER_DB=/data/summaries.db

WORKDIR /app

# CPU-only PyTorch keeps the image much smaller than the default CUDA build
RUN pip install --no-cache-dir torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m nltk.downloader -q punkt stopwords

COPY . .
RUN mkdir -p /data /models uploads

EXPOSE 5000 8000

# Web UI by default; docker-compose also starts the REST API on port 8000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "300", "app:app"]
