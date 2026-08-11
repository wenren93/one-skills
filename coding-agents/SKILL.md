---
name: coding-agents
description: "Delegate coding to external CLI agents: Claude Code, Codex, OpenCode."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Claude, Codex, OpenCode, OpenAI, Anthropic, Code-Review, Refactoring, PTY, Automation]
    related_skills: [hermes-agent]
---

# Coding Agents

Delegate coding tasks to external autonomous coding agent CLIs via Hermes terminal/process tools. Three agents are supported — choose based on availability, preference, or task requirements.

## Decision: Which Agent?

| Agent | Provider | Best for | Install |
|-------|----------|----------|---------|
| **Claude Code** | Anthropic | Complex multi-step tasks, PR reviews, structured JSON output | `npm install -g @anthropic-ai/claude-code` |
| **Codex** | OpenAI | One-shot tasks, batch issue fixing, sandboxed execution | `npm install -g @openai/codex` |
| **OpenCode** | Multi-provider | Provider-agnostic work, long sessions, parallel tasks | `npm i -g opencode-ai@latest` |

**Default choice:** Claude Code for complex reasoning, Codex for quick one-shots, OpenCode when you need provider flexibility.

## Common Workflow (All Agents)

1. **Verify prerequisites**: check agent is installed and authenticated
2. **Choose mode**: one-shot (`exec`/`run`/`-p`) vs interactive (background PTY)
3. **Set workdir**: always scope to the target project directory
4. **Execute**: run the task with appropriate flags
5. **Monitor**: poll/log for long tasks, submit input if asked
6. **Report**: summarize changes, test results, and next steps

## One-Shot Tasks (Preferred for Most Work)

All three agents support bounded, non-interactive execution:

```bash
# Claude Code (print mode)
claude -p 'Add error handling to all API calls in src/' --allowedTools 'Read,Edit' --max-turns 10

# Codex
codex exec 'Add dark mode toggle to settings'

# OpenCode
opencode run 'Add retry logic to API calls and update tests'
```

## Interactive Sessions (Multi-Turn Work)

For iterative work requiring follow-up prompts, use background PTY sessions:

### Claude Code (tmux-based)
```bash
tmux new-session -d -s claude-work -x 140 -y 40
tmux send-keys -t claude-work 'cd /path/to/project && claude' Enter
sleep 5 && tmux send-keys -t claude-work 'Your task description' Enter
# Monitor: tmux capture-pane -t claude-work -p -S -50
```

### Codex (background PTY)
```bash
terminal(command="codex exec --full-auto 'Refactor the auth module'", workdir="~/project", background=true, pty=true)
# Monitor: process(action="poll", session_id="<id>")
```

### OpenCode (background PTY)
```bash
terminal(command="opencode", workdir="~/project", background=true, pty=true)
process(action="submit", session_id="<id>", data="Implement OAuth refresh flow")
# Exit: process(action="write", session_id="<id>", data="\x03")
```

## PR Reviews

All agents support code review:

```bash
# Claude Code (print mode — cleanest)
git diff main...feature-branch | claude -p 'Review this diff for bugs, security issues, and style problems.' --max-turns 1

# Claude Code (from PR number)
claude -p 'Review this PR thoroughly' --from-pr 42 --max-turns 10

# Codex (clone + review)
REVIEW=$(mktemp -d) && git clone https://github.com/user/repo.git $REVIEW && cd $REVIEW && gh pr checkout 42 && codex review --base origin/main

# OpenCode
opencode pr 42
```

## Parallel Work

Run multiple agents simultaneously on independent tasks:

```bash
# Claude Code (tmux parallel)
tmux new-session -d -s task1 && tmux send-keys -t task1 'cd ~/project && claude -p "Fix auth bug" --max-turns 10' Enter
tmux new-session -d -s task2 && tmux send-keys -t task2 'cd ~/project && claude -p "Write tests" --max-turns 15' Enter

# Codex (worktrees)
git worktree add -b fix/issue-78 /tmp/issue-78 main
codex --yolo exec 'Fix issue #78' --workdir /tmp/issue-78

# OpenCode (separate workdirs)
opencode run 'Fix issue #101' --workdir /tmp/issue-101
opencode run 'Add parser tests' --workdir /tmp/issue-102
```

## Session Management

| Agent | Resume | Continue | List sessions |
|-------|--------|----------|---------------|
| Claude Code | `claude -r "id"` | `claude -c` | Session files in `.claude/` |
| Codex | N/A | N/A | N/A |
| OpenCode | `opencode -s ses_abc123` | `opencode -c` | `opencode session list` |

## Cost Control

| Agent | Cost cap | Turn limit | Model selection |
|-------|----------|------------|-----------------|
| Claude Code | `--max-budget-usd N` | `--max-turns N` | `--model sonnet/opus/haiku` |
| Codex | N/A | N/A | Via OPENAI model config |
| OpenCode | N/A | N/A | `--model provider/model` |

## Rules for Hermes Agents

1. **Prefer one-shot mode** for single tasks — cleaner, no dialog handling
2. **Always set `workdir`** — keep the agent focused on the right project
3. **Set limits** — `--max-turns` (Claude Code) prevents runaway loops
4. **Monitor background sessions** — use `process(action="poll"|"log")` or `tmux capture-pane`
5. **Clean up** — kill tmux sessions and background processes when done
6. **Report results** — summarize what changed, tests that pass/fail, remaining risks
7. **Use `--allowedTools`** (Claude Code) to restrict capabilities to what's needed

---

## Claude Code — Detailed Reference

### Authentication
- **OAuth**: run `claude` once to log in (browser OAuth for Pro/Max)
- **API key**: set `ANTHROPIC_API_KEY`
- **Console auth**: `claude auth login --console` for API key billing
- **Check status**: `claude auth status` (JSON) or `claude auth status --text`

### Print Mode Deep Dive
```bash
# Structured JSON output
claude -p 'Analyze auth.py' --output-format json --max-turns 5

# Streaming JSON
claude -p 'Write a summary' --output-format stream-json --verbose

# JSON Schema for structured extraction
claude -p 'List functions in src/' --output-format json --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}}}'

# Session continuation
claude -p 'Continue refactoring' --resume $(cat /tmp/session.json | python3 -c 'import json,sys; print(json.load(sys.stdin)["session_id"])')

# Bare mode for CI (fastest startup)
claude --bare -p 'Run all tests' --allowedTools 'Read,Bash' --max-turns 10
```

### PTY Dialog Handling
Claude Code presents confirmation dialogs on first launch:
1. **Workspace Trust**: just press Enter (default is "Yes")
2. **Permissions Warning** (with `--dangerously-skip-permissions`): must press Down then Enter

### Key CLI Flags
| Flag | Effect |
|------|--------|
| `-p, --print` | Non-interactive one-shot mode |
| `-c, --continue` | Resume most recent conversation |
| `-r, --resume <id>` | Resume specific session |
| `--max-turns N` | Limit agentic loops (print mode) |
| `--max-budget-usd N` | Cap API spend |
| `--model <alias>` | sonnet, opus, haiku |
| `--effort <level>` | low, medium, high, max, auto |
| `--allowedTools <tools>` | Whitelist specific tools |
| `--dangerously-skip-permissions` | Auto-approve ALL tool use |
| `--bare` | Skip hooks, plugins, MCP, OAuth |
| `--output-format <fmt>` | text, json, stream-json |
| `--json-schema <schema>` | Force structured JSON output |
| `--fallback-model <model>` | Auto-fallback on overload |

### Hooks (Automation on Events)
Configure in `.claude/settings.json`:
- `PreToolUse` — before tool execution (security gates)
- `PostToolUse` — after tool finishes (auto-format, lint)
- `Stop` — when Claude finishes a response
- `SessionStart` — when a session begins

### MCP Integration
```bash
claude mcp add -s user github -- npx @modelcontextprotocol/server-github
claude mcp add -s local postgres -- npx @anthropic-ai/server-postgres --connection-string postgresql://localhost/mydb
```

### Cost Tips
- Use `--max-turns` to prevent runaway loops
- Use `--effort low` for simple tasks (faster, cheaper)
- Use `--bare` for CI to skip plugin/hook discovery
- Use `--model haiku` for simple tasks, `opus` for complex work
- Use `/compact` in interactive sessions when context gets large

---

## Codex — Detailed Reference

### Authentication
- `OPENAI_API_KEY` env var, or Codex OAuth from `~/.codex/auth.json`
- **Must run inside a git repository** — Codex refuses to run outside one
- **Always use `pty=true`** — Codex is an interactive terminal app

### Key Flags
| Flag | Effect |
|------|--------|
| `exec "prompt"` | One-shot execution, exits when done |
| `--full-auto` | Sandboxed, auto-approves file changes |
| `--yolo` | No sandbox, no approvals (fastest) |
| `--sandbox danger-full-access` | No Codex sandbox (for gateway contexts) |

### Gateway Caveat
In Hermes gateway/service contexts, Codex `workspace-write` sandboxing may fail with bubblewrap/user-namespace errors. Use `--sandbox danger-full-access` and rely on process boundaries as the safety layer.

### Scratch Work
```bash
cd $(mktemp -d) && git init && codex exec 'Build a snake game in Python'
```

---

## OpenCode — Detailed Reference

### Authentication
- `opencode auth login` or set provider env vars (OPENROUTER_API_KEY, etc.)
- Verify: `opencode auth list`

### One-Shot Tasks
```bash
opencode run 'Add retry logic' -f config.yaml -f .env.example
opencode run 'Debug CI failures' --thinking
opencode run 'Refactor auth' --model openrouter/anthropic/claude-sonnet-4
```

### Interactive TUI Keybindings
| Key | Action |
|-----|--------|
| `Enter` | Submit message |
| `Tab` | Switch agents (build/plan) |
| `Ctrl+P` | Command palette |
| `Ctrl+X M` | Switch model |
| `Ctrl+C` | Exit (NOT `/exit`) |

### Important: Do NOT use `/exit` — it opens an agent selector dialog. Use Ctrl+C or `process(action="kill")`.

### Session & Cost
```bash
opencode session list    # Past sessions
opencode stats           # Token usage and costs
```

### Binary Resolution
If behavior differs between terminal and Hermes, check `which -a opencode` and pin explicit path if needed.
