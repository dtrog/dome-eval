"""One interface, many backends: every model is reached through the OpenAI-compatible API."""

from __future__ import annotations

import os

from openai import OpenAI

from dome_eval.config import Backend


def make_client(backend: Backend, timeout: float = 600.0) -> OpenAI:
    if backend.api_key_env:
        key = os.environ.get(backend.api_key_env)
        if not key:
            raise RuntimeError(f"Environment variable {backend.api_key_env} is not set")
    else:
        key = "local"  # local servers ignore the key but the client requires one
    return OpenAI(base_url=backend.base_url, api_key=key, timeout=timeout)


def list_models(backend: Backend) -> list[str]:
    client = make_client(backend, timeout=10.0)
    return [m.id for m in client.models.list().data]
