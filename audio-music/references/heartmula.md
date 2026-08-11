# HeartMuLa — Open-Source Music Generation

HeartMuLa is a family of open-source music foundation models (Apache-2.0) that generates music conditioned on lyrics and tags, with multilingual support. Comparable to Suno for open-source.

## When to Use

- User wants to generate music/songs from text descriptions
- User wants an open-source Suno alternative
- User wants local/offline music generation

## Hardware Requirements

- **Minimum**: 8GB VRAM with `--lazy_load true`
- **Recommended**: 16GB+ VRAM
- **Multi-GPU**: `--mula_device cuda:0 --codec_device cuda:1`
- 3B model with lazy_load peaks at ~6.2GB VRAM

## Installation

```bash
cd ~/
git clone https://github.com/HeartMuLa/heartlib.git
cd heartlib
uv venv --python 3.10 .venv
. .venv/bin/activate
uv pip install -e .
uv pip install --upgrade datasets transformers
```

### Required Patches (as of Feb 2026)

**Patch 1 — RoPE cache fix** in `src/heartlib/heartmula/modeling_heartmula.py`:
In `setup_caches`, add after the `reset_caches` try/except and before `with device:`:
```python
from torchtune.models.llama3_1._position_embeddings import Llama3ScaledRoPE
for module in self.modules():
    if isinstance(module, Llama3ScaledRoPE) and not module.is_cache_built:
        module.rope_init()
        module.to(device)
```

**Patch 2 — HeartCodec loading fix** in `src/heartlib/pipelines/music_generation.py`:
Add `ignore_mismatched_sizes=True` to all `HeartCodec.from_pretrained()` calls.

### Download Models
```bash
hf download --local-dir './ckpt' 'HeartMuLa/HeartMuLaGen'
hf download --local-dir './ckpt/HeartMuLa-oss-3B' 'HeartMuLa/HeartMuLa-oss-3B-happy-new-year'
hf download --local-dir './ckpt/HeartCodec-oss' 'HeartMuLa/HeartCodec-oss-20260123'
```

## Usage

```bash
cd heartlib && . .venv/bin/activate
python ./examples/run_music_generation.py \
  --model_path=./ckpt --version="3B" \
  --lyrics="./assets/lyrics.txt" \
  --tags="./assets/tags.txt" \
  --save_path="./assets/output.mp3" \
  --lazy_load true
```

**Tags**: comma-separated, no spaces: `piano,happy,wedding,synthesizer,romantic`

**Lyrics**: use bracketed structural tags: `[Intro]`, `[Verse]`, `[Chorus]`, `[Bridge]`, `[Outro]`

## Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--max_audio_length_ms` | 240000 | Max length (240s = 4 min) |
| `--lazy_load` | false | Load/unload models on demand (saves VRAM) |
| `--mula_dtype` | bfloat16 | bf16 recommended for MuLa |
| `--codec_dtype` | float32 | fp32 recommended for quality |

## Pitfalls

1. **Do NOT use bf16 for HeartCodec** — degrades audio quality.
2. **Tags may be ignored** — known issue. Lyrics tend to dominate.
3. **Triton not available on macOS** — Linux/CUDA only.
4. **No GPU?** CPU mode works but is extremely slow (30-60+ min per song).

## Links

- Repo: https://github.com/HeartMuLa/heartlib
- Models: https://huggingface.co/HeartMuLa
- License: Apache-2.0
