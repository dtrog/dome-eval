"""Append-only JSONL: one record per line, flushed immediately so a crash loses nothing."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any


def read_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    with Path(path).open() as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{line_no}: invalid JSON") from e


def append_jsonl(path: str | Path, record: dict[str, Any]) -> None:
    with Path(path).open("a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()
