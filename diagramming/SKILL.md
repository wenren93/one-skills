---
name: diagramming
description: "Create diagrams: dark-themed SVG architecture diagrams or hand-drawn Excalidraw JSON."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Diagrams, Architecture, SVG, Excalidraw, Flowcharts, Visualization, HTML, JSON]
    related_skills: [design-md, claude-design, sketch]
---

# Diagramming

Two diagram generation approaches for different aesthetics and workflows. Both produce self-contained files that work without external rendering services.

## Decision: Which Approach?

| Feature | Architecture Diagram | Excalidraw |
|---------|---------------------|------------|
| **Output** | Standalone HTML with inline SVG | `.excalidraw` JSON file |
| **Aesthetic** | Dark tech theme (slate-950 grid) | Hand-drawn whiteboard look |
| **Best for** | Cloud infra, system architecture, microservices | Flowcharts, sequence diagrams, concept maps |
| **Viewing** | Open HTML in any browser | Drag onto excalidraw.com |
| **Editing** | Edit HTML source | Edit in Excalidraw web app |
| **Dependencies** | None (self-contained) | None (JSON file) |
| **Upload/share** | Host the HTML file | Upload script creates shareable link |

**Rule of thumb:** Architecture diagram for dark, tech-infrastructure visuals. Excalidraw for everything else.

---

## Architecture Diagram (Dark SVG/HTML)

Generate professional, dark-themed technical architecture diagrams as standalone HTML files with inline SVG graphics. Based on [Cocoon AI's architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator).

### Scope
- Software system architecture (frontend / backend / database layers)
- Cloud infrastructure (VPC, regions, subnets, managed services)
- Microservice / service-mesh topology
- Database + API map, deployment diagrams

### Workflow
1. User describes their system architecture
2. Generate the HTML file following the design system below
3. Save with `write_file` to a `.html` file
4. User opens in any browser — works offline, no dependencies

### Color Palette (Semantic Mapping)

| Component Type | Fill (rgba) | Stroke (Hex) |
| :--- | :--- | :--- |
| **Frontend** | `rgba(8, 51, 68, 0.4)` | `#22d3ee` (cyan-400) |
| **Backend** | `rgba(6, 78, 59, 0.4)` | `#34d399` (emerald-400) |
| **Database** | `rgba(76, 29, 149, 0.4)` | `#a78bfa` (violet-400) |
| **AWS/Cloud** | `rgba(120, 53, 15, 0.3)` | `#fbbf24` (amber-400) |
| **Security** | `rgba(136, 19, 55, 0.4)` | `#fb7185` (rose-400) |
| **Message Bus** | `rgba(251, 146, 60, 0.3)` | `#fb923c` (orange-400) |
| **External** | `rgba(30, 41, 59, 0.5)` | `#94a3b8` (slate-400) |

### Typography & Background
- **Font:** JetBrains Mono (Monospace), loaded from Google Fonts
- **Sizes:** 12px (Names), 9px (Sublabels), 8px (Annotations), 7px (Tiny labels)
- **Background:** Slate-950 (`#020617`) with subtle 40px grid pattern

### Technical Details
- Components are rounded rectangles (`rx="6"`) with 1.5px strokes
- **Double-rect masking**: opaque background rect + semi-transparent styled rect on top
- **Z-Order:** Draw arrows early (after grid) so they render behind component boxes
- **Security Flows:** Dashed lines in rose color (`#fb7185`)
- **Legend Placement:** Must be outside all boundary boxes, 20px below lowest boundary

### Document Structure
1. **Header:** Title with pulsing dot indicator and subtitle
2. **Main SVG:** Diagram in a rounded border card
3. **Summary Cards:** Grid of three cards for high-level details
4. **Footer:** Minimal metadata

### Output Requirements
- Single self-contained `.html` file
- All CSS and SVG inline (except Google Fonts)
- No JavaScript — pure CSS for animations
- Must render correctly in any modern browser

### Template Reference
Load the full HTML template: `skill_view(name="architecture-diagram", file_path="templates/template.html")`

---

## Excalidraw (Hand-Drawn JSON)

Create diagrams by writing standard Excalidraw element JSON and saving as `.excalidraw` files. Drag-and-drop onto [excalidraw.com](https://excalidraw.com) for viewing and editing.

### Workflow
1. Write the elements JSON — an array of Excalidraw element objects
2. Save as `.excalidraw` file using `write_file`
3. Optionally upload for a shareable link using `scripts/upload.py`

### Saving a Diagram

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "hermes-agent",
  "elements": [ ... ],
  "appState": { "viewBackgroundColor": "#ffffff" }
}
```

### Element Format Reference

**Required fields (all):** `type`, `id` (unique string), `x`, `y`, `width`, `height`

**Rectangle:**
```json
{ "type": "rectangle", "id": "r1", "x": 100, "y": 100, "width": 200, "height": 100 }
```
- `roundness: { "type": 3 }` for rounded corners
- `backgroundColor: "#a5d8ff"`, `fillStyle: "solid"` for filled

**Labeled shape (container binding):**

> **WARNING:** Do NOT use `"label": { "text": "..." }` on shapes — NOT valid. Use container binding:

```json
{ "type": "rectangle", "id": "r1", "x": 100, "y": 100, "width": 200, "height": 80,
  "roundness": { "type": 3 }, "backgroundColor": "#a5d8ff", "fillStyle": "solid",
  "boundElements": [{ "id": "t_r1", "type": "text" }] },
{ "type": "text", "id": "t_r1", "x": 105, "y": 110, "width": 190, "height": 25,
  "text": "Hello", "fontSize": 20, "fontFamily": 1, "strokeColor": "#1e1e1e",
  "textAlign": "center", "verticalAlign": "middle",
  "containerId": "r1", "originalText": "Hello", "autoResize": true }
```

**Arrow bindings:**
```json
{ "type": "arrow", "id": "a1", "x": 300, "y": 150, "width": 150, "height": 0,
  "points": [[0,0],[150,0]], "endArrowhead": "arrow",
  "startBinding": { "elementId": "r1", "fixedPoint": [1, 0.5] },
  "endBinding": { "elementId": "r2", "fixedPoint": [0, 0.5] } }
```

### Drawing Order (z-order)
- Array order = z-order (first = back, last = front)
- Emit: background zones → shape → its bound text → its arrows → next shape
- Always place bound text immediately after its container shape

### Color Palette

| Use | Fill Color | Hex |
|-----|-----------|-----|
| Primary / Input | Light Blue | `#a5d8ff` |
| Success / Output | Light Green | `#b2f2bb` |
| Warning / External | Light Orange | `#ffd8a8` |
| Processing / Special | Light Purple | `#d0bfff` |
| Error / Critical | Light Red | `#ffc9c9` |
| Notes / Decisions | Light Yellow | `#fff3bf` |
| Storage / Data | Light Teal | `#c3fae8` |

### Sizing Guidelines
- Minimum `fontSize`: **16** for body, **20** for titles, **14** for annotations (sparingly)
- Minimum shape size: 120x60 for labeled shapes
- Leave 20-30px gaps between elements
- Do NOT use emoji — they don't render in Excalidraw's font

### Uploading for Shareable Link
```bash
python scripts/upload.py ~/diagrams/my_diagram.excalidraw
```
Requires `pip install cryptography`.

### References
- `references/examples.md` — larger diagram examples
- `references/colors.md` — full color tables
- `references/dark-mode.md` — dark mode diagrams
