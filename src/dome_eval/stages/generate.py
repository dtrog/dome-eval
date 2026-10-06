"""Stage 1: generate responses and write them, one per line, to the run directory."""

from __future__ import annotations

import time
from pathlib import Path

from dome_eval.backends import make_client
from dome_eval.config import Backend, GenerateExperiment
from dome_eval.jsonl import append_jsonl, read_jsonl


def run_generate(exp: GenerateExperiment, backend: Backend, out_path: Path) -> int:
    client = make_client(backend)
    n = 0
    for item in read_jsonl(exp.prompts):
        t0 = time.perf_counter()
        record: dict = {"prompt_id": item["id"], "prompt": item["prompt"]}
        try:
            resp = client.chat.completions.create(
                model=exp.model,
                messages=[{"role": "user", "content": item["prompt"]}],
                temperature=exp.sampling.temperature,
                max_tokens=exp.sampling.max_tokens,
                seed=exp.sampling.seed,
                extra_body=exp.extra_body or None,
            )
            choice = resp.choices[0]
            content = choice.message.content
            record |= {
                "response": content,
                # Thinking models (served by LM Studio, llama.cpp) return their reasoning here.
                "reasoning": (choice.message.model_extra or {}).get("reasoning_content"),
                "finish_reason": choice.finish_reason,
                "served_model": resp.model,
                "usage": resp.usage.model_dump() if resp.usage else None,
                "error": None,
            }
            if not (content or "").strip():
                # e.g. a thinking model spending all of max_tokens on reasoning
                reason = choice.finish_reason
                record["error"] = f"EmptyResponse: no content (finish_reason={reason})"
        except Exception as e:  # record failures instead of losing the run
            record |= {"response": None, "error": f"{type(e).__name__}: {e}"}
        record["latency_s"] = round(time.perf_counter() - t0, 3)
        append_jsonl(out_path, record)
        n += 1
    return n
