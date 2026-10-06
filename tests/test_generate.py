from types import SimpleNamespace

from openai.types.chat import ChatCompletion

from dome_eval.config import Backend, GenerateExperiment
from dome_eval.jsonl import read_jsonl
from dome_eval.stages import generate


def _completion(content, finish_reason, reasoning=None):
    message = {"role": "assistant", "content": content}
    if reasoning is not None:
        message["reasoning_content"] = reasoning
    return ChatCompletion.model_validate(
        {
            "id": "x",
            "object": "chat.completion",
            "created": 0,
            "model": "m",
            "choices": [{"index": 0, "message": message, "finish_reason": finish_reason}],
        }
    )


def _run(tmp_path, monkeypatch, resp):
    prompts = tmp_path / "p.jsonl"
    prompts.write_text('{"id": "p1", "prompt": "hi"}\n')
    create = lambda **_: resp  # noqa: E731
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    monkeypatch.setattr(generate, "make_client", lambda _: client)
    exp = GenerateExperiment(
        id="t", hypothesis="h.md", backend="b", model="m", prompts=str(prompts)
    )
    backend = Backend(base_url="http://x", kind="local", node="n")
    out = tmp_path / "out.jsonl"
    generate.run_generate(exp, backend, out)
    return next(read_jsonl(out))


def test_empty_content_is_recorded_as_error(tmp_path, monkeypatch):
    rec = _run(tmp_path, monkeypatch, _completion("", "length", reasoning="thinking..."))
    assert rec["error"] == "EmptyResponse: no content (finish_reason=length)"
    assert rec["reasoning"] == "thinking..."


def test_normal_response_has_no_error(tmp_path, monkeypatch):
    rec = _run(tmp_path, monkeypatch, _completion("answer", "stop"))
    assert rec["response"] == "answer"
    assert rec["reasoning"] is None
    assert rec["error"] is None
