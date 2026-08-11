---
name: spec-and-tickets
description: "Turn conversations into specs and break specs into tracer-bullet tickets. Use when the user wants to formalize discussion into a spec or decompose work into trackable tickets."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [spec, tickets, planning, issue-tracker, workflow]
    category: software-development
disable-model-invocation: true
---

# Spec and Tickets

Two sequential workflows: (1) synthesize the current conversation into a spec, then (2) break the spec into tracer-bullet tickets with blocking edges.

The issue tracker and triage label vocabulary should have been provided — run `/setup-matt-pocock-skills` if not.

---

## Part 1: To Spec

Turn the current conversation into a spec and publish it to the issue tracker. No interview — just synthesize what you already know.

### Process

1. **Explore the repo** to understand current state. Use the project's domain glossary throughout, respect ADRs.

2. **Sketch the seams** at which you'll test the feature. Prefer existing seams over new ones. Use the highest seam possible. The fewer seams, the better — ideal is one. Check with the user.

3. **Write the spec** using the template below, then publish to the issue tracker. Apply the `ready-for-agent` label.

### Spec Template

```markdown
## Problem Statement
The problem from the user's perspective.

## Solution
The solution from the user's perspective.

## User Stories
1. As an <actor>, I want a <feature>, so that <benefit>
[... extensive, numbered list covering all aspects]

## Implementation Decisions
- Modules to build/modify
- Interface changes
- Technical clarifications
- Architectural decisions
- Schema changes, API contracts
[No specific file paths or code snippets — they go stale fast.
Exception: decision-rich snippets from prototypes (state machines, schemas).]

## Testing Decisions
- What makes a good test
- Which modules to test
- Prior art for similar tests

## Out of Scope
What's explicitly excluded.

## Further Notes
Any additional context.
```

---

## Part 2: To Tickets

Break a spec (or the current conversation) into tracer-bullet tickets with blocking edges.

### Process

1. **Gather context** from the conversation. If the user passes a reference (spec path, issue number), fetch and read it.

2. **Explore the codebase** (optional). Use domain glossary vocabulary, respect ADRs. Look for prefactoring opportunities.

3. **Draft vertical slices.** Each slice:
   - Cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests)
   - Is demoable/verifiable on its own
   - Fits in a single fresh context window
   - Has blocking edges (which tickets must complete first)

4. **Quiz the user.** Present as numbered list showing title, blocked-by, and what it delivers. Ask about granularity, blocking edges, and whether to merge/split.

5. **Publish tickets** to the configured tracker:
   - **Local files**: one file per ticket under `.scratch/<feature-slug>/issues/<NN>-<slug>.md`
   - **Real tracker**: one issue per ticket in dependency order, with native blocking links

### Wide Refactors (Exception to Vertical Slicing)

For mechanical changes with large blast radius (rename a column, retype a shared symbol):
- **Expand**: add new form beside old (nothing breaks)
- **Migrate**: batch call sites by blast radius, each batch its own ticket
- **Contract**: delete old form once no caller remains

### Ticket Template (Local Files)

```markdown
# <NN> — <Ticket title>

**What to build:** end-to-end behaviour from user's perspective.

**Blocked by:** ticket numbers/titles, or "None — can start immediately".

**Status:** ready-for-agent

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2
```
