import storage


def test_save_and_read_back():
    first = storage.save_summary("api", "legal", 100, 20, 0.5, "First summary.")
    second = storage.save_summary("text", "lexrank", 80, 10, 0.1, "Second summary.")
    assert second > first
    rows = storage.recent_summaries()
    assert [r["summary"] for r in rows] == ["Second summary.", "First summary."]


def test_usage_by_model_groups_and_averages():
    storage.save_summary("api", "legal", 100, 20, 1.0, "a")
    storage.save_summary("api", "legal", 100, 20, 3.0, "b")
    storage.save_summary("api", "t5", 100, 20, 2.0, "c")
    usage = storage.usage_by_model()
    assert usage[0] == {"model": "legal", "requests": 2, "avg_seconds": 2.0}
