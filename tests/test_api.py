def test_health(api_client):
    assert api_client.get("/health").json() == {"status": "ok"}


def test_summarize_returns_summary_and_stats(api_client, sample_text):
    resp = api_client.post("/api/v1/summarize", json={"text": sample_text, "model": "lexrank", "sentences": 2})
    assert resp.status_code == 200
    body = resp.json()
    assert body["summary"]
    assert body["model"] == "lexrank"
    assert body["summary_words"] < body["original_words"]
    assert 0 < body["compression_ratio"] < 100


def test_rejects_unknown_model(api_client, sample_text):
    resp = api_client.post("/api/v1/summarize", json={"text": sample_text, "model": "gpt"})
    assert resp.status_code == 422


def test_rejects_short_text(api_client):
    resp = api_client.post("/api/v1/summarize", json={"text": "Too short."})
    assert resp.status_code == 422


def test_history_and_stats(api_client, sample_text):
    for model in ("lexrank", "lexrank", "legal"):
        api_client.post("/api/v1/summarize", json={"text": sample_text, "model": model})
    history = api_client.get("/api/v1/history?limit=2").json()
    assert len(history) == 2
    stats = {row["model"]: row["requests"] for row in api_client.get("/api/v1/stats").json()}
    assert stats == {"lexrank": 2, "legal": 1}
