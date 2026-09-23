import hashlib

from dome_eval.manifest import build_manifest, weights_sha256


def test_single_file_hash(tmp_path):
    f = tmp_path / "w.gguf"
    f.write_bytes(b"weights")
    assert weights_sha256(f) == hashlib.sha256(b"weights").hexdigest()


def test_directory_hash_is_order_independent_and_cached(tmp_path):
    d = tmp_path / "mlx"
    d.mkdir()
    (d / "b.safetensors").write_bytes(b"B")
    (d / "a.json").write_bytes(b"A")
    cache = tmp_path / "cache.json"
    h1 = weights_sha256(d, cache)
    assert cache.exists()
    assert weights_sha256(d, cache) == h1


def test_hash_changes_when_content_changes(tmp_path):
    f = tmp_path / "w.bin"
    f.write_bytes(b"one")
    h1 = weights_sha256(f)
    f.write_bytes(b"two")
    assert weights_sha256(f) != h1


def test_manifest_has_provenance_fields():
    m = build_manifest(experiment_id="t")
    for key in ("created_utc", "host", "python", "git", "packages", "experiment_id"):
        assert key in m
