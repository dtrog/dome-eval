"""Run manifest: everything needed to reproduce or audit a run.

Chain-of-custody for experiments: config hash, code version, weights hash,
backend, host and timing are recorded before any output is produced.
"""

from __future__ import annotations

import hashlib
import json
import platform
import socket
import subprocess
import sys
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Any

CHUNK = 8 * 1024 * 1024


def git_state() -> dict[str, Any]:
    def run(*args: str) -> str:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, check=False
        ).stdout.strip()

    commit = run("rev-parse", "HEAD")
    return {
        "commit": commit or None,
        "dirty": bool(run("status", "--porcelain")) if commit else None,
    }


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK):
            h.update(chunk)
    return h.hexdigest()


def weights_sha256(path: str | Path, cache_file: str | Path | None = None) -> str:
    """Hash a model file, or a model directory (MLX) as a sorted combination of its files.

    Multi-GB hashing is slow, so results are cached by (path, size, mtime).
    """
    p = Path(path).expanduser().resolve()
    files = sorted(f for f in p.rglob("*") if f.is_file()) if p.is_dir() else [p]
    key = json.dumps([[str(f), f.stat().st_size, f.stat().st_mtime] for f in files])

    cache_path = Path(cache_file) if cache_file else None
    cache: dict[str, str] = {}
    if cache_path and cache_path.exists():
        cache = json.loads(cache_path.read_text())
    if key in cache:
        return cache[key]

    if p.is_dir():
        h = hashlib.sha256()
        for f in files:
            h.update(str(f.relative_to(p)).encode())
            h.update(_file_sha256(f).encode())
        digest = h.hexdigest()
    else:
        digest = _file_sha256(p)

    if cache_path:
        cache[key] = digest
        cache_path.write_text(json.dumps(cache))
    return digest


def package_versions(names: tuple[str, ...] = ("openai", "pydantic", "dome-eval")) -> dict:
    out = {}
    for n in names:
        try:
            out[n] = metadata.version(n)
        except metadata.PackageNotFoundError:
            out[n] = None
    return out


def build_manifest(**fields: Any) -> dict[str, Any]:
    return {
        "created_utc": datetime.now(UTC).isoformat(),
        "host": socket.gethostname(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "packages": package_versions(),
        "git": git_state(),
        **fields,
    }
