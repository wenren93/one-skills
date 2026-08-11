---
name: ascii
description: "ASCII art and video: banners, cowsay, image-to-ascii, video-to-ASCII pipelines, audio-reactive visualizers."
version: 1.0.0
author: 0xbyt4, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ASCII, Art, Video, Banners, Creative, Unicode, Text-Art, Animation, Visualizer]
    related_skills: [excalidraw]
---

# ASCII Art & Video

Everything ASCII — from static text banners to production video pipelines. Two modes, one medium.

## When to use

- **Static art** (banners, cowsay, image-to-ASCII, QR codes, pre-made art) → § Static ASCII Art
- **Video/animation** (ASCII video, audio visualizers, generative animation) → § ASCII Video Production

---

## Static ASCII Art

Multiple tools for different ASCII art needs. All tools are local CLI programs or free REST APIs — no API keys required.

### Tool 1: Text Banners (pyfiglet — local)

Render text as large ASCII art banners. 571 built-in fonts.

```bash
pip install pyfiglet --break-system-packages -q
python3 -m pyfiglet "YOUR TEXT" -f slant
python3 -m pyfiglet "TEXT" -f doom -w 80
python3 -m pyfiglet --list_fonts
```

**Recommended fonts:**

| Style | Font | Best for |
|-------|------|----------|
| Clean & modern | `slant` | Project names, headers |
| Bold & blocky | `doom` | Titles, logos |
| Big & readable | `big` | Banners |
| Classic banner | `banner3` | Wide displays |
| Compact | `small` | Subtitles |
| Cyberpunk | `cyberlarge` | Tech themes |
| 3D effect | `3-d` | Splash screens |
| Gothic | `gothic` | Dramatic text |

### Tool 2: Text Banners (asciified API — remote, no install)

Free REST API, 250+ FIGlet fonts, returns plain text directly.

```bash
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello+World"
curl -s "https://asciified.thelicato.io/api/v2/ascii?text=Hello&font=Slant"
curl -s "https://asciified.thelicato.io/api/v2/fonts"
```

### Tool 3: Cowsay (Message Art)

```bash
cowsay "Hello World"
cowsay -f tux "Linux rules"
cowsay -f dragon "Rawr!"
cowthink "Hmm..."
cowsay -l    # List all characters
```

Eye/tongue modifiers: `-b` Borg, `-d` Dead, `-g` Greedy, `-p` Paranoid, `-s` Stoned, `-w` Wired.

### Tool 4: Boxes (Decorative Borders)

70+ built-in designs. Combine with pyfiglet:

```bash
echo "Hello World" | boxes -d stone
echo "Hello World" | boxes -d parchment
python3 -m pyfiglet "HERMES" -f slant | boxes -d stone
```

### Tool 5: TOIlet (Colored Text Art)

Like pyfiglet but with ANSI color effects:

```bash
toilet "Hello World"
toilet --gay "Rainbow!"
toilet --metal "Metal!"
toilet -F border "Bordered"
```

### Tool 6: Image to ASCII Art

**Option A: ascii-image-converter (recommended):**
```bash
sudo snap install ascii-image-converter
ascii-image-converter image.png -C               # Color output
ascii-image-converter image.png -d 60,30          # Dimensions
ascii-image-converter image.png -b                # Braille
```

**Option B: jp2a (lightweight, JPEG only):**
```bash
sudo apt install jp2a -y
jp2a --width=80 --colors image.jpg
```

### Tool 7: Search Pre-Made ASCII Art

Source: `https://ascii.co.uk/art/{subject}` — fetch with curl, extract from `<pre>` tags.

Subjects: Animals (cat, dog, dragon, penguin…), Objects (rocket, guitar, computer…), Nature (tree, flower, moon…), Characters (skull, robot, alien…), Holidays (christmas, halloween…).

### Tool 8: Fun ASCII Utilities

```bash
curl -s "qrenco.de/Hello+World"        # QR code as ASCII
curl -s "wttr.in/London"               # Weather with ASCII graphics
curl -s "wttr.in/Moon"                 # Moon phase
curl -s https://api.github.com/octocat # Random Octocat
```

### Decision Flow

1. **Text banner** → pyfiglet or asciified API
2. **Fun character message** → cowsay
3. **Decorative border** → boxes (combine with pyfiglet)
4. **Art of a specific thing** → ascii.co.uk via curl
5. **Convert image** → ascii-image-converter or jp2a
6. **QR code** → qrenco.de
7. **Weather art** → wttr.in
8. **Custom/creative** → LLM generation with Unicode palette

### LLM-Generated Custom Art (Fallback)

Box drawing: `╔ ╗ ╚ ╝ ║ ═ ╠ ╣ ╦ ╩ ╬ ┌ ┐ └ ┘ │ ─ ├ ┤ ┬ ┴ ┼`
Block elements: `░ ▒ ▓ █ ▄ ▀ ▌ ▐`
Geometric: `◆ ◇ ● ○ ■ □ ▲ △ ★ ☆ ✦`

Max 60 chars/line, max 15 lines for banners, 25 for scenes. Monospace only.

---

## ASCII Video Production Pipeline

Production pipeline for ASCII art video — any format. Converts video/audio/images/generative input into colored ASCII character video output (MP4, GIF, image sequence).

### Modes

| Mode | Input | Output | Reference |
|------|-------|--------|-----------|
| **Video-to-ASCII** | Video file | ASCII recreation of source footage | `references/inputs.md` § Video Sampling |
| **Audio-reactive** | Audio file | Generative visuals driven by audio features | `references/inputs.md` § Audio Analysis |
| **Generative** | None (or seed params) | Procedural ASCII animation | `references/effects.md` |
| **Hybrid** | Video + audio | ASCII video with audio-reactive overlays | Both input refs |
| **Lyrics/text** | Audio + text/SRT | Timed text with visual effects | `references/inputs.md` § Text/Lyrics |
| **TTS narration** | Text quotes + TTS API | Narrated testimonial/quote video | `references/inputs.md` § TTS Integration |

### Stack

Single self-contained Python script per project. No GPU required.

| Layer | Tool | Purpose |
|-------|------|---------|
| Core | Python 3.10+, NumPy | Math, array ops, vectorized effects |
| Signal | SciPy | FFT, peak detection (audio modes) |
| Imaging | Pillow (PIL) | Font rasterization, frame decoding |
| Video I/O | ffmpeg (CLI) | Decode input, encode output, mux audio |
| Parallel | concurrent.futures | N workers for batch rendering |

### Pipeline Architecture

Every mode follows the same 6-stage pipeline:

```
INPUT → ANALYZE → SCENE_FN → TONEMAP → SHADE → ENCODE
```

1. **INPUT** — Load/decode source material
2. **ANALYZE** — Extract per-frame features (audio bands, video luminance/edges)
3. **SCENE_FN** — Scene function renders to pixel canvas (`uint8 H,W,3`). See `references/composition.md`
4. **TONEMAP** — Percentile-based adaptive brightness normalization
5. **SHADE** — Post-processing via `ShaderChain` + `FeedbackBuffer`. See `references/shaders.md`
6. **ENCODE** — Pipe raw RGB frames to ffmpeg for H.264/GIF encoding

### Creative Direction

**Aesthetic Dimensions:**

| Dimension | Options | Reference |
|-----------|---------|-----------|
| Character palette | Density ramps, block elements, symbols, scripts | `references/architecture.md` § Palettes |
| Color strategy | HSV, OKLAB/OKLCH, discrete RGB palettes | `references/architecture.md` § Color System |
| Background texture | Sine fields, fBM noise, voronoi, reaction-diffusion | `references/effects.md` |
| Primary effects | Rings, spirals, tunnel, vortex, waves, aurora | `references/effects.md` |
| Particles | Sparks, snow, rain, bubbles, runes, boids | `references/effects.md` § Particles |
| Shader mood | Retro CRT, clean modern, glitch art, cinematic | `references/shaders.md` |
| Grid density | xs(8px) through xxl(40px), mixed per layer | `references/architecture.md` § Grid System |

**Per-Section Variation** — Never use the same config for the entire video. For each section/scene:
- Different background effect (or compose 2-3)
- Different character palette (match the mood)
- Different color strategy (or at minimum a different hue)
- Vary shader intensity

**Project-Specific Invention** — For every project, invent at least one custom element (palette, effect, color, particle set, or transition).

### Creative Standard

This is visual art. ASCII characters are the medium; cinema is the standard.

Before writing code, articulate the creative concept: mood, visual story, color world, character texture, what makes THIS different. First-render excellence is non-negotiable.

### Critical Implementation Notes

**Brightness** — Use `tonemap()`, not linear multipliers. Never `canvas * N` — they clip highlights. Pipeline: `scene_fn() → tonemap() → FeedbackBuffer → ShaderChain → ffmpeg`.

**Font Cell Height** — macOS Pillow: `textbbox()` returns wrong height. Use `font.getmetrics()`.

**ffmpeg Pipe Deadlock** — Never `stderr=subprocess.PIPE` with long-running ffmpeg. Redirect to file.

**Font Compatibility** — Validate palettes at init — render each char, check for blank output.

### References

| File | Contents |
|------|----------|
| `references/architecture.md` | Grid system, resolution presets, font selection, character palettes, color system |
| `references/composition.md` | Pixel blend modes, multi-grid composition, adaptive tonemap, FeedbackBuffer, masking |
| `references/effects.md` | Effect building blocks: noise/fBM, voronoi, reaction-diffusion, particles, transforms |
| `references/shaders.md` | ShaderChain, 38 shader catalog, audio-reactive scaling, transitions |
| `references/scenes.md` | Scene protocol, Renderer class, SCENES table, beat-synced cutting, parallel rendering |
| `references/inputs.md` | Audio analysis (FFT, bands, beats), video sampling, text/lyrics, TTS integration |
| `references/optimization.md` | Hardware detection, quality profiles, vectorized patterns, parallel rendering |
| `references/troubleshooting.md` | NumPy traps, blend pitfalls, multiprocessing, brightness diagnostics, ffmpeg issues |

### Creative Divergence (experimental output)

For creative/experimental/surprising output:

- **Forced Connections** — cross-domain inspiration (weather systems → erosion effects, microbiology → mitosis patterns)
- **Conceptual Blending** — combine two spaces (ocean + sheet music → crests = high notes)
- **Oblique Strategies** — draw a lateral-thinking card and interpret it against the challenge
