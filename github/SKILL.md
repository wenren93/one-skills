---
name: github
description: "GitHub workflows via gh CLI and git: auth, PR lifecycle, code review, issues, repo management, and codebase inspection."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [github, git, gh-cli, pull-requests, code-review, issues, repositories, authentication]
    related_skills: [code-review]
---

# GitHub Workflows

Complete guide for working with GitHub from the terminal. Every section shows `gh` first, then `git` + `curl` fallback.

## Auth Detection (shared by all workflows)

Run this at the start of any GitHub task:

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi

REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

---

## 1. Authentication Setup

**Method 1: gh CLI (simplest)**
```bash
gh auth login                    # Interactive browser login
echo "$TOKEN" | gh auth login --with-token   # Token-based
gh auth setup-git                # Configure git credentials through gh
gh auth status                   # Verify
```

**Method 2: Git-only (no gh needed)**
```bash
# HTTPS token
git config --global credential.helper store
# Then do any git op — enter username + token when prompted

# SSH key
ssh-keygen -t ed25519 -C "email@example.com" -f ~/.ssh/id_ed25519 -N ""
cat ~/.ssh/id_ed25519.pub   # Add to https://github.com/settings/keys
ssh -T git@github.com       # Test

# Git identity
git config --global user.name "Name"
git config --global user.email "email@example.com"
```

**API without gh:** Extract token from git credentials, then `curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/...`

See `references/github-auth.md` for full setup details.

---

## 2. PR Lifecycle

### Branch → Commit → Push → Create PR

```bash
git checkout main && git pull origin main
git checkout -b feat/description

# (make changes with file tools)

git add src/file.py && git commit -m "feat: add feature"
git push -u origin HEAD

# Create PR
gh pr create --title "feat: add feature" --body "## Summary\n...\nCloses #42"
# Or with curl:
curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/pulls \
  -d '{"title":"feat: add feature","body":"...","head":"branch","base":"main"}'
```

### Monitor CI

```bash
gh pr checks              # One-shot
gh pr checks --watch      # Poll until done

# Or with curl:
SHA=$(git rev-parse HEAD)
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/$OWNER/$REPO/commits/$SHA/status
```

### Auto-Fix CI Failures

```bash
gh run list --branch $(git branch --show-current) --limit 5
gh run view <RUN_ID> --log-failed
# Fix, commit, push, re-check
```

### Merge

```bash
gh pr merge --squash --delete-branch
gh pr merge --auto --squash --delete-branch   # Auto-merge when green
```

See `references/github-pr-workflow.md` for full lifecycle details, templates, and conventional commits.

---

## 3. Code Review

### Review Local Changes (Pre-Push)

```bash
git diff main...HEAD --stat        # Scope
git diff main...HEAD               # Full diff
git diff main...HEAD | grep -n "print(\|console.log\|TODO\|FIXME"  # Red flags
```

### Review a PR on GitHub

```bash
gh pr view 123
gh pr diff 123
gh pr checkout 123                  # Check out locally for full review

# Leave inline comments
gh api repos/$OWNER/$REPO/pulls/123/comments --method POST \
  -f body="Use parameterized queries." -f path="src/auth.py" \
  -f commit_id="$SHA" -f line=45 -f side="RIGHT"

# Submit formal review
gh pr review 123 --approve --body "LGTM!"
gh pr review 123 --request-changes --body "See inline comments."
```

### Review Checklist

- **Correctness:** Does code do what it claims? Edge cases? Error paths?
- **Security:** No hardcoded secrets, input validation, parameterized SQL, no XSS
- **Quality:** Clear naming, no duplication, single responsibility
- **Testing:** New code paths tested? Happy path + error cases?
- **Performance:** No N+1 queries, appropriate caching, no blocking in async

See `references/github-code-review.md` for curl-based review workflow and the review output template.

---

## 4. Issues Management

```bash
# View
gh issue list --state open --label "bug"
gh issue view 42

# Create
gh issue create --title "Bug: login redirect broken" \
  --body "## Steps to Reproduce\n1. ...\n## Expected\n..." \
  --label "bug,backend" --assignee "username"

# Manage
gh issue edit 42 --add-label "priority:high"
gh issue edit 42 --add-assignee @me
gh issue comment 42 --body "Investigating..."
gh issue close 42
gh issue reopen 42

# Triage workflow
gh issue list --label "needs-triage" --state open
```

See `references/github-issues.md` for curl-based workflows and issue templates.

---

## 5. Repository Management

```bash
# Clone
gh repo clone owner/repo-name

# Create
gh repo create my-project --public --clone
gh repo create my-org/my-project --private --clone

# Fork
gh repo fork owner/repo-name --clone

# Settings
gh repo edit --description "Updated" --visibility public
gh repo edit --enable-auto-merge

# Releases
gh release create v1.0.0 --title "v1.0.0" --generate-notes
gh release list

# Secrets (GitHub Actions)
gh secret set API_KEY --body "value"
gh secret list

# Workflows
gh workflow list
gh run list --limit 10
gh run view <RUN_ID> --log-failed
gh run rerun <RUN_ID> --failed
```

See `references/github-repo-management.md` for curl-based workflows and branch protection.

---

## 6. Codebase Inspection

Analyze repos for LOC, language breakdown, and code-vs-comment ratios:

```bash
pip install pygount
pygount --format=summary --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,dist,build" .
```

Always use `--folders-to-skip` to exclude dependency directories.

---

## Quick Reference

| Action | gh | git + curl |
|--------|-----|-----------|
| Auth | `gh auth login` | `git config credential.helper store` |
| List PRs | `gh pr list` | `curl GET /repos/o/r/pulls` |
| Create PR | `gh pr create` | `curl POST /repos/o/r/pulls` |
| View diff | `gh pr diff` | `git diff main...HEAD` |
| Merge | `gh pr merge --squash` | `curl PUT /repos/o/r/pulls/N/merge` |
| List issues | `gh issue list` | `curl GET /repos/o/r/issues` |
| Create issue | `gh issue create` | `curl POST /repos/o/r/issues` |
| Create release | `gh release create` | `curl POST /repos/o/r/releases` |
| Set secret | `gh secret set` | `curl PUT /repos/o/r/actions/secrets/KEY` |
