# dome-eval

Can small, local language models reliably monitor larger ones? This project evaluates
monitor models ("judges") for the output-verification gate (Gate 2) of the Silicon Dome
framework, on constrained hardware: an M1 laptop, a Raspberry Pi 5, and later a Jetson.

## Research questions

1. Does a purpose-built guard model (Granite Guardian) outperform a general small model
   as a monitor, given identical criteria?
2. Do judges respond to the *meaning* of a criterion or to its *wording*?
3. Does extreme weight compression (ternary/1-bit) preserve safety behaviour and tool-call accuracy?
4. What is the smallest monitor that remains useful on edge hardware?

## Principles

- **One interface, many backends.** Every model is reached via the OpenAI-compatible API
  (LM Studio, llama.cpp, OpenRouter, DeepSeek). Experiment code only knows backend *names*.
- **Chain of custody.** Every run records config hash, git commit, weights hash, backend,
  host and timing before producing output.
- **Hypothesis first.** A run refuses to start without its hypothesis file.
- **Stages are decoupled.** generate → judge → analyse, each writing JSONL to disk.
- **Raw outputs never enter git.** They live under `DATA_ROOT` on an encrypted drive.
- **Public adversarial data only.** No material from earlier, discontinued experiments.

## Quick start

```bash
git init && git add -A && git commit -m "Skeleton"
uv sync                          # create environment (writes uv.lock; commit it)
cp .env.example .env             # set DATA_ROOT and any cloud keys
uv run pre-commit install
uv run dome check                # which backends are up, which models they serve
uv run dome run configs/experiments/m1_smoke.yaml
uv run pytest
```

See `docs/SETUP.md` for machine setup.

## Layout

```
configs/        backends.yaml + one YAML per experiment
data/prompts/   small, public, versioned prompt sets
hypotheses/     pre-registered expectations, one file per experiment
notebook/       lab logbook
src/dome_eval/  package: config, backends, manifest, stages
tests/          unit tests (no network, no models)
```

## Milestones

1. Setup: one backend, one end-to-end logged call  ← current
2. Pilot: Guardian vs Ministral, built-in vs BYOC criteria
3. Robustness: criteria rephrasing
4. Compression: Bonsai vs Qwen base
5. Edge: smallest usable monitor on RPi / Jetson
6. Write-up: technical report + cleaned public repo
