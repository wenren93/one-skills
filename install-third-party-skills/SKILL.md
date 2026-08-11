---
name: install-third-party-skills
description: |
  Install skills from a third-party GitHub repository (Claude Code / Codex /
  Agent-Skills format) into WorkBuddy's user skill directory. Use when the user
  provides a GitHub repo URL or a skill name and asks to install or find a skill
  that is NOT available in the WorkBuddy recommendation market
  (workbuddy_marketplace_skill). Covers clone, security audit, format
  adaptation, and flattened install with provenance tracking.
agent_created: true
version: "1.0.0"
---

# Install Third-Party Skills

## Overview

WorkBuddy's recommendation market does not carry every community skill. When a
user points at a GitHub repository of skills (e.g. `github.com/OWNER/skills`)
and asks to install it, this skill provides a safe, repeatable workflow:
clone → security-audit → adapt to WorkBuddy's `SKILL.md` format → install into
`~/.workbuddy/skills/` (flattened, with provenance metadata).

This workflow was first used to install Matt Pocock's
`github.com/mattpocock/skills` (35 skills, MIT) into WorkBuddy.

## When to Use

- User says "install GITHUB_REPO", "install this skill", or pastes a GitHub
  URL whose path ends in `/skills` or contains a `SKILL.md`.
- The `workbuddy_marketplace_skill` search returns no match for the requested
  skill name/keyword.
- Do NOT use this for skills already in the WorkBuddy recommendation market —
  those go through `workbuddy_marketplace_skill` install instead.

## Workflow

### Step 1 — Validate the source

1. If the user gave a profile/repo URL that is NOT a skills repo (e.g. a
   `readme.md`-only profile page), stop and tell the user it contains no
   installable skill. Example: `github.com/mattpocock/mattpocock` is just a
   promo README — nothing to install.
2. A real skills repo has a `skills/` tree where each subfolder contains a
   `SKILL.md`. Confirm this before proceeding.

### Step 2 — Clone (shallow, to a temp dir)

```bash
git clone --depth 1 REPO_URL /tmp/SHORT_NAME-skills
```

Never clone into a personal directory or the workspace. Use a system temp dir.

### Step 3 — Security audit (MANDATORY before install)

Run the audit even if the `skills-security-check` skill is unavailable — perform
it manually by following `references/security-audit.md`. In short:

- Grep the whole repo (excluding `.git`) for dangerous patterns:
  `rm -rf`, `curl ... | sh`, `wget ... | sh`, `eval (`, `base64 -d`,
  `sudo `, `chmod 777`, `/dev/tcp`, `ssh-keygen`, `nc -`, `curl ... POST`,
  `git reset --hard`, `git push --force`, reading `~/.ssh` / env secrets.
- Read every bundled `scripts/*.sh` / `*.py` / `*.js` file in full — scripts are
  the highest-risk surface.
- Rate the result:
  - **P0** (exfiltration, RCE, destructive without guard): STRONGLY warn, require
    explicit confirmation before any install.
  - **P1** (questionable but bounded): warn and require explicit confirmation.
  - **P2** (safe / only beneficial, e.g. guardrail hooks): proceed normally.
- Present the audit report to the user before installing.

### Step 4 — Decide scope and check collisions

- Exclude `skills/deprecated/` (or any clearly-archived folder).
- List skill names: `find skills -name SKILL.md -not -path '*/deprecated/*'`.
- For each skill name, check it does not already exist in
  `~/.workbuddy/skills/NAME`. If a collision exists, decide per skill (skip,
  rename with a prefix, or ask the user) — do NOT silently overwrite an existing
  WorkBuddy skill.
- Note which skills are `in-progress` / harness-specific (Claude Code / Codex
  hooks, slash commands) — they install fine as guidance but will not auto-wire
  native hooks in WorkBuddy.

### Step 5 — Adapt and install (flattened)

For each skill folder:

```bash
SRC=/tmp/SHORT_NAME-skills/skills
DEST=/Users/one/.workbuddy/skills
for skillmd in $(find "$SRC" -name SKILL.md -not -path '*/deprecated/*' | sort); do
  sdir=$(dirname "$skillmd")
  name=$(basename "$sdir")
  dstdir="$DEST/$name"
  rm -rf "$dstdir"
  mkdir -p "$dstdir"
  cp -R "$sdir"/. "$dstdir"/          # keep bundled references/ and scripts/
  python3 scripts/augment_frontmatter.py "$dstdir/SKILL.md" "REPO_VERSION"
done
```

`scripts/augment_frontmatter.py` injects `version` and `source` into the
frontmatter (only if missing) so installs stay trackable for future updates. It
leaves the body untouched and preserves internal cross-references (skills that
call each other by name). WorkBuddy tolerates extra frontmatter fields, so
`disable-model-invocation`, `allowed-tools`, etc. pass through harmlessly.

### Step 6 — Verify and report

- Spot-check: head of a few `SKILL.md` files show the augmented frontmatter;
  bundled files (e.g. `tests.md`, `scripts/*.sh`) copied alongside.
- Report: number installed, audit rating, which are experimental/harness-specific,
  and the install path. Offer a short usage note.

## Resources

### scripts/augment_frontmatter.py

Injects `version` / `source` into a `SKILL.md` frontmatter without parsing YAML
(inserts after the opening `---`), so it is safe for any valid frontmatter.

### references/security-audit.md

The full manual security-audit checklist used in Step 3.
