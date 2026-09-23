from pathlib import Path

from dome_eval.config import load_backends, load_experiment


def test_backends_parse():
    backends = load_backends("configs/backends.yaml")
    assert backends["lmstudio"].kind == "local"
    assert backends["openrouter"].api_key_env == "OPENROUTER_API_KEY"


def test_smoke_experiment_parses_and_hash_is_stable():
    exp, h1 = load_experiment("configs/experiments/m1_smoke.yaml")
    _, h2 = load_experiment("configs/experiments/m1_smoke.yaml")
    assert exp.id == "m1-smoke"
    assert exp.backend in load_backends("configs/backends.yaml")
    assert Path(exp.prompts).exists()
    assert h1 == h2 and len(h1) == 64
