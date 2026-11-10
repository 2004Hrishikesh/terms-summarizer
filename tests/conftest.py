import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import storage  # noqa: E402


class FakeSummarizer:
    """Stands in for the real models so tests run fast and offline."""

    def generate_summary(self, text, max_length=3, model_type="legal"):
        sentences = [s.strip() for s in text.split(".") if s.strip()]
        return {
            "summary": ". ".join(sentences[:max_length]) + ".",
            "key_points": sentences[:2],
            "processing_time": 0.01,
        }


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "test.db"))


@pytest.fixture
def sample_text():
    return (
        "These terms govern your use of the service. "
        "By creating an account you agree to share usage data with our partners. "
        "We may change these terms at any time without notice. "
        "You can cancel your subscription from the settings page. "
        "Refunds are not available after thirty days."
    )


@pytest.fixture
def flask_client(monkeypatch):
    import app as web

    monkeypatch.setattr(web, "summarizer", FakeSummarizer())
    web.app.config["TESTING"] = True
    return web.app.test_client()


@pytest.fixture
def api_client(monkeypatch):
    from fastapi.testclient import TestClient

    import api

    monkeypatch.setattr(api, "summarizer", FakeSummarizer())
    return TestClient(api.app)
