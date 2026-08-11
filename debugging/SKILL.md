---
name: debugging
description: "Debugging methodology and language-specific debugger tools (Python pdb/debugpy, Node.js inspect/CDP)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, troubleshooting, root-cause, python, nodejs, pdb, debugpy, breakpoints, cdp]
    related_skills: [test-driven-development, plan]
---

# Debugging

Two layers: the **methodology** (how to think) and the **tools** (how to inspect). Always start with the methodology; reach for language-specific tools when `print()` isn't enough.

---

## Part 1: Systematic Debugging Methodology

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

### The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read error messages carefully** — don't skip past errors. Read stack traces completely. Note line numbers, file paths, error codes.

2. **Reproduce consistently** — can you trigger it reliably? What are exact steps? If not reproducible → gather more data, don't guess.

3. **Check recent changes** — `git log --oneline -10`, `git diff`, recent commits, new dependencies.

4. **Gather evidence in multi-component systems** — for each component boundary: log what data enters/exits, verify config propagation, check state at each layer.

5. **Trace data flow** — where does the bad value originate? Keep tracing upstream until you find the source. Fix at the source, not at the symptom.

**STOP:** Do not proceed until you understand WHY it's happening.

### Phase 2: Pattern Analysis

1. Find similar working code in the same codebase
2. Compare against reference implementations (read COMPLETELY)
3. Identify every difference between working and broken
4. Understand dependencies and assumptions

### Phase 3: Hypothesis and Testing

1. Form a single hypothesis: "I think X is the root cause because Y"
2. Make the SMALLEST possible change to test it
3. One variable at a time
4. Didn't work? Form NEW hypothesis. DON'T add more fixes on top.

### Phase 4: Implementation

1. Create a failing test case (MUST have before fixing)
2. Implement single fix — ONE change, no bundled refactoring
3. Verify: run regression test + full suite
4. **Rule of Three:** If ≥ 3 fixes failed → STOP and question the architecture. Discuss with user.

### Red Flags — STOP and Return to Phase 1

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "I don't fully understand but this might work"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when already tried 2+)
- Each fix reveals a new problem in a different place

---

## Part 2: Python Debugging (pdb + debugpy)

Three tools, picked by situation:

| Tool | When |
|---|---|
| `breakpoint()` + pdb | Local, interactive, simplest. Add `breakpoint()` in source, run normally. |
| `python -m pdb` | Launch existing script under pdb with no source edits. |
| `debugpy` | Remote / headless / attach to already-running process. |

### pdb Quick Reference

| Command | Action |
|---|---|
| `n` | next line (step over) |
| `s` | step into |
| `r` | return from current function |
| `c` | continue |
| `w` | where (stack trace) |
| `u` / `d` | up / down in stack |
| `p expr` / `pp expr` | print / pretty-print |
| `b file:line` | set breakpoint |
| `b func` | break on function entry |
| `cl N` | clear breakpoint N |
| `!stmt` | execute arbitrary Python |
| `interact` | full Python REPL in current scope |
| `q` | quit |

### Recipe: Local breakpoint

```python
def compute(x, y):
    result = some_helper(x)
    breakpoint()           # <-- drops into pdb here
    return result + y
```

Don't forget to remove before committing: `rg -n 'breakpoint\(\)' --type py`

### Recipe: Debug a pytest test

```bash
# pdb under xdist doesn't work — add -p no:xdist
python -m pytest tests/foo_test.py::test_bar --pdb -p no:xdist
```

### Recipe: Post-mortem on any exception

```bash
python -m pdb -c continue script.py
# When it crashes, pdb catches it at the frame of the exception
```

### Recipe: Remote debug with debugpy

```python
import debugpy
debugpy.listen(("127.0.0.1", 5678))
debugpy.wait_for_client()  # blocks until debugger attaches
```

Or launch without source edit: `python -m debugpy --listen 127.0.0.1:5678 --wait-for-client your_script.py`

Or attach to running process: `python -m debugpy --listen 127.0.0.1:5678 --pid <pid>`

**Terminal-side:** Use `remote-pdb` for agent-friendly debugging:
```python
from remote_pdb import set_trace
set_trace(host="127.0.0.1", port=4444)
# Then: nc 127.0.0.1 4444 → get (Pdb) prompt
```

### Python Pitfalls

1. **pdb under pytest-xdist silently does nothing.** Always use `-p no:xdist` or `-n 0`.
2. **`breakpoint()` in CI / non-TTY hangs the process.** Never commit it.
3. **`PYTHONBREAKPOINT=0`** disables all `breakpoint()` calls.
4. **Attach to PID fails on hardened kernels.** `echo 0 > /proc/sys/kernel/yama/ptrace_scope` or launch under debugpy.
5. **pdb only debugs current thread.** For multithreaded code, use debugpy.

---

## Part 3: Node.js Debugging (inspect + CDP)

Two tools:

| Tool | When |
|---|---|
| `node inspect` | Built-in, zero install, CLI REPL. Best for quick poking. |
| CDP via `chrome-remote-interface` | Scriptable from Node. Best for automation. |

### `node inspect` Quick Reference

```bash
node inspect path/to/script.js
# or with tsx:
node --inspect-brk $(which tsx) path/to/script.ts
```

| Command | Action |
|---|---|
| `c` / `cont` | continue |
| `n` / `next` | step over |
| `s` / `step` | step into |
| `o` / `out` | step out |
| `sb('file.js', 42)` | set breakpoint at file:line |
| `sb('functionName')` | break on function call |
| `bt` | backtrace (call stack) |
| `repl` | drop into REPL in current scope |
| `exec expr` | evaluate expression |
| `pause` | pause running code |

### Attaching to a Running Process

```bash
# 1. Send SIGUSR1 to enable inspector
kill -SIGUSR1 <pid>

# 2. Attach
node inspect -p <pid>
```

### Start with Inspector

```bash
node --inspect script.js           # listen, keep running
node --inspect-brk script.js       # listen AND pause on first line
```

### Node Pitfalls

1. **Wrong line numbers in TS source.** Breakpoints hit emitted JS. Use `node --enable-source-maps` or break in `dist/*.js`.
2. **`--inspect` vs `--inspect-brk`.** `--inspect` doesn't pause; your script races past breakpoints. Use `--inspect-brk` when you need to set breakpoints first.
3. **Port collisions.** Default 9229. Use `--inspect=0` for random port.
4. **Child processes** aren't auto-inspected. Use `NODE_OPTIONS='--inspect-brk'` to propagate.
