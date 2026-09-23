# Machine setup

## M1 MacBook (main experiment node)

1. **External NVMe**: Disk Utility → Erase → *APFS (Encrypted)*, name it `LAB`.
   Create `/Volumes/LAB/dome-eval` and `/Volumes/LAB/models`.
2. **LM Studio**: Settings → change the models directory to `/Volumes/LAB/models`
   (move existing models there). Developer tab → start the server (port 1234).
   Load one model at a time; with 16 GB unified memory, stay under ~11 GB of weights.
3. **uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
4. **Repo**: `git clone …`, then `uv sync`, `cp .env.example .env`, `uv run pre-commit install`.
5. **Check**: `uv run dome check` should show `lmstudio` as OK with your loaded model.

Note: if the external drive is not mounted, runs fail on purpose (DATA_ROOT missing)
rather than silently writing raw outputs to the internal disk. Leave DATA_ROOT set.

## Raspberry Pi 5 (edge node)

```bash
sudo apt install -y build-essential cmake git
git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
cmake -B build && cmake --build build -j4 --config Release
./build/bin/llama-server -m ~/models/<model>.gguf --host 0.0.0.0 --port 8080 -c 4096
```

Then `uv run dome check` on the Mac should show `llamacpp-pi` as OK.

## Lenovo (Ubuntu)

SSH terminal and light tasks. Would serve as the flashing host for a Jetson.

## Cloud backends

Only for reference runs (full-precision baselines, large "gold" judges).
Every cloud run is flagged in its manifest. Keep sensitive material local.
