import pytest

from dome_eval.jsonl import append_jsonl, read_jsonl


def test_roundtrip(tmp_path):
    p = tmp_path / "x.jsonl"
    append_jsonl(p, {"a": 1, "t": "é"})
    append_jsonl(p, {"a": 2})
    assert [r["a"] for r in read_jsonl(p)] == [1, 2]


def test_invalid_line_reports_location(tmp_path):
    p = tmp_path / "bad.jsonl"
    p.write_text('{"ok": 1}\nnot json\n')
    with pytest.raises(ValueError, match=":2:"):
        list(read_jsonl(p))
