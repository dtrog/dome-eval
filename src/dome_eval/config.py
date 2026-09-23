"""Typed configuration: backends and experiments."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field


class Backend(BaseModel):
    base_url: str
    kind: Literal["local", "cloud"]
    node: str
    api_key_env: str | None = None


class Sampling(BaseModel):
    temperature: float = 0.0
    max_tokens: int = 256
    seed: int | None = None


class GenerateExperiment(BaseModel):
    id: str
    hypothesis: str
    stage: Literal["generate"] = "generate"
    backend: str
    model: str
    weights_path: str | None = None
    prompts: str
    sampling: Sampling = Field(default_factory=Sampling)
    extra_body: dict[str, Any] = Field(default_factory=dict)


def load_backends(path: str | Path = "configs/backends.yaml") -> dict[str, Backend]:
    raw = yaml.safe_load(Path(path).read_text())
    return {name: Backend(**spec) for name, spec in raw.items()}


def load_experiment(path: str | Path) -> tuple[GenerateExperiment, str]:
    """Return the parsed experiment plus the SHA-256 of the exact config text."""
    text = Path(path).read_text()
    exp = GenerateExperiment(**yaml.safe_load(text))
    return exp, hashlib.sha256(text.encode()).hexdigest()
