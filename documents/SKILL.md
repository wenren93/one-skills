---
name: documents
description: "Document processing: PDF extraction/editing, OCR, PowerPoint creation, text extraction."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, Documents, OCR, PowerPoint, PPTX, Text-Extraction, Editing, NLP, Productivity]
    related_skills: [research-paper-writing, arxiv]
---

# Documents

All-in-one document processing: extract text from PDFs/scans, edit PDF content, create and edit PowerPoint presentations, and work with Word documents.

## Decision: Which Tool?

| Task | Tool | Section |
|------|------|---------|
| Extract text from PDF (digital) | pymupdf | [PDF Extraction] |
| Extract text from scanned PDF (OCR) | marker-pdf | [PDF Extraction] |
| Edit PDF text/typos | nano-pdf | [PDF Editing] |
| Create PowerPoint from scratch | pptxgenjs | [PowerPoint] |
| Edit existing PowerPoint | python-pptx | [PowerPoint] |
| Read/analyze PowerPoint | markitdown | [PowerPoint] |
| Extract text from Word doc | python-docx | [Word Documents] |
| Remote PDF URL | web_extract | [PDF Extraction] |

---

## PDF Extraction

### Remote URLs — Always Try First

If the document has a URL, use `web_extract` before any local tool:
```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```
This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

### Local Extractors

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **Text-based PDF** | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ✅ |
| **Code blocks** | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ✅ |
| **Reading order detection** | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

### pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script** (in `scripts/`):
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

### marker-pdf (high-quality OCR)

```bash
pip install marker-pdf
```

**Via helper script** (in `scripts/`):
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

### Split, Merge & Search

```python
import pymupdf

# Split: extract pages 1-5
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")

# Merge multiple PDFs
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")

# Search for text
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
```

---

## PDF Editing

### nano-pdf

Edit PDFs using natural-language instructions:

```bash
uv pip install nano-pdf
```

```bash
nano-pdf edit <file.pdf> <page_number> "<instruction>"
```

Examples:
```bash
nano-pdf edit deck.pdf 1 "Change the title to 'Q3 Results' and fix the typo in the subtitle"
nano-pdf edit report.pdf 3 "Update the date from January to February 2026"
nano-pdf edit contract.pdf 2 "Change the client name from 'Acme Corp' to 'Acme Industries'"
```

**Notes:**
- Page numbers may be 0-based or 1-based depending on version — retry with ±1 if wrong page
- Uses an LLM under the hood — requires an API key
- Works well for text changes; complex layout modifications need different approaches

---

## PowerPoint

### Reading Content

```bash
pip install "markitdown[pptx]"

# Text extraction
python -m markitdown presentation.pptx

# Visual overview
python scripts/thumbnail.py presentation.pptx

# Raw XML
python scripts/office/unpack.py presentation.pptx unpacked/
```

### Editing Existing Presentations

See `references/editing.md` for the full workflow:
1. Analyze template with `thumbnail.py`
2. Unpack → manipulate slides → edit content → clean → pack

### Creating from Scratch

See `references/pptxgenjs.md` for the full workflow using `pptxgenjs` (Node.js):
```bash
npm install -g pptxgenjs
```

### Design Principles

**Don't create boring slides.** Key rules:
- Pick a bold, content-informed color palette (not generic blue)
- Every slide needs a visual element — image, chart, icon, or shape
- Dark backgrounds for title + conclusion, light for content ("sandwich")
- Vary layouts across slides — don't repeat the same card grid
- Left-align body text; center only titles
- Minimum 0.5" margins, 0.3-0.5" between content blocks
- NEVER use accent lines under titles (hallmark of AI-generated slides)

### Color Palettes

| Theme | Primary | Secondary | Accent |
|-------|---------|-----------|--------|
| Midnight Executive | `1E2761` (navy) | `CADCFC` (ice blue) | `FFFFFF` |
| Forest & Moss | `2C5F2D` (forest) | `97BC62` (moss) | `F5F5F5` |
| Coral Energy | `F96167` (coral) | `F9E795` (gold) | `2F3C7E` |
| Warm Terracotta | `B85042` | `E7E8D1` (sand) | `A7BEAE` |
| Charcoal Minimal | `36454F` | `F2F2F2` | `212121` |

### QA (Required)

**Assume there are problems. Your job is to find them.**

1. Content QA: `python -m markitdown output.pptx` — check for missing content, typos
2. Visual QA: Convert to images and inspect with vision tools
3. Fix and re-verify at least once before declaring success

Converting to images:
```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```

---

## Word Documents

For DOCX files, use `python-docx` (parses actual document structure, far better than OCR):

```bash
pip install python-docx
```

```python
from docx import Document
doc = Document('report.docx')
for para in doc.paragraphs:
    print(para.text)
```

For advanced Word operations (creating from scratch with docx-js, XML editing, tracked changes, comments), see `references/office-documents-word.md`.

---

## Excel (.xlsx)

Create, read, and edit Excel spreadsheets — formulas, formatting, charts, data cleaning.

### Quick Reference

| Task | Approach |
|------|----------|
| **Create/edit** with formulas/formatting | `openpyxl` |
| **Bulk data** in/out | `pandas` (`read_excel`, `to_excel`) |
| **Quick look** at a sheet | `markitdown file.xlsx` |

### Prerequisites

```bash
pip install openpyxl pandas "markitdown[xlsx]"
```

### Recalculate (mandatory for formula files)

openpyxl writes formulas as strings with no cached values. Until you recalculate, every formula cell reads back as `None`.

```bash
python scripts/recalc.py output.xlsx [timeout_seconds]
```

### Key Rules

- **Professional font** (Arial, Times New Roman) throughout unless user says otherwise.
- **Zero formula errors.** Never ship while `recalc.py` reports `errors_found`.
- **Use formulas, never hardcoded results.** Write `=SUM(B2:B9)`, not the Python-computed total.
- **Never use XLOOKUP, XMATCH, SORT, FILTER, UNIQUE, or SEQUENCE** — LibreOffice can't evaluate them. Use INDEX/MATCH instead.
- **Financial models:** blue text for hardcoded inputs, black for formulas, green for sheet links, red for external file links, yellow fill for key assumptions.

### openpyxl Gotchas

- **Two loads needed** for reading models: `data_only=True` yields cached values (no formulas), default yields formula strings (no values).
- **`data_only=True` is destructive if you save** — it replaces formulas with literals permanently.
- **Merged cells:** write the top-left anchor only. Every other cell is read-only `MergedCell`.
- **`.xlsm` loses macros** unless you pass `keep_vba=True`.

---

## Full Office Documents Reference

For comprehensive Word document creation (docx-js, XML editing, tracked changes, comments), detailed PDF operations (form filling, watermarks, encryption), and advanced Excel patterns (financial models, formula selection), see the full reference files:

- `references/pdf-forms.md` — PDF form filling workflow
- `references/pdf-reference.md` — Advanced PDF library usage
- `references/office-documents-word.md` — Word document deep dive (from office-documents skill)

---

## Dependencies

- `pip install pymupdf pymupdf4llm` — PDF extraction
- `pip install marker-pdf` — OCR (large, ~3-5GB)
- `uv pip install nano-pdf` — PDF editing
- `pip install "markitdown[pptx]"` — PowerPoint reading
- `npm install -g pptxgenjs` — PowerPoint creation
- `pip install python-docx` — Word document parsing
- LibreOffice (`soffice`) — PDF conversion for visual QA
- Poppler (`pdftoppm`) — PDF to images
