---
name: audio-music
description: "Audio & music: songwriting craft, AI music generation (Suno, HeartMuLa), parody, lyrics, spectrograms, audio analysis."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [songwriting, music, suno, parody, lyrics, audio, spectrogram, analysis, creative]
---

# Audio & Music

Two domains: **creation** (songwriting, lyrics, AI music generation) and **analysis** (spectrograms, audio features). Use the right section for the task.

---

## Songwriting & AI Music Generation

Everything here is a GUIDELINE, not a rule. Art breaks rules on purpose. Use what serves the song.

### Song Structure

Common skeletons — mix, modify, or throw out:

```
ABABCB  Verse/Chorus/Verse/Chorus/Bridge/Chorus    (most pop/rock)
AABA    Verse/Verse/Bridge/Verse                    (jazz standards, ballads)
ABAB    Verse/Chorus alternating                    (simple, direct)
AAA     Verse/Verse/Verse (strophic)                (folk, storytelling)
```

Building blocks: Intro, Verse, Pre-Chorus, Chorus, Bridge, Outro. You don't need all of them.

### Rhyme, Meter, and Sound

**Rhyme types** (tight to loose): Perfect (lean/mean), Family (crate/braid), Assonance (had/glass), Consonance (scene/when), Near/slant. Mix them — all perfect rhymes sound nursery; all slant sounds lazy.

**Internal rhyme**: Rhyming within a line, not just at ends.

**Meter**: Stressed vs unstressed syllables. Say it out loud — if you stumble, the meter needs work.

### Emotional Arc

```
Intro: 2-3  |  Verse: 5-6  |  Pre-Chorus: 7
Chorus: 8-9  |  Bridge: varies  |  Final Chorus: 9-10
```

Most powerful trick: CONTRAST. Whisper before a scream. Sparse before dense. Silence is an instrument.

### Writing Lyrics

**Show, don't tell** (usually): "Your hoodie's still on the hook by the door" beats "I was sad."

**The hook**: The line people remember. Usually the title or core phrase. Place it where it lands hardest.

**Prosody**: Stable feelings pair with settled melodies, perfect rhymes, resolved chords. Unstable feelings pair with wandering melodies, near-rhymes, unresolved chords.

### Parody and Adaptation

1. Map the original's structure (syllables, rhyme scheme, stress patterns)
2. Match stressed syllables to the same beats
3. On long held notes, match the VOWEL SOUND of the original
4. Monosyllabic swaps keep rhythm intact (Crime → Code, Snake → Noose)
5. Keep some original lines intact for recognizability

### Suno AI Prompt Engineering

**Style field formula**: Genre + Mood + Era + Instruments + Vocal Style + Production + Dynamics

```
BAD:  "sad rock song"
GOOD: "Cinematic orchestral spy thriller, 1960s Cold War era, smoky
       sultry female vocalist, big band jazz, brass section with
       trumpets and french horns, sweeping strings, minor key,
       vintage analog warmth"
```

Describe the JOURNEY, not just the genre. V4.5+ supports 1000 chars. NO artist names — describe the sound instead.

**Metatags** (in `[brackets]` inside lyrics):
- Structure: `[Intro]` `[Verse]` `[Chorus]` `[Bridge]` `[Outro]`
- Vocal: `[Whispered]` `[Belted]` `[Falsetto]` `[Raspy]` `[Harmonies]`
- Dynamics: `[High Energy]` `[Building Energy]` `[Emotional Climax]`
- Atmosphere: `[Melancholic]` `[Euphoric]` `[Nostalgic]` `[Dark Atmosphere]`

Keep 5-8 tags per section max. Don't contradict.

### Phonetic Tricks for AI Singers

- Spell words as they SOUND: "through" → "thru"
- Proper nouns: test in a short clip first — pronunciation is baked in once generated
- ALL CAPS = louder. Vowel extension: "lo-o-o-ove" = sustained. Ellipses = dramatic pauses.
- Spell out numbers: "24/7" → "twenty four seven"
- Space acronyms: "AI" → "A I" or "A-I"

### Workflow

1. Write the concept/hook first
2. If adapting, map the original structure
3. Generate raw material — brainstorm freely before structuring
4. Draft lyrics into the structure
5. Read/sing aloud — catch stumbles, fix meter
6. Build the Suno style description — paint the dynamic arc
7. Add metatags for performance direction
8. Generate 3-5 variations minimum — treat as recording takes
9. Pick the best, use Extend/Continue for promising sections

Expect ~3-5 generations per 1 good result.

### Lessons Learned

- Describing the dynamic ARC in the style field matters more than listing genres
- Keeping some original lines in parody adds recognizability
- The bridge is where you transform imagery — swap references for your theme's metaphors
- A strong vocal persona description beats any single metatag
- Don't be precious about rules. If a line breaks meter but hits harder, keep it.

### HeartMuLa (Open-Source Suno Alternative)

Local song generation from lyrics + tags. Apache-2.0, requires 8GB+ VRAM. See `references/heartmula.md`.

**When to choose**: offline/private, no subscription, reproducible, custom fine-tuning.
**When to choose Suno**: zero setup, faster iteration, better vocal quality.

---

## Audio Analysis (songsee)

Generate spectrograms and multi-panel audio feature visualizations from audio files.

### Setup

```bash
go install github.com/steipete/songsee/cmd/songsee@latest
```

### Quick Start

```bash
songsee track.mp3                              # Basic spectrogram
songsee track.mp3 -o spectrogram.png           # Save to file
songsee track.mp3 --viz spectrogram,mel,chroma,hpss,selfsim,loudness,tempogram,mfcc,flux  # Multi-panel grid
songsee track.mp3 --start 12.5 --duration 8    # Time slice
cat track.mp3 | songsee - --format png -o out.png  # From stdin
```

### Visualization Types

| Type | Description |
|------|-------------|
| `spectrogram` | Standard frequency spectrogram |
| `mel` | Mel-scaled spectrogram |
| `chroma` | Pitch class distribution |
| `hpss` | Harmonic/percussive separation |
| `selfsim` | Self-similarity matrix |
| `loudness` | Loudness over time |
| `tempogram` | Tempo estimation |
| `mfcc` | Mel-frequency cepstral coefficients |
| `flux` | Spectral flux (onset detection) |

### Common Flags

| Flag | Description |
|------|-------------|
| `--viz` | Visualization types (comma-separated) |
| `--style` | Color palette: `classic`, `magma`, `inferno`, `viridis`, `gray` |
| `--width` / `--height` | Output dimensions |
| `--window` / `--hop` | FFT window and hop size |
| `--min-freq` / `--max-freq` | Frequency range filter |
| `--start` / `--duration` | Time slice |
| `-o` | Output file path |

### Notes

- WAV and MP3 native; other formats require `ffmpeg`
- Output images can be inspected with `vision_analyze` for automated analysis
- Useful for comparing audio outputs, debugging synthesis, documenting pipelines

---

## Pitfalls

- Don't treat songwriting guidelines as rules — craft serves art
- Don't use artist names in Suno prompts — describe the sound
- Don't generate more than 8 metatags per section — confuses the AI
- Don't skip the "sing aloud" step — meter problems invisible on paper
- Don't expect perfect pronunciation on first try — test proper nouns in short clips
- Always check `--viz` types are comma-separated (no spaces) for songsee
