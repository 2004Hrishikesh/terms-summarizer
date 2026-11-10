from models.summarizer import TextSummarizer


def test_chunk_text_splits_on_word_limit():
    words = " ".join(f"w{i}" for i in range(2500))
    chunks = TextSummarizer()._chunk_text(words, 1024)
    assert [len(c.split()) for c in chunks] == [1024, 1024, 452]


def test_models_are_not_loaded_at_startup():
    assert TextSummarizer().models == {}
