---
name: office-documents
description: "Create, read, and edit Word (.docx), PDF, and Excel (.xlsx) documents. Covers document creation, editing, format conversion, form filling, formula recalculation, and verification."
version: 1.0.0
author: Nous Research
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Word, DOCX, PDF, Excel, XLSX, Documents, Office, Productivity, Forms, Spreadsheets]
    category: productivity
    related_skills: [documents, powerpoint]
---

# Office Documents

Create, read, and edit Word documents (.docx), PDF files, and Excel spreadsheets (.xlsx). Each format has its own tools, gotchas, and verification steps — this skill covers all three with deep detail.

## Decision: Which Format?

| User wants... | Format | Section |
|---------------|--------|---------|
| Report, memo, letter, template | Word (.docx) | [Word Documents] |
| Combine, split, fill forms, watermark | PDF | [PDF] |
| Spreadsheet, formulas, charts, data | Excel (.xlsx) | [Excel] |
| Extract text from scanned document | PDF + OCR | [PDF → OCR] |
| Presentation / deck | PowerPoint | Use `documents` skill |

---

## Word Documents (.docx)

Create, read, and edit Word documents — reports, memos, letters, letterheads, tables of contents, tracked changes (redlining), and comments. A `.docx` is a ZIP archive of XML files; this skill covers both the high-level creation path and surgical XML editing.

### When to Use

Any mention of "Word doc", ".docx", ".dotx", or requests for a "report", "memo", "letter" as a Word file; extracting or reorganizing content; find-and-replace; inserting images; tracked changes or comments.

### Prerequisites

```bash
npm ls docx --depth=0 2>/dev/null | grep -q docx || npm install docx   # creation (docx-js)
pip show pandoc >/dev/null 2>&1 || true; which pandoc || sudo apt install -y pandoc   # reading
which soffice || sudo apt install -y libreoffice     # rendering/verification
which pdftoppm || sudo apt install -y poppler-utils  # PDF → images
pip install defusedxml lxml   # validation scripts
```

macOS: `brew install pandoc libreoffice poppler`.

### Quick Reference

| Task | Approach |
|---|---|
| **Create** a new document | Write a `docx` (npm) script — see gotchas below |
| **Edit** an existing document | `unzip` → edit `word/document.xml` → `zip` (docx-js cannot open existing files) |
| **Read** content | `pandoc -t markdown file.docx` (or `read_file`, which auto-extracts .docx text) |

### Creating with docx-js — gotchas

- **Page size defaults to A4.** For US Letter set `page: { size: { width: 12240, height: 15840 } }` (DXA; 1440 = 1″).
- **Landscape:** pass portrait dimensions and `orientation: PageOrientation.LANDSCAPE` — docx-js swaps width/height internally.
- **Tables need dual widths:** set `columnWidths` on the table AND `width` on every cell, both in `WidthType.DXA` (PERCENTAGE breaks in Google Docs). Column widths must sum to the table width.
- **Table shading:** use `ShadingType.CLEAR`, never `SOLID` (renders black).
- **Lists:** never insert `•` literally; use a `numbering` config with `LevelFormat.BULLET`.
- **`ImageRun` requires `type:`** (`"png"`, `"jpg"`, …).
- **`PageBreak` must be inside a `Paragraph`.**
- **Never use `\n`** — use separate `Paragraph` elements.
- **TOC:** headings must use built-in `HeadingLevel.*`; custom heading styles need `outlineLevel` set or they won't appear.
- **Don't use a table as a horizontal rule** — use a paragraph bottom border instead.
- **Dot-leader / right-aligned-on-same-line:** use `PositionalTab` (`alignment: PositionalTabAlignment.RIGHT`, `leader: PositionalTabLeader.DOT`) inside a `TextRun`, not literal `.` or space padding.

### Verify the output

```bash
python scripts/office/soffice.py --headless --convert-to pdf output.docx
pdftoppm -jpeg -r 100 output.pdf page
ls page-*.jpg   # then inspect each with vision_analyze
```

### Editing existing documents

Legacy `.doc` files must be converted first: `python scripts/office/soffice.py --headless --convert-to docx file.doc`.

```bash
unzip -q doc.docx -d unpacked/
find unpacked -type l -delete   # strip symlink entries — docx from external parties is untrusted
python scripts/merge_runs.py unpacked/   # coalesce fragmented runs so text is findable
# edit unpacked/word/document.xml in place — do NOT reformat or pretty-print
(cd unpacked && rm -f ../out.docx && zip -Xr ../out.docx .)
python scripts/office/validate.py out.docx --original doc.docx   # XSD checks; --auto-repair fixes common issues
```

Word splits text across many `<w:r>` runs (revision ids, spell-check markers), so a phrase you can see in the document often doesn't exist as a contiguous string in the XML. `merge_runs.py` merges adjacent identically-formatted runs without changing content or rendering.

**Tracked changes:** when redlining, validate with `--author "<the name you redlined under>"` — it reports any text you changed without a `<w:ins>`/`<w:del>` around it. Wrap runs in `<w:ins>`/`<w:del>` with `w:id`, `w:author`, `w:date` attributes. Inside `<w:del>`, the text element is `<w:delText>`, not `<w:t>`.

To produce a clean copy with all tracked changes accepted: `python scripts/accept_changes.py in.docx out.docx`.

### Comments

Comments require six cross-linked files. Use the helper:

```bash
# Against an already-unpacked directory (preferred when also placing markers)
python scripts/comment.py unpacked/ "Fees & expenses cap is too low"
python scripts/comment.py unpacked/ "Agreed" --parent 0

# Against a .docx directly
python scripts/comment.py contract.docx "This cap is too low" -o annotated.docx
```

### Word Pitfalls

- Don't round-trip OOXML through `xml.etree.ElementTree` — it rewrites namespace prefixes and corrupts the file. Use `defusedxml.minidom` for scripted transforms.
- Zip from INSIDE the unpacked directory (`cd unpacked && zip -Xr ../out.docx .`) and `rm` the target first, or deleted parts survive in the archive.

---

## PDF

Create, combine, split, transform, and secure PDF files — merging, page manipulation, form filling, watermarks, encryption, and text/table extraction.

### When to Use

Anything with PDF files: reading/extracting text/tables, combining/merging, splitting, rotating pages, adding watermarks, creating new PDFs, filling forms, encrypting/decrypting, extracting images, or OCR on scanned PDFs.

### Prerequisites

```bash
pip install pypdf pdfplumber reportlab
which pdftotext || sudo apt install -y poppler-utils   # pdftotext, pdftoppm, pdfimages
which qpdf || sudo apt install -y qpdf                 # CLI merge/split/decrypt
```

macOS: `brew install poppler qpdf`. OCR extras: `pip install pytesseract pdf2image` + `sudo apt install -y tesseract-ocr`.

### Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Merge PDFs | pypdf | `writer.add_page(page)` per page |
| Split PDFs | pypdf | One page per file |
| Extract text | pdfplumber | `page.extract_text()` |
| Extract tables | pdfplumber | `page.extract_tables()` |
| Create PDFs | reportlab | Canvas or Platypus |
| Command-line merge/split | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs | pytesseract | Convert to images first |
| Fill PDF forms | see `references/pdf-forms.md` | `scripts/fill_fillable_fields.py` etc. |
| Edit existing text | `nano-pdf` skill | `nano-pdf edit file.pdf <page> "<instruction>"` |

### Merge / split / rotate (pypdf)

```python
from pypdf import PdfReader, PdfWriter

# Merge
writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf"]:
    for page in PdfReader(pdf_file).pages:
        writer.add_page(page)
with open("merged.pdf", "wb") as f:
    writer.write(f)

# Split: one file per page
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    w = PdfWriter(); w.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as f:
        w.write(f)

# Rotate
page = reader.pages[0]
page.rotate(90)  # clockwise
```

### Extract text and tables (pdfplumber)

```python
import pdfplumber, pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    tables = [pd.DataFrame(t[1:], columns=t[0])
              for page in pdf.pages
              for t in page.extract_tables() if t]
```

### Create PDFs (reportlab)

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = [Paragraph("Report Title", styles["Title"]), Spacer(1, 12),
         Paragraph("Body text...", styles["Normal"]), PageBreak(),
         Paragraph("Page 2", styles["Heading1"])]
doc.build(story)
```

**Subscripts/superscripts:** never use Unicode sub/superscript characters (₀₁₂, ⁰¹²) — the built-in fonts lack the glyphs and render solid black boxes. Use `<sub>`/`<super>` markup inside `Paragraph` objects.

### Command-line tools

```bash
pdftotext -layout input.pdf output.txt                     # text, layout preserved
pdftotext -f 1 -l 5 input.pdf output.txt                   # pages 1-5
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf     # merge
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf               # split range
qpdf input.pdf output.pdf --rotate=+90:1                   # rotate page 1
qpdf --password=pw --decrypt encrypted.pdf decrypted.pdf   # remove password
pdfimages -j input.pdf img                                 # extract images
```

### Watermark

```python
from pypdf import PdfReader, PdfWriter

watermark = PdfReader("watermark.pdf").pages[0]
reader, writer = PdfReader("document.pdf"), PdfWriter()
for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)
with open("watermarked.pdf", "wb") as f:
    writer.write(f)
```

### OCR scanned PDFs

```python
import pytesseract
from pdf2image import convert_from_path

pages = convert_from_path("scanned.pdf")
text = "\n\n".join(pytesseract.image_to_string(img) for img in pages)
```

### Form filling

Read `references/pdf-forms.md` first — it distinguishes fillable (AcroForm) PDFs from flat scanned forms and walks through the helper scripts:

- `scripts/check_fillable_fields.py` — does the PDF have AcroForm fields?
- `scripts/extract_form_field_info.py` / `scripts/extract_form_structure.py` — enumerate fields
- `scripts/fill_fillable_fields.py` — fill AcroForm fields
- `scripts/fill_pdf_form_with_annotations.py` — overlay text on flat forms
- `scripts/check_bounding_boxes.py`, `scripts/create_validation_image.py` — verify placement visually

Advanced library usage (pypdfium2, pdf-lib) and troubleshooting: `references/pdf-reference.md`.

### PDF Pitfalls

- `page.extract_text()` returns `None` on image-only pages — guard with `or ""` and fall back to OCR.
- pypdf preserves encryption flags: reading an encrypted PDF requires `PdfReader(path, password=...)` before pages are accessible.
- reportlab coordinates are bottom-left origin, points (1/72″) — not top-left.
- When filling flat forms by annotation overlay, always render a validation image and check the placement before delivering.

---

## Excel (.xlsx)

Create, read, and edit Excel workbooks — formulas, formatting, charts, data cleaning, and format conversion. Every formula-bearing output must be recalculated and error-free before delivery.

### When to Use

Any time a spreadsheet file is the primary input or output: opening, reading, editing, or fixing an existing .xlsx, .xlsm, .xltx, .csv, or .tsv file; creating a new spreadsheet from scratch; converting between tabular formats; cleaning messy tabular data.

### Prerequisites

```bash
pip install openpyxl pandas "markitdown[xlsx]"
which soffice || sudo apt install -y libreoffice   # formula recalculation (scripts/recalc.py)
```

macOS: `brew install libreoffice`.

### Quick Reference

| Task | Approach |
|---|---|
| **Create** or **edit** with formulas/formatting | `openpyxl` — see gotchas below |
| **Bulk data** in or out | `pandas` (`read_excel`, `to_excel`) |
| **Quick look** at a sheet | `markitdown file.xlsx` — `## SheetName` per sheet; reads `.xlsm` too |
| **Read** a model (formulas *and* values) | two `load_workbook` passes — see gotchas |

### Requirements for every output

- **Professional font** (Arial, Times New Roman) throughout, unless the user says otherwise.
- **Zero formula errors.** Never ship while `recalc.py` reports `errors_found`. If you think an error predates you, prove it: load the *original* with `data_only=True` and look at that cell.
- **Use formulas, never hardcoded results.** Write `sheet['B10'] = '=SUM(B2:B9)'`, not the Python-computed total.
- **Follow the user's spec literally.** Exact tab names, exact column headers, and the formula they spelled out.
- **Document every assumption and hardcoded number** where the reader will see it — a cell comment, or an adjacent cell at a table's end.
- **A workbook *you create* for someone to fill in** needs a short legend naming which cells to edit, and one example row of realistic values.
- **Editing an existing file: match its conventions exactly.** Find its designated input cells first — a distinct font color, fill, or shading marks them — write only there, and leave every existing formula untouched.

### Recalculate (mandatory whenever the file contains formulas)

openpyxl writes formulas as strings with **no cached values**. Until you recalculate, every formula cell reads back as `None`.

```bash
python scripts/recalc.py output.xlsx [timeout_seconds]   # default 30
```

LibreOffice computes every formula, the file is **rewritten in place**, and you get JSON: `status` (`success` | `errors_found`), `total_formulas`, `total_errors`, and an `error_summary` naming up to 100 cells per error type.

**A green recalc proves your formulas *evaluate*, not that they are *right*.** An off-by-one range or a reference to the wrong row yields a clean, error-free file with wrong numbers.

### Choosing formulas that survive verification

- **Prefer Excel-2007-era functions** — `SUMIFS`, `INDEX`, `MATCH`, `IFERROR`, `SUMPRODUCT` — which need no prefix.
- **Six post-2007 functions work, but only with an `_xlfn.` prefix**: `_xlfn.TEXTJOIN`, `_xlfn.CONCAT`, `_xlfn.IFS`, `_xlfn.SWITCH`, `_xlfn.MAXIFS`, `_xlfn.MINIFS`. Written bare, each yields `#NAME?`.
- **Never use `XLOOKUP`, `XMATCH`, `SORT`, `FILTER`, `UNIQUE`, or `SEQUENCE`.** LibreOffice cannot reliably evaluate them. Use `INDEX`/`MATCH` for lookups, and sort, filter, and de-duplicate in Python before writing the cells.
- A formula LibreOffice could not parse is written back **lowercased** — a quick tell beside a `#NAME?`.

### openpyxl gotchas

- **Reading a model takes two loads.** `data_only=True` yields cached values with the formulas gone; the default yields formula strings with no values.
- **`data_only=True` is destructive if you save.** That workbook has no formulas left, so saving replaces every one with a literal — permanently.
- **`data_only=True` on a file openpyxl just wrote returns `None` everywhere** — run `recalc.py` first.
- **Merged cells: write the top-left anchor only.** Every other cell in the range is a `MergedCell` whose `.value` is read-only.
- **`.xlsm` loses its macros unless you pass `keep_vba=True`** to `load_workbook`.
- **A sheet name containing a space must be quoted** in a cross-sheet reference: `='Assumptions Inputs'!$B$5`.

### Financial models

Unless the user says otherwise, or the existing file already does something else.

**Color:** blue text (`0,0,255`) for hardcoded inputs · black for formulas · green (`0,128,0`) for links to another sheet · red (`255,0,0`) for links to another file · yellow fill (`255,255,0`) for key assumptions.

**Numbers:** currency `$#,##0` · zeros render as `-` · negatives in parentheses · percentages `0.0%`, **stored as fractions** · valuation multiples `0.0x` · years as text (`"2024"`, never `2,024`).

**Structure:** every assumption in its own labeled cell, referenced by the formulas that use it · formulas consistent across every projection period · guard denominators that can be zero.

---

## Verification (all formats)

1. **Word:** `python scripts/office/validate.py out.docx --original in.docx` — schema, relationship, and content-type checks. Render to PDF → images and inspect each page with `vision_analyze`.
2. **PDF:** Open with `PdfReader` and assert expected page count. Re-extract text and confirm content is present. For visual output: `pdftoppm -jpeg -r 100 output.pdf page` and inspect with `vision_analyze`.
3. **Excel:** `python scripts/recalc.py output.xlsx` → `status: success`, `total_errors: 0`. Spot-check 2–3 computed cells. `markitdown output.xlsx` — scan for missing sheets, misplaced headers.

## Related skills

`documents` (quick-reference for PDF extraction, OCR, PowerPoint), `powerpoint` (decks).
