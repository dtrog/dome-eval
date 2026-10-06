# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Research harness evaluating whether small, local LLMs can act as monitors ("judges") for
Gate 2 (output verification) of the Silicon Dome framework, on constrained hardware
(M1 MacBook, Raspberry Pi 5, later Jetson). See README.md for research questions and milestones;
the project is currently at milestone 1 (one backend, one end-to-end logged call).

## Commands

```bash
uv sync                                         # install (dev group included by default)
uv sync --group analysis                        # add duckdb/pandas for analysis work
uv run pytest                                   # all tests (no network, no models)
uv run pytest tests/test_config.py::test_backends_parse   # single test
uv run ruff check . && uv run ruff format .     # lint/format (line length 100, py311)
uv run dome check                               # ping every backend, list served models
uv run dome run configs/experiments/m1_smoke.yaml
uv run dome hash <model file or MLX dir>        # cached SHA-256 of weights
```

Commands must be run from the repo root: config, prompt and hypothesis paths are relative.

## Architecture

- **Backends** (`configs/backends.yaml` → `config.Backend` → `backends.make_client`): every model,
  local or cloud, is reached through the `openai` client pointed at an OpenAI-compatible
  `base_url`. Experiment configs refer to backends only by name. `api_key_env` is the *name* of
  an environment variable (loaded from `.env` via python-dotenv), never the key itself; omit it
  for local servers. `kind: cloud` triggers a warning that prompts leave the machine.
- **Experiments** (`configs/experiments/*.yaml` → `config.GenerateExperiment`): `load_experiment`
  returns the parsed model plus the SHA-256 of the exact YAML text, which goes in the manifest.
  Only the `generate` stage exists; `m2_pilot.draft.yaml` documents the planned multi-judge
  schema and does not parse with the current models.
- **Run flow** (`cli.run`): refuses to start unless the `hypothesis` file exists → creates
  `<DATA_ROOT>/<exp.id>/<UTC stamp>/` → copies config and hypothesis in → writes `manifest.json`
  (`status: running`; git commit/dirty flag, host, package versions, config hash, optional
  weights hash) *before* any output → `stages.generate.run_generate` appends one record per
  prompt to `generations.jsonl` → manifest rewritten with `status: done`.
- **DATA_ROOT**: if set, it must already exist (encrypted external drive); an unmounted drive
  aborts the run rather than writing raw outputs to the internal disk. Unset → `./runs`.
- **Stages are decoupled via JSONL on disk** (`jsonl.py`, append + flush per record). Generation
  failures are recorded in the record's `error` field, not raised. `stages/judge.py` and
  `stages/analyse.py` are design-note stubs: judges read a finished `generations.jsonl` (never
  regenerate), write one output file per judge, and return pydantic-validated JSON scores in
  [0, 1] per criterion.

## Research conventions

- **Hypothesis first**: each experiment has a pre-registered file in `hypotheses/` (copy
  `000-template.md`), written before running; the Outcome section is filled in afterwards.
- **Criteria** (`criteria/vX.Y/`, one Markdown file per criterion, format in `criteria/README.md`):
  never edit a released version in place; copy to a new version folder. All judges get identical
  criteria text so differences are attributable to the model.
- Raw run outputs never go into git. Prompt sets in `data/prompts/` must be small, public data
  only (JSONL with `id` and `prompt`).
- A dirty git tree makes a run non-reproducible (warned, recorded in the manifest), so commit
  before real runs.
- `notebook/LOGBOOK.md` is a dated lab log that feeds the write-up.
- Tests in `tests/` read the real files under `configs/` (e.g. `test_backends_parse` asserts
  `openrouter.api_key_env == "OPENROUTER_API_KEY"`), so config edits can break them.
