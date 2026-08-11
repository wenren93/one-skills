---
name: development-methodology
description: "Development methodology: planning, spike experiments, and test-driven development."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Planning, Spike, TDD, Testing, Methodology, Workflow, Development, Red-Green-Refactor]
    related_skills: [debugging, code-review, subagent-driven-development]
---

# Development Methodology

Three complementary approaches for structured software development: planning before building, spiking to validate unknowns, and test-driving implementation.

## Decision: Which Approach?

| Situation | Approach | Section |
|-----------|----------|---------|
| Multi-step feature or complex task | **Plan** — write an actionable implementation plan | [Plan Mode] |
| Unknown feasibility, need to validate an idea | **Spike** — throwaway experiment | [Spike] |
| Implementing any code (features, bugs, refactoring) | **TDD** — test-first red-green-refactor | [Test-Driven Development] |
| Complex feature with unknowns | **Spike → Plan → TDD** — validate, then plan, then implement | Combine all three |

**Typical flow:** Spike to validate unknowns → Plan the implementation → TDD each task

---

## Plan Mode

Use when the user wants a plan instead of execution. Write a concrete, actionable markdown plan.

### Core Rules
- **Do not implement code** — plan only
- Do not edit project files except the plan markdown file
- Deliverable: markdown plan saved under `.hermes/plans/`

### Output Requirements

Include when relevant:
- Goal
- Current context / assumptions
- Proposed approach
- Step-by-step plan
- Files likely to change
- Tests / validation
- Risks, tradeoffs, and open questions

### Save Location
```
.hermes/plans/YYYY-MM-DD_HHMMSS-<slug>.md
```

### Bite-Sized Task Granularity

**Each task = 2-5 minutes of focused work.** Every step is one action:
- "Write the failing test" — step
- "Run it to make sure it fails" — step
- "Implement the minimal code to make the test pass" — step
- "Run the tests and make sure they pass" — step
- "Commit" — step

### Task Structure

```markdown
### Task N: [Descriptive Name]

**Objective:** What this task accomplishes (one sentence)

**Files:**
- Create: `exact/path/to/new_file.py`
- Modify: `exact/path/to/existing.py:45-67`
- Test: `tests/path/to/test_file.py`

**Step 1: Write failing test**
[test code]

**Step 2: Run test to verify failure**
Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL

**Step 3: Write minimal implementation**
[code]

**Step 4: Run test to verify pass**
Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

**Step 5: Commit**
```

### Plan Review Checklist
- [ ] Tasks are sequential and logical
- [ ] Each task is bite-sized (2-5 min)
- [ ] File paths are exact
- [ ] Code examples are complete (copy-pasteable)
- [ ] Commands are exact with expected output
- [ ] DRY, YAGNI, TDD principles applied

### Principles
- **DRY**: Extract validation functions, reuse everywhere
- **YAGNI**: Implement only what's needed now
- **TDD**: Every code task includes the full red-green-refactor cycle
- **Frequent commits**: Commit after every task

---

## Spike

Use when the user wants to **validate feasibility** before committing to a real build. Spikes are disposable by design.

### Core Method
```
decompose → research → build → verdict
   ↑_________________________________↓
         iterate on findings
```

### 1. Decompose

Break the idea into 2-5 independent feasibility questions. Each is one spike:

| # | Spike | Validates | Risk |
|---|-------|-----------|------|
| 001 | websocket-streaming | WS connection streams tokens < 100ms | High |
| 002a | pdf-parse-pdfjs | pdfjs extracts structured text | Medium |
| 002b | pdf-parse-camelot | camelot extracts structured text | Medium |

**Spike types:**
- **standard** — one approach, one question
- **comparison** — same question, different approaches (002a/002b)

**Order by risk.** The spike most likely to kill the idea runs first.

### 2. Research (per spike)

- Brief it: 2-3 sentences on what and why
- Surface competing approaches with pros/cons
- Pick one and state why
- Skip research for pure logic with no external dependencies

### 3. Build

One directory per spike, standalone:
```
spikes/
├── 001-websocket-streaming/
│   ├── README.md
│   └── main.py
└── 002a-pdf-parse-pdfjs/
    ├── README.md
    └── parse.js
```

Bias toward something interactive: CLI > HTML page > web server > unit test.

**Depth over speed.** Never declare "it works" after one happy-path run.

### 4. Verdict

Each spike's README closes with:
```markdown
## Verdict: VALIDATED | PARTIAL | INVALIDATED

### What worked
- ...
### What didn't
- ...
### Surprises
- ...
### Recommendation for the real build
- ...
```

### Comparison Head-to-Head

```markdown
## Head-to-head: pdfjs vs camelot

| Dimension | pdfjs (002a) | camelot (002b) |
|-----------|--------------|----------------|
| Quality | 9/10 | 7/10 |
| Setup | npm, 1 line | pip + ghostscript |
| Perf | 3s | 18s |

**Winner:** pdfjs for our use case.
```

---

## Test-Driven Development (TDD)

Write the test first. Watch it fail. Write minimal code to pass.

### The Iron Law
```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Write code before the test? Delete it. Start over. No exceptions.

### Red-Green-Refactor Cycle

#### RED — Write Failing Test

One minimal test showing what should happen:
```python
def test_retries_failed_operations_3_times():
    attempts = 0
    def operation():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise Exception('fail')
        return 'success'
    result = retry_operation(operation)
    assert result == 'success'
    assert attempts == 3
```

Requirements:
- One behavior per test
- Clear descriptive name ("and" in name? Split it)
- Real code, not mocks (unless truly unavoidable)
- Name describes behavior, not implementation

#### Verify RED — Watch It Fail (MANDATORY)

```bash
pytest tests/test_feature.py::test_specific_behavior -v
```

Confirm: test fails (not errors from typos), failure message is expected, fails because feature is missing.

Test passes immediately? You're testing existing behavior. Fix the test.

#### GREEN — Minimal Code

Write the simplest code to pass. Nothing more. Cheating is OK: hardcode return values, copy-paste, duplicate code, skip edge cases. Fix in REFACTOR.

#### Verify GREEN — Watch It Pass (MANDATORY)

```bash
pytest tests/test_feature.py::test_specific_behavior -v
pytest tests/ -q  # Check for regressions
```

#### REFACTOR — Clean Up

After green only: remove duplication, improve names, extract helpers. Keep tests green throughout.

### Vertical Tracer Bullets (NOT Horizontal Slices)

```
WRONG:  RED: test1, test2, test3  →  GREEN: impl1, impl2, impl3
RIGHT:  RED→GREEN: test1→impl1  →  RED→GREEN: test2→impl2  →  RED→GREEN: test3→impl3
```

### Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Too simple to test" | Simple code breaks. Test takes 30 seconds. |
| "I'll test after" | Tests passing immediately prove nothing. |
| "Deleting X hours is wasteful" | Sunk cost fallacy. Keeping unverified code is debt. |
| "TDD will slow me down" | TDD faster than debugging. |
| "Need to explore first" | Fine. Throw away exploration, start with TDD. |

### Red Flags — STOP and Start Over

If you catch yourself doing any of these, delete the code and restart:
- Code before test
- Test passes immediately on first run
- Tests added "later"
- Rationalizing "just this once"
- "Keep as reference" or "adapt existing code"

### Verification Checklist

Before marking work complete:
- [ ] Every new function has a test
- [ ] Watched each test fail before implementing
- [ ] Wrote minimal code to pass each test
- [ ] All tests pass, output pristine
- [ ] Tests use real code (mocks only if unavoidable)
- [ ] Edge cases and errors covered

### When Stuck

| Problem | Solution |
|---------|----------|
| Don't know how to test | Write the wished-for API. Write the assertion first. |
| Test too complicated | Design too complicated. Simplify the interface. |
| Must mock everything | Code too coupled. Use dependency injection. |
| Test setup huge | Extract helpers. Still complex? Simplify the design. |

---

## Combining Approaches

### For Complex Features with Unknowns
1. **Spike** the risky parts first (validate feasibility)
2. **Plan** the implementation (break into bite-sized tasks)
3. **TDD** each task (red-green-refactor per task)

### For Simple Features
1. **Plan** if multi-step (skip if single task)
2. **TDD** the implementation
### For Bug Fixes

1. Write failing test reproducing the bug (TDD)
2. Fix the code
3. Verify test passes

---

## Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

### Branch

- **"Does this logic / state model feel right?"** → Build a single shareable HTML file with free-play buttons + tabbed guided walkthroughs that pushes the state machine through hard-to-reason-about cases.
- **"What should this look like?"** → Generate several radically different UI variations on a single route, switchable via URL search param and floating bottom bar.

### Rules

1. **Throwaway from day one, clearly marked.** Name it so a casual reader can see it's a prototype, not production.
2. **Trivial to run.** One command in the project's task runner. No thinking required.
3. **No persistence by default.** State lives in memory. Persistence is what the prototype is checking.
4. **Skip the polish.** No tests, no error handling beyond runnable, no abstractions.
5. **Surface the state.** After every action, print or render full relevant state.
6. **Capture when done.** Fold validated decisions into real code, commit prototype to throwaway branch, leave context pointer on the implementation issue.
