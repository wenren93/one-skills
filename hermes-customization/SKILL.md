---
name: hermes-customization
description: "Customize Hermes appearance and behavior: desktop plugins, color themes, TUI widgets, and animated mascots. Use when the user wants to change how Hermes looks or add UI extensions."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, customization, themes, plugins, widgets, petdex, mascot, ui, appearance]
    category: productivity
---

# Hermes Customization

Four ways to customize Hermes: desktop plugins (UI panes and commands), color themes (skins), TUI widgets (dock panels), and animated mascots (petdex).

## Decision: Which Customization?

| Goal | Section |
|------|---------|
| Add a UI pane or command to the desktop app | [Desktop Plugins] |
| Change colors/appearance across CLI, TUI, and desktop | [Color Themes] |
| Add a live panel to the TUI dock | [TUI Widgets] |
| Add an animated mascot | [Petdex] |

---

## Color Themes

Author a Hermes **skin** — one YAML file that themes the CLI, TUI, and desktop GUI at once. The skin engine resolves the active skin and the gateway pushes it to every surface.

### When to Use
- User wants a custom look ("make me a synthwave theme", "dark forest vibes")
- User wants CLI/TUI/desktop to share one coordinated palette
- User wants to iterate live — edit YAML and every surface repaints

### Quick Reference — Element → Key

| Visible element | Key to set | Falls back to |
|---|---|---|
| App background | `background` | terminal default |
| Tool-call marker (`●`) | `ui_tool` | `ui_accent` |
| Thinking/reasoning text | `ui_thinking` | `banner_dim` |
| Accent — headings, links | `ui_accent` / `banner_accent` | — |
| Primary text | `banner_title` / `ui_primary` | — |
| Body/label text | `ui_text` / `banner_text` | — |
| Muted/secondary | `banner_dim` | — |
| Borders, rules | `ui_border` / `banner_border` | — |
| Success/warn/error | `ui_ok` / `ui_warn` / `ui_error` | — |
| Status bar text | `status_bar_text` | — |
| Diff add/remove | `diff_added` / `diff_removed` | — |
| Code syntax | `syntax_string` / `syntax_number` / `syntax_keyword` / `syntax_comment` | accent/text/muted |

### Procedure
1. Copy `templates/skin.yaml` and fill in the palette (keep every key)
2. Write to `<hermes-home>/skins/<name>.yaml`
3. Apply: `hermes config set display.skin <name>` (gateway repaints live)
4. Tweak one color: `hermes skin set <key> <hex>`

### Pitfalls
- Keep `#rrggbb` hex. Shorthand `#rgb`, `rgb()`, named colors may not parse.
- Always set `background`. Without it the GUI guesses from text luminance.
- Never hand-edit `config.yaml` to activate. Use `hermes config set`.
- Skin name must not collide with built-ins (`mono`, `slate`, `cyberpunk`, `nous`, `midnight`, `ember`).

---

## Desktop Plugins

Write plugins for the Hermes desktop app: statusbar items, layout panes, command-palette commands, keybinds, routes, and themes. A plugin is a single plain-JavaScript ESM file loaded at runtime.

### When to Use
- User asks for a new desktop UI element (pane, statusbar widget, dashboard, command)
- You want to surface data computed via gateway RPC inside the app

### Quick Reference
- `ctx.register({ id, area, order?, render?, data? })` — contribute UI
- Key areas: `'statusBar.right'`/`'statusBar.left'` (chips), `'panes'` (layout zones), `PALETTE_AREA` (⌘K commands), `KEYBINDS_AREA` (rebindable actions)
- Pane placement: `placement: 'left'|'right'|'bottom'|'main'` with optional `dock: { pane, pos }`
- `host.state.*` — readonly reactive atoms: `activeSessionId`, `cwd`, `gateway`, `model`, `profile`, `viewport`
- `host.request(method, params)` — gateway JSON-RPC
- `host.onEvent(type, fn)` — live gateway events

### Procedure
1. Create `$HERMES_HOME/desktop-plugins/<name>/plugin.js` from `templates/plugin.js`
2. The desktop app hot-loads within seconds. Fallback: ⌘K → Reload desktop plugins.
3. UI components: `Button`, `Input`, `Dialog*`, `DropdownMenu*`, etc. from `@hermes/plugin-sdk`

### Pitfalls
- NEVER hardcode colors. Use theme variables: `var(--ui-text-secondary)`, `var(--ui-accent)`.
- JSX syntax will not parse — use `jsx('div', { children: ... })` from `react/jsx-runtime`.
- Canvas panes MUST track container with `ResizeObserver`.
- Only import from `@hermes/plugin-sdk`, `react`, `react/jsx-runtime`.

---

## TUI Widgets

Author widget apps for the Hermes TUI (`hermes --tui`): glanceable ambient panels docked above the status bar, or modal overlays.

### When to Use
- User asks for a live panel in the TUI (ticker, clock, countdown, status card)
- User wants a custom modal tool bound to a slash command

### Quick Reference
- Default-export `register(sdk)` with `defineWidgetApp({ id, help, mode, init, reduce, render })`
- `mode: 'ambient'` — docks, no input capture; `mode: 'modal'` — owns every keypress
- Charts: `sdk.sparkline()`, `sdk.sparkRows()`, `sdk.gauge()`, `sdk.hbars()`
- Colors: ALWAYS theme tones (`t.color.primary/label/muted/ok/error/…`), never hardcoded

### Procedure
1. Write `~/.hermes/tui-widgets/<name>.mjs` (see templates)
2. TUI hot-loads on write. `/<id>` to launch.
3. Ambient widgets: end `register()` with `sdk.openWidget(app, app.init(''))` to auto-dock.

### Pitfalls
- No JSX in `.mjs` — use `h(...)` from sdk.
- Ambient widgets must stay small (≤ ~6 rows).
- Keep intervals ≥ 250ms for animation.

---

## Petdex (Animated Mascots)

Browse, install, and select animated "pet" mascots from the public [petdex](https://github.com/crafter-station/petdex) gallery. An installed pet reacts to agent activity (idle, running, reviewing, error, done).

### Quick Reference

| Goal | Command |
|------|---------|
| Browse gallery | `hermes pets list [filter]` |
| Install + activate | `hermes pets install <slug> --select` |
| Preview | `hermes pets show [slug] [--cycle]` |
| Resize | `hermes pets scale <factor>` (0.1–3.0) |
| Disable | `hermes pets off` |
| Diagnose | `hermes pets doctor` |

### Pitfalls
- Pet only shows once installed AND selected (`enabled: true`).
- Inside a pipe/redirect (no TTY) rendering is disabled.
- Use `hermes pets` CLI, not the petdex npm CLI (different install paths).

---

## Verification

- **Themes**: `hermes config get display.skin` reports the name. Repaint lands within ~1 second.
- **Plugins**: UI appears after Reload desktop plugins. No error toast.
- **Widgets**: `/widgets-reload` lists the file. `/<id>` shows the widget.
- **Pets**: `hermes pets doctor` reports `✓ ready`.
