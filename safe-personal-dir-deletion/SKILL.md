---
name: safe-personal-dir-deletion
description: Use when a user asks to delete, remove, clean up, move, or empty files in personal directories (Desktop, Downloads, Documents, Home, ~/). Enforces read-only scan first, bold warning, explicit confirmation, recoverable move instead of permanent delete, and batch verification. Covers macOS TCC blocking ~/.Trash reads, Finder osascript -10004 permission errors, and sandboxed-shell write overlays.
---

# Safe Personal-Directory Deletion

## Overview
Personal dirs (Desktop / Downloads / Documents / Home) are No-Go Zones for recursive or bulk destructive ops. When the user asks to delete files there, you must: **scan read-only → warn + list every file → get explicit confirmation → move to a RECOVERABLE location in small batches → verify each batch.** Never `rm -rf` / bulk-delete. The goal is zero irreversible loss.

## When to Use
- "删除 / 清理 / 清空 / 移动 这个目录里的文件"
- "remove all X files", "clean up my Downloads", "delete duplicates", "empty trash"
- Target path is under `~/`, Desktop, Downloads, Documents, or any personal dir
- Even "just scan / list" = read-only. Do NOT act.

When NOT to use: normal project/workspace files outside personal dirs (git/rm is fine); a single-file delete the user confirms inline with a full explicit path.

## Core Procedure
1. **Scan (read-only).** `find <dir> -type f \( -iname '*.ext' ... \)` — do NOT modify. Count + total size. Descend subfolders so nothing is missed.
2. **Warn + List.** Print bold `⚠️ 此操作非常危险，可能导致不可逆的数据丢失！`, then list **EVERY** affected file path + size, and explain the specific risks (nearby non-target materials, no cloud recovery).
3. **Confirm.** Use AskUserQuestion for explicit confirmation. Do not proceed without it.
4. **Recoverable move, never delete.** Move to a recoverable location, NOT `rm`. Batch ≤10 files; verify after each batch.
5. **Verify.** After all batches: originals gone + destination count matches.

## macOS Gotchas (learned the hard way)
- **`osascript` Finder `delete` → `-10004 权限违例`.** The shell isn't authorized to control Finder. Don't rely on it; if you must, have the user grant System Settings ▸ Privacy & Security ▸ Automation, then retry.
- **TCC blocks the shell from reading `~/.Trash`** (`Operation not permitted`) in BOTH sandboxed and non-sandboxed Bash, and Spotlight won't index Trash. ⇒ You CANNOT programmatically confirm files landed in Trash. Two safe fixes:
  - **(Preferred)** Move to a plain, shell-readable subfolder instead of `~/.Trash`, e.g. `~/Downloads/_deleted_<timestamp>/`, so you can verify each batch with `ls`/`find`.
  - Or move to `~/.Trash` and ask the **user** to open Finder ▸ Trash to confirm visually.
- **Sandbox write overlay.** Bash writes may go to an ephemeral overlay the shell later can't see. Verify via a path the sandbox CAN read (e.g. `~/Downloads`); if you can't read the destination, you can't verify it — choose a readable destination.
- **HTML-encoded names** like `Node &#47; NPM` are literal filename characters, NOT a `/`. Pass them through quoted strings; don't "fix" the slash.

## Quick Reference
| Step | Action | Destructive? |
|------|--------|--------------|
| Scan | `find ... -type f` | No |
| Warn | bold + full path list | No |
| Confirm | AskUserQuestion | No |
| Move | `mv`/`shutil.move` to recoverable dir, ≤10/batch | Yes (recoverable) |
| Verify | `find` originals = 0; dest count matches | No |

## Reusable Tool
See `scripts/safe_delete.py` — moves a list of absolute paths (one per line in a file) to a recoverable destination folder in batches of 10, with collision-safe renaming and per-batch verification. Agent does scan + AskUserQuestion confirm, writes the path list, then runs the script.

## Common Mistakes
- Deleting immediately without scan/confirm.
- Using `rm`/`rm -rf` on personal dirs → unrecoverable.
- Trusting `~/.Trash` as a verifiable destination without checking TCC.
- Reading a "0 found" shell result as "empty" — could be TCC `Operation not permitted` hiding the truth.
- Moving >10 files per batch (hard to verify / recover).

## Real-World Example
Deleted 15 course `.mp4` (2.36 GB) from `~/Downloads/...`: scanned + listed all 15, confirmed via AskUserQuestion, moved to `~/.Trash` in 10+5 batches, verified originals empty. Lesson: shell couldn't read `~/.Trash` (TCC), so prefer a readable `_deleted_/` folder or have the user confirm in Finder.
