"""Command line: `dome check`, `dome run <config>`, `dome hash <weights>`."""

from __future__ import annotations

import json
import os
import shutil
from datetime import UTC, datetime
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console

from dome_eval.backends import list_models
from dome_eval.config import load_backends, load_experiment
from dome_eval.manifest import build_manifest, weights_sha256
from dome_eval.stages.generate import run_generate

app = typer.Typer(add_completion=False, help="Local LLM monitor evaluation.")
console = Console()


def data_root() -> Path:
    """Where runs go. If DATA_ROOT is set it must already exist, so an unmounted
    external drive stops the run instead of spilling raw outputs onto the internal disk."""
    env = os.environ.get("DATA_ROOT")
    if not env:
        return Path("runs")
    root = Path(env).expanduser()
    if not root.is_dir():
        raise typer.BadParameter(f"DATA_ROOT {root} does not exist (drive not mounted?)")
    return root


@app.callback()
def _init() -> None:
    load_dotenv()


@app.command()
def check(backends_file: str = "configs/backends.yaml") -> None:
    """Ping every configured backend and list the models it serves."""
    for name, b in load_backends(backends_file).items():
        try:
            models = list_models(b)
            console.print(f"[green]OK[/]   {name:14} {b.base_url}  ({len(models)} models)")
            for m in models:
                console.print(f"       - {m}")
        except Exception as e:
            console.print(f"[red]FAIL[/] {name:14} {b.base_url}  {type(e).__name__}")


@app.command("hash")
def hash_weights(path: str) -> None:
    """SHA-256 of a model file or MLX model directory (cached)."""
    cache = data_root() / "weights.hashcache.json"
    cache.parent.mkdir(parents=True, exist_ok=True)
    console.print(weights_sha256(path, cache))


@app.command()
def run(config: str, backends_file: str = "configs/backends.yaml") -> None:
    """Run a generate experiment and write a manifest plus JSONL outputs."""
    exp, config_sha = load_experiment(config)
    backend = load_backends(backends_file)[exp.backend]

    if not Path(exp.hypothesis).exists():
        raise typer.BadParameter(f"Write the hypothesis first: {exp.hypothesis} not found")

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = data_root() / exp.id / stamp
    run_dir.mkdir(parents=True, exist_ok=False)
    shutil.copy(config, run_dir / "config.yaml")
    shutil.copy(exp.hypothesis, run_dir / "hypothesis.md")

    weights = None
    if exp.weights_path:
        console.print("Hashing weights (cached after first time)...")
        weights = weights_sha256(exp.weights_path, data_root() / "weights.hashcache.json")

    manifest = build_manifest(
        experiment_id=exp.id,
        config_sha256=config_sha,
        backend={"name": exp.backend, **backend.model_dump(exclude={"api_key_env"})},
        model=exp.model,
        weights_sha256=weights,
        status="running",
    )
    if manifest["git"]["dirty"]:
        console.print("[yellow]Warning: uncommitted changes; this run is not reproducible[/]")
    if backend.kind == "cloud":
        console.print("[yellow]Cloud backend: prompts leave this machine[/]")

    mpath = run_dir / "manifest.json"
    mpath.write_text(json.dumps(manifest, indent=2))

    n = run_generate(exp, backend, run_dir / "generations.jsonl")

    manifest |= {"status": "done", "n_records": n, "finished_utc": datetime.now(UTC).isoformat()}
    mpath.write_text(json.dumps(manifest, indent=2))
    console.print(f"[green]Done[/]: {n} records in {run_dir}")


if __name__ == "__main__":
    app()
