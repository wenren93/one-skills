---
name: web-design
description: "Web design: process, taste, quick mockups, and 54 real design systems as HTML/CSS."
version: 1.0.0
author: BadTechBandit, Hermes Agent, Teknium
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, html, prototype, ux, ui, creative, mockup, design-systems, templates, variants]
    related_skills: [design-md, diagramming, excalidraw]
---

# Web Design

Three complementary capabilities for designing web artifacts:

| Section | What it gives you | Use when... |
|---------|-------------------|-------------|
| **§ Design Process** | Design taste, anti-slop rules, surface-first composition, verification | From-scratch artifact with no specific brand dictated |
| **§ Quick Mockups** | 2-3 throwaway variants for comparing visual directions | User wants to see options before committing |
| **§ Design System Library** | 54 real-world design systems (Stripe, Linear, Vercel, etc.) as templates | User wants a known brand's look |

These compose: use the Design System Library for visual vocabulary, Design Process for how to turn a brief into a thoughtful artifact, and Quick Mockups when the user wants to compare directions.

---

## Design Process

### When to use

Landing pages, prototypes, decks, component explorations, motion studies, dashboards, redesigns from screenshots/repos/brand docs.

### Surface-First: Commit to a Composition Before Touching Tokens

The single highest-leverage anti-slop rule. Before writing any colors or type, commit to exactly one surface archetype:

1. **Monitor** — watching state change (dashboards, status pages). Density, glanceable hierarchy.
2. **Operate** — taking action on things (consoles, admin panels, inboxes). Action affordances dominate.
3. **Compare** — weighing options (pricing, plans, spec tables). Aligned columns, one differentiator.
4. **Configure** — setting things up (settings, forms, wizards). Progressive disclosure.
5. **Decide / Learn** — being convinced or taught (landing pages, docs). One idea per section; hero is correct here.
6. **Explore** — browsing an open space (galleries, catalogs). Filters and result grids.
7. **Command / Inspect** — keyboard-driven or single-object drill-down (command bars, inspectors).

A dashboard is a Monitor surface, not Decide — no centered hero with three feature cards.

### Workflow

1. **Understand the brief** — what, who, artifact, constraints
2. **Gather context** — brand docs, screenshots, repo files, design tokens, UI kits
3. **Commit to a surface** — name the archetype before any visual tokens
4. **Define the design system** — colors, type, spacing, radii, shadows, motion, components
5. **Choose format** — static comparison, clickable prototype, HTML deck, component lab, motion study
6. **Build the artifact** — single self-contained HTML file preferred
7. **Verify** — file exists, syntax checks, browser console, visual inspection
8. **Report** — path, contents, caveats, next action

### Anti-Slop Rules

- No aggressive gradient backgrounds or glassmorphism by default
- No emoji unless the brand uses them
- No generic SaaS cards with icons everywhere
- No left-border accent callout cards
- No fake dashboards filled with arbitrary numbers
- No stock-photo hero sections
- No rainbow palettes
- No vague labels ("Insights," "Growth," "Scale") without content

### Slop Diagnostic (score before you fix)

Score 0-10 on these tells, then repair only what fired:

1. **Tech gradient** — blue/violet/indigo glossy on everything
2. **Generic tech hue** — default indigo/violet accent
3. **Feature-tile grid** — icon + heading + sentence × 3, equal weight
4. **Accent rail** — colored left strip on cards
5. **Unearned blur** — glassmorphism with no depth system
6. **Monument stat** — oversized numbers filling space
7. **Icon topper** — rounded-square icon above every heading
8. **Center stack** — everything centered, no composition
9. **Default type** — Inter used by default rather than chosen
10. **Wrong surface** — composition doesn't match surface

Tells 3, 8, 10 → re-layout. Tells 1, 2, 9 → recolor/re-typeset. Tells 4, 5, 6, 7 → remove decoration.

### Typography

Choose type deliberately: editorial (serif headlines), software/product (precise sans), luxury (fewer weights, more spacing), technical (mono accents). Avoid overused defaults when stronger choices exist. Use type as hierarchy before adding boxes, icons, or color.

### Color

Use brand colors first. If none, define a small system: neutrals, surface, ink, muted text, border, accent. Prefer oklch for invented palettes. Check contrast.

### Artifact Format Rules

- Self-contained HTML with embedded CSS/JS
- Responsive unless intentionally fixed-size
- Preserve previous versions for major revisions (`Name v2.html`)
- Modern CSS: variables, grid, container queries, focus states, hover states, `prefers-reduced-motion`
- Mobile hit targets ≥ 44px

### Deck Rules

Fixed-size canvas (1920×1080 default), keyboard navigation, visible slide count, localStorage persistence. 1-2 background colors max. Keep slides sparse.

### Variation Rules

Default to at least three options: Conservative, Strong-fit, Divergent. Variations should explore different design stances, not just color swaps.

### Content Discipline

No filler content. No fake metrics, decorative stats, generic feature grids, placeholder testimonials. Every element must earn its place.

### Verification

Minimum: file exists, HTML complete, syntax checked. Better: open in browser, check console errors, inspect screenshots, test interactions.

---

## Quick Mockups

Use when the user wants to see a design direction before committing — "sketch this screen," "show me what X could look like," "compare layout A vs B."

### Core Method

```
intake → variants → head-to-head → pick winner (or iterate)
```

**Intake** (skip if user gave enough):
1. **Feel** — adjectives, emotions, a vibe
2. **References** — apps/sites that capture the feel
3. **Core action** — single most important thing a user does

**Variants** (2-3, never 1, rarely 4+):
Each variant takes a **different design stance**, not different pixel values:
- Density: compact / airy / ultra-dense
- Emphasis: content-first / action-first / tool-first
- Aesthetic: editorial / utilitarian / playful
- Layout: single-column / sidebar / split-pane

**Make them real HTML** — single self-contained files, inline styles, system fonts or one Google Font, realistic content, interactive (clickable links, hovers, at least one state transition). Verify with `browser_navigate` + `browser_vision`.

**Head-to-head** — present as comparison table with opinions, not just listings.

### Variant README

Each variant gets a README: design stance, key choices (layout/typography/color/interaction), trade-offs, best for.

### Interactivity Bar

A sketch is interactive enough when the user can: click a primary action, see one meaningful state transition, hover recognizable affordances.

---

## Design System Library

54 real-world design systems ready for use. Each captures a site's complete visual language: colors, typography, components, spacing, shadows.

### How to Use

1. Pick a design from the catalog below
2. Load it: `skill_view(name="web-design", file_path="templates/<site>.md")`
3. Use the design tokens and component specs when generating HTML

### Choosing a Design

| Use case | Recommended designs |
|----------|-------------------|
| Developer tools / dashboards | Linear, Vercel, Supabase, Raycast, Sentry |
| Documentation / content | Mintlify, Notion, Sanity, MongoDB |
| Marketing / landing pages | Stripe, Framer, Apple, SpaceX |
| Dark mode UIs | Linear, Cursor, ElevenLabs, Warp, Superhuman |
| Light / clean UIs | Vercel, Stripe, Notion, Cal.com, Replicate |
| Playful / friendly | PostHog, Figma, Lovable, Zapier, Miro |
| Premium / luxury | Apple, BMW, Stripe, Superhuman, Revolut |
| Data-dense / dashboards | Sentry, Kraken, Cohere, ClickHouse |
| Monospace / terminal | Ollama, OpenCode, x.ai, VoltAgent |

### Font Substitution Reference

| Proprietary Font | CDN Substitute | Character |
|---|---|---|
| Geist / Geist Sans | Geist (Google Fonts) | Geometric, compressed tracking |
| sohne-var (Stripe) | Source Sans 3 | Light weight elegance |
| Airbnb Cereal VF | DM Sans | Rounded, friendly |
| Circular (Spotify) | DM Sans | Geometric, warm |
| figmaSans | Inter | Clean humanist |
| Pin Sans (Pinterest) | DM Sans | Friendly, rounded |
| UberMove | DM Sans | Bold, tight |

### Design Catalog

**AI & Machine Learning:** claude.md, cohere.md, elevenlabs.md, minimax.md, mistral.ai.md, ollama.md, opencode.ai.md, replicate.md, runwayml.md, together.ai.md, voltagent.md, x.ai.md

**Developer Tools:** cursor.md, expo.md, linear.app.md, lovable.md, mintlify.md, posthog.md, raycast.md, resend.md, sentry.md, supabase.md, superhuman.md, vercel.md, warp.md, zapier.md

**Infrastructure:** clickhouse.md, composio.md, hashicorp.md, mongodb.md, sanity.md, stripe.md

**Design & Productivity:** airtable.md, cal.md, clay.md, figma.md, framer.md, intercom.md, miro.md, notion.md, pinterest.md, webflow.md

**Fintech:** coinbase.md, kraken.md, revolut.md, wise.md

**Enterprise & Consumer:** airbnb.md, apple.md, bmw.md, ibm.md, nvidia.md, spacex.md, spotify.md, uber.md

### HTML Generation Pattern

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Page Title</title>
  <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
  <style>
    :root {
      --color-bg: #ffffff;
      --color-text: #171717;
      --color-accent: #533afd;
    }
    body {
      font-family: 'Inter', system-ui, sans-serif;
      color: var(--color-text);
      background: var(--color-bg);
    }
  </style>
</head>
<body>
  <!-- Build using component specs from the template -->
</body>
</html>
```

---

## Pitfalls

- Do not produce generic SaaS layouts and call them designed
- Do not over-ask when the user already gave enough direction
- Do not under-ask for high-fidelity work with no brand context
- Do not claim browser verification unless it actually happened
- Do not create variations that are merely color swaps
- Do not leave the project as a pile of options forever — consolidate when the user picks
- Do not add filler content — every element must earn its place
- Always check `browser_console()` after navigating — silent JS errors are high-value findings
