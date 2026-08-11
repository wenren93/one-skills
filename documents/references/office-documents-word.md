# Word Documents - Advanced Operations

From the `office-documents` skill. For basic reading, see the main documents skill.

## Creating with docx-js

npm package `docx` for creating .docx from scratch:

```bash
npm install docx
```

### Key Gotchas
- Page size defaults to A4. US Letter: `page: { size: { width: 12240, height: 15840 } }` (DXA; 1440 = 1")
- Landscape: pass portrait dimensions + `orientation: PageOrientation.LANDSCAPE`
- Tables need dual widths: `columnWidths` on table AND `width` on every cell (both DXA)
- Table shading: use `ShadingType.CLEAR`, never `SOLID` (renders black)
- Lists: use `numbering` config with `LevelFormat.BULLET`, never literal `•`
- `ImageRun` requires `type:` (`"png"`, `"jpg"`, …)
- `PageBreak` must be inside a `Paragraph`
- Never use `\n` — use separate `Paragraph` elements
- TOC: headings must use built-in `HeadingLevel.*`; custom styles need `outlineLevel`

## Editing Existing Documents

Legacy `.doc` files must be converted first: `python scripts/office/soffice.py --headless --convert-to docx file.doc`

```bash
unzip -q doc.docx -d unpacked/
find unpacked -type l -delete   # strip symlink entries
python scripts/merge_runs.py unpacked/   # coalesce fragmented runs
# edit unpacked/word/document.xml in place — do NOT reformat
(cd unpacked && rm -f ../out.docx && zip -Xr ../out.docx .)
python scripts/office/validate.py out.docx --original doc.docx
```

Word splits text across many `<w:r>` runs, so a phrase may not exist as a contiguous string in XML. `merge_runs.py` merges adjacent identically-formatted runs.

## Tracked Changes

Validate with `--author "<name>"` — reports text changed without `<w:ins>`/`<w:del>`. Wrap runs in `<w:ins>`/`<w:del>` with `w:id`, `w:author`, `w:date` attributes. Inside `<w:del>`, text element is `<w:delText>`, not `<w:t>`.

To produce clean copy with all changes accepted: `python scripts/accept_changes.py in.docx out.docx`

## Comments

```bash
python scripts/comment.py unpacked/ "Fees & expenses cap is too low"
python scripts/comment.py unpacked/ "Agreed" --parent 0
```

## Pitfalls
- Don't round-trip OOXML through `xml.etree.ElementTree` — it rewrites namespace prefixes and corrupts the file. Use `defusedxml.minidom`.
- Zip from INSIDE the unpacked directory and `rm` the target first, or deleted parts survive in the archive.
