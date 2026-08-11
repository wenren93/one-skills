---
name: code-review
description: "Pre-commit code review: security scan, quality gates, parallel multi-agent cleanup, and auto-fix loop."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [code-review, security, cleanup, verification, quality, pre-commit, auto-fix, simplify]
    related_skills: [github-code-review, test-driven-development, plan]
---

# Code Review & Pre-Commit Verification

Two complementary approaches to catching problems before code lands. Use either or both depending on the situation.

**This skill vs `github-code-review`:** This skill verifies YOUR changes before committing. `github-code-review` reviews OTHER people's PRs on GitHub with inline comments.

## When to Use

- After implementing a feature or bug fix, before `git commit` or `git push`
- When user says "commit", "push", "ship", "done", "verify", "review", or "simplify"
- After completing a task with 2+ file edits in a git repo

**Skip for:** documentation-only changes, pure config tweaks, or when user says "skip verification".

---

## Approach 1: Security & Quality Gate (requesting-code-review)

Automated verification pipeline: static scans, baseline-aware quality gates, an independent reviewer subagent, and an auto-fix loop.

**Core principle:** No agent should verify its own work. Fresh context finds what you miss.

### Step 1 — Get the diff

```bash
git diff --cached
```

If empty, try `git diff` then `git diff HEAD~1 HEAD`.

### Step 2 — Static security scan

```bash
# Hardcoded secrets
git diff --cached | grep "^+" | grep -iE "(api_key|secret|password|token|passwd)\s*=\s*['\"][^'\"]{6,}['\"]"

# Shell injection
git diff --cached | grep "^+" | grep -E "os\.system\(|subprocess.*shell=True"

# Dangerous eval/exec
git diff --cached | grep "^+" | grep -E "\beval\(|\bexec\("

# Unsafe deserialization
git diff --cached | grep "^+" | grep -E "pickle\.loads?\("

# SQL injection
git diff --cached | grep "^+" | grep -E "execute\(f\"|\.format\(.*SELECT|\.format\(.*INSERT"
```

### Step 3 — Baseline tests and linting

Detect project language and run appropriate tools. Capture failure count BEFORE changes as **baseline_failures** (stash, run, pop). Only NEW failures block the commit.

```bash
# Python
python -m pytest --tb=no -q 2>&1 | tail -5
which ruff && ruff check . 2>&1 | tail -10

# Node
npm test -- --passWithNoTests 2>&1 | tail -5
```

### Step 4 — Self-review checklist

- [ ] No hardcoded secrets, API keys, or credentials
- [ ] Input validation on user-provided data
- [ ] SQL queries use parameterized statements
- [ ] No debug print/console.log left behind
- [ ] No commented-out code
- [ ] New code has tests

### Step 5 — Independent reviewer subagent

```python
delegate_task(
    goal="""You are an independent code reviewer. Review the git diff and return ONLY valid JSON.

FAIL-CLOSED RULES:
- security_concerns non-empty -> passed must be false
- logic_errors non-empty -> passed must be false

<static_scan_results>[INSERT FINDINGS]</static_scan_results>
<code_changes>[INSERT GIT DIFF]</code_changes>

Return ONLY: {"passed": bool, "security_concerns": [], "logic_errors": [], "suggestions": [], "summary": "..."}""",
    toolsets=["terminal"]
)
```

### Step 6 — Auto-fix loop (max 2 cycles)

If verification failed, spawn a fix agent that addresses ONLY the reported issues, then re-verify.

### Step 7 — Commit

```bash
git add -A && git commit -m "[verified] <description>"
```

---

## Approach 2: Parallel 3-Agent Cleanup (simplify-code)

Three focused reviewers running in parallel, each searching the codebase for a single class of problem.

**Core principle:** Three narrow reviewers beat one broad reviewer. They run concurrently — you pay the latency of one review, not three.

### When to Use This Approach

- User says "simplify" / "simplify my changes" / "clean up my changes"
- After a feature is complete but before committing
- Optional modifiers: `focus on efficiency`, `dry run`, `the last commit`

### Phase 1 — Identify changes

```bash
git diff                    # Default: uncommitted changes
git diff HEAD               # Include staged
git diff main...HEAD        # Full branch diff
```

### Phase 2 — Launch three reviewers in parallel

Use `delegate_task` **batch mode** — pass all three tasks in one `tasks` array. Give every reviewer the COMPLETE diff plus repo path.

**Reviewer 1 — Code Reuse:** Search for existing functions/constants/patterns the new code could call instead of reimplementing. Flag duplications with file:line evidence.

**Reviewer 2 — Code Quality:** Redundant state, parameter sprawl, copy-paste-with-variation, leaky abstractions, stringly-typed code.

**Reviewer 3 — Efficiency:** Unnecessary work, missed concurrency, hot-path bloat, TOCTOU anti-patterns, memory issues, overly broad reads.

Each reviewer reports: `file:line → problem → suggested fix`, ranked `high`/`medium`/`low` confidence.

### Phase 3 — Aggregate and apply

1. Merge findings, dedup overlapping suggestions
2. Discard false positives
3. Resolve conflicts: **correctness > user's stated focus > readability > micro-perf**
4. Apply surviving fixes with `patch`/`write_file`
5. Verify: run targeted tests, re-run linter
6. Summarize what changed and what was deliberately skipped

---

## Pitfalls

- **Empty diff** — check `git status`, tell user nothing to verify
- **Large diff (>15k chars)** — split by file, review each separately
- **delegate_task returns non-JSON** — retry once with stricter prompt, then treat as FAIL
- **No test framework found** — skip regression check, reviewer verdict still runs
- **Don't fan out wider than ~3 reviewers** — more cost, more conflicts
- **Give the WHOLE diff to each reviewer** — splitting defeats the design
- **Apply ≠ rewrite** — keep edits scoped to what the diff touched
