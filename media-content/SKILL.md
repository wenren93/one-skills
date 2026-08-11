---
name: media-content
description: "Extract and transform content from external media platforms — GIF search (Tenor), YouTube transcripts, and other media sources. Use when the user shares a media URL, asks to search for GIFs, summarize a video, or extract content from a media platform."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [media, gif, youtube, transcript, tenor, content-extraction, video-summary]
---

# Media Content Extraction

Extract and transform content from external media platforms. Covers GIF search, YouTube transcript extraction, and content reformatting.

## When to Use

- User shares a YouTube URL or asks to summarize a video
- User asks to search for or download GIFs
- User wants a transcript, chapters, or thread from a video
- User asks to extract content from any media platform

---

## GIF Search (Tenor API)

Search and download GIFs via the Tenor API using curl. No extra tools needed.

### Setup

Set your Tenor API key in `${HERMES_HOME:-~/.hermes}/.env`:
```bash
TENOR_API_KEY=your_key_here
```
Get a free key at https://developers.google.com/tenor/guides/quickstart.

### Search for GIFs

```bash
# Search and get GIF URLs
curl -s "https://tenor.googleapis.com/v2/search?q=thumbs+up&limit=5&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.gif.url'

# Smaller preview versions
curl -s "https://tenor.googleapis.com/v2/search?q=nice+work&limit=3&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.tinygif.url'
```

### Download a GIF

```bash
URL=$(curl -s "https://tenor.googleapis.com/v2/search?q=celebration&limit=1&key=${TENOR_API_KEY}" | jq -r '.results[0].media_formats.gif.url')
curl -sL "$URL" -o celebration.gif
```

### API Parameters

| Parameter | Description |
|-----------|-------------|
| `q` | Search query (URL-encode spaces as `+`) |
| `limit` | Max results (1-50, default 20) |
| `key` | API key (from `$TENOR_API_KEY` env var) |
| `contentfilter` | Safety: `off`, `low`, `medium`, `high` |

### Media Formats

| Format | Use case |
|--------|----------|
| `gif` | Full quality GIF |
| `tinygif` | Small preview (lighter for chat) |
| `mp4` | Video version (smaller file size) |
| `nanogif` | Tiny thumbnail |

For sending in chat, `tinygif` URLs are lighter weight.

---

## YouTube Transcript Extraction

Extract transcripts from YouTube videos and convert into useful formats.

### Setup

```bash
uv pip install youtube-transcript-api
```

### Helper Script

```bash
# JSON output with metadata
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "https://youtube.com/watch?v=VIDEO_ID"

# Plain text
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --text-only

# With timestamps
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --timestamps

# Specific language with fallback
uv run python3 SKILL_DIR/scripts/fetch_transcript.py "URL" --language tr,en
```

`SKILL_DIR` is the directory containing this SKILL.md file. Accepts any YouTube URL format (standard, shorts, embeds, youtu.be, raw video ID).

### Output Formats

After fetching the transcript, format based on user request:

- **Chapters**: Group by topic shifts with timestamped chapter list
- **Summary**: Concise 5-10 sentence overview
- **Chapter summaries**: Chapters with paragraph summaries
- **Thread**: Twitter/X thread — numbered posts, each under 280 chars
- **Blog post**: Full article with title, sections, takeaways
- **Quotes**: Notable quotes with timestamps

See `references/output-formats.md` for detailed format specifications.

### Workflow

1. **Fetch** transcript with `--text-only --timestamps`
2. **Validate**: confirm non-empty, correct language. Retry without `--language` if empty.
3. **Chunk if needed**: if >50K chars, split into ~40K overlapping chunks, summarize each, merge.
4. **Transform** into requested format (default: summary)
5. **Verify**: check coherence, timestamps, completeness before presenting

### Error Handling

- **Transcript disabled**: tell user; suggest checking subtitles on video page
- **Private/unavailable**: relay error, ask user to verify URL
- **No matching language**: retry without `--language`, note actual language
- **Dependency missing**: `uv pip install youtube-transcript-api` and retry

---

## Pitfalls

1. **Tenor API key required** — GIF search won't work without `TENOR_API_KEY` in `.env`
2. **YouTube transcripts may be auto-generated** — quality varies; note this when presenting
3. **Long videos need chunking** — transcripts over 50K chars must be split before summarizing
4. **URL encoding** — Tenor queries need spaces as `+`, special chars as `%XX`
5. **Rate limits** — Tenor has generous free limits; YouTube transcript API may rate-limit on heavy use
