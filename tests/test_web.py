from io import BytesIO

import storage


def test_index_page_loads(flask_client):
    resp = flask_client.get("/")
    assert resp.status_code == 200


def test_text_input_shows_summary(flask_client, sample_text):
    resp = flask_client.post(
        "/summarize",
        data={"input_method": "text", "text_input": sample_text, "summary_length": "2", "model_type": "lexrank"},
    )
    assert resp.status_code == 200
    assert b"These terms govern" in resp.data
    assert storage.recent_summaries()[0]["source"] == "text"


def test_txt_upload(flask_client, sample_text):
    resp = flask_client.post(
        "/summarize",
        data={
            "input_method": "file",
            "file": (BytesIO(sample_text.encode()), "terms.txt"),
            "summary_length": "2",
            "model_type": "lexrank",
        },
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    assert storage.recent_summaries()[0]["source"] == "file"


def test_unsupported_file_type_redirects(flask_client):
    resp = flask_client.post(
        "/summarize",
        data={"input_method": "file", "file": (BytesIO(b"data"), "terms.exe"), "summary_length": "2"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 302


def test_short_text_redirects(flask_client):
    resp = flask_client.post("/summarize", data={"input_method": "text", "text_input": "Too short."})
    assert resp.status_code == 302
