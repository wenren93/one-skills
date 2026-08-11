---
name: model-lifecycle
description: "Model lifecycle: discover, download, and run models locally. HuggingFace Hub CLI + llama.cpp GGUF inference."
version: 1.0.0
author: Hugging Face, Orchestra Research, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [huggingface, hf, models, datasets, llama.cpp, GGUF, quantization, inference, mlops]
---

# Model Lifecycle

Two phases of working with models: **discovery** (finding and downloading from Hugging Face Hub) and **inference** (running models locally with llama.cpp). Use the right section for the task.

---

## Model Discovery (HuggingFace Hub CLI)

The `hf` command is the modern CLI for interacting with Hugging Face Hub. Replaces the deprecated `huggingface-cli`.

### Quick Start

```bash
curl -LsSf https://hf.co/cli/install.sh | bash -s
hf --help
```

### Authentication

```bash
hf auth login          # Interactive login
hf auth whoami         # Check current account
hf auth list           # List stored tokens
```

### Core Commands

```bash
hf download REPO_ID                          # Download files
hf upload REPO_ID                            # Upload files (single-commit)
hf upload-large-folder REPO_ID LOCAL_PATH    # Resumable uploads
hf sync                                      # Sync local ↔ Hub
hf env / hf version                          # Environment info
```

### Repository Management

```bash
hf repos create / delete / duplicate / move
hf repos branch / tag
hf repos delete-files
```

### Datasets & Models

```bash
hf datasets list / info / parquet
hf datasets sql "SELECT * FROM dataset LIMIT 10"    # DuckDB SQL on parquet
hf models list / info
hf papers list                                        # Daily papers
```

### Discussions & PRs

```bash
hf discussions list / create / info / comment / close / reopen
hf discussions diff / merge
```

### Infrastructure

- **Endpoints**: `hf endpoints deploy / pause / resume / scale-to-zero / catalog`
- **Jobs**: `hf jobs uv` for running Python scripts with inline dependencies
- **Spaces**: `hf spaces dev-mode` and `hot-reload` for Python files

### Storage & Automation

- **Buckets**: S3-like management (`create`, `cp`, `mv`, `rm`, `sync`)
- **Cache**: `hf cache list / prune / verify`
- **Webhooks**: `hf webhooks create / watch / enable / disable`
- **Collections**: `hf collections add-item / update / list`

### Global Flags

- `--format json` — machine-readable output
- `-q` / `--quiet` — IDs only

---

## Local Inference (llama.cpp + GGUF)

Run models locally on CPU, Apple Silicon, CUDA, ROCm, or Intel GPUs.

### Model Discovery Workflow

Prefer URL workflows before asking for scripts:

1. Search Hub: `https://huggingface.co/models?apps=llama.cpp&sort=trending`
2. Open repo: `https://huggingface.co/<repo>?local-app=llama.cpp`
3. Copy the exact `llama-server` or `llama-cli` command from the local-app snippet
4. Query tree API for available GGUFs: `https://huggingface.co/api/models/<repo>/tree/main?recursive=true`

### Install

```bash
brew install llama.cpp           # macOS / Linux
winget install llama.cpp         # Windows
# Or build from source:
git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
cmake -B build && cmake --build build --config Release
```

### Run from Hub

```bash
llama-cli -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
llama-server -hf bartowski/Llama-3.2-3B-Instruct-GGUF:Q8_0
```

### Run Exact File

```bash
llama-server \
    --hf-repo microsoft/Phi-3-mini-4k-instruct-gguf \
    --hf-file Phi-3-mini-4k-instruct-q4.gguf \
    -c 4096
```

### OpenAI-Compatible Server

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Write a limerick about Python"}]}'
```

### Python Bindings

```bash
pip install llama-cpp-python
# CUDA: CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
# Metal: CMAKE_ARGS="-DGGML_METAL=on" ...
```

```python
from llama_cpp import Llama

llm = Llama(model_path="./model-q4_k_m.gguf", n_ctx=4096, n_gpu_layers=35)
out = llm("What is machine learning?", max_tokens=256, temperature=0.7)
print(out["choices"][0]["text"])

# Load from Hub directly:
llm = Llama.from_pretrained(
    repo_id="bartowski/Llama-3.2-3B-Instruct-GGUF",
    filename="*Q4_K_M.gguf",
    n_gpu_layers=35,
)
```

### Choosing a Quant

Use the Hub page first, generic heuristics second:

- **General chat**: `Q4_K_M` (start here)
- **Code/technical**: `Q5_K_M` or `Q6_K` if memory allows
- **Tight RAM**: `Q3_K_M`, `IQ` variants
- Always prefer the exact quant HF marks as compatible for the user's hardware
- Don't normalize repo-native labels (if page says `UD-Q4_K_M`, report `UD-Q4_K_M`)

### Output Format for Discovery Requests

```
Repo: <repo>
Recommended quant from HF: <label> (<size>)
llama-server: <command>
Other GGUFs:
- <filename> - <size>
Source URLs:
- <local-app URL>
- <tree API URL>
```

---

## References

| File | Contents |
|------|----------|
| `references/hub-discovery.md` | URL-only HuggingFace workflows, search patterns, GGUF extraction |
| `references/advanced-usage.md` | Speculative decoding, batched inference, grammar-constrained generation, LoRA, multi-GPU |
| `references/quantization.md` | Quant quality tradeoffs, Q4/Q5/Q6/IQ, model size scaling, imatrix |
| `references/server.md` | Direct-from-Hub server launch, OpenAI API, Docker, NGINX, monitoring |
| `references/optimization.md` | CPU threading, BLAS, GPU offload heuristics, batch tuning, benchmarks |
| `references/troubleshooting.md` | Install/convert/quantize/inference/server issues, Apple Silicon debugging |

## Resources

- **llama.cpp GitHub**: https://github.com/ggml-org/llama.cpp
- **HF GGUF docs**: https://huggingface.co/docs/hub/gguf-llamacpp
- **HF Local Apps**: https://huggingface.co/docs/hub/main/local-apps
- **HF CLI install**: `curl -LsSf https://hf.co/cli/install.sh | bash -s`
