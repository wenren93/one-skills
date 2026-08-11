---
name: codebase-architecture
description: "Design deep modules, scan for architectural improvements, and maintain domain models. Use when designing interfaces, finding deepening opportunities, or pinning down domain terminology."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [architecture, design, modules, seams, domain-model, codebase, refactoring]
    category: software-development
---

# Codebase Architecture

Three complementary disciplines for structuring code: a shared vocabulary for deep modules, a process for finding deepening opportunities, and a method for maintaining domain models.

## Decision: Which Discipline?

| Situation | Section |
|-----------|---------|
| Designing or improving a module's interface | [Deep Module Vocabulary] |
| Scanning a codebase for refactoring opportunities | [Architecture Review] |
| Pinning down domain terminology or recording ADRs | [Domain Modeling] |

**Typical flow:** Use the vocabulary to design → scan for opportunities → maintain the domain model as you go.

---

## Deep Module Vocabulary

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface.

### Glossary (use these terms exactly)

- **Module** — anything with an interface and implementation (function, class, package). Avoid: component, service.
- **Interface** — everything a caller must know: type signature, invariants, ordering constraints, error modes. Avoid: API (too narrow).
- **Depth** — leverage at the interface: behaviour exercised per unit of interface learned. Deep = small interface + lots of implementation.
- **Seam** — where you can alter behaviour without editing in that place. Avoid: boundary (overloaded with DDD).
- **Adapter** — a concrete thing satisfying an interface at a seam.
- **Leverage** — what callers get from depth: more capability per unit of interface.
- **Locality** — what maintainers get from depth: change/bugs/verification concentrate in one place.

### Principles

- Depth is a property of the interface, not the implementation.
- **The deletion test.** Delete the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.** Callers and tests cross the same seam.
- **One adapter = hypothetical seam. Two = real seam.** Don't introduce a seam unless something varies across it.

### Testability Patterns

1. Accept dependencies, don't create them
2. Return results, don't produce side effects
3. Small surface area = fewer tests needed

### Going Deeper

- **Deepening a cluster** — see `references/DEEPENING.md`: dependency categories, seam discipline, replace-don't-layer testing.
- **Design it twice** — see `references/DESIGN-IT-TWICE.md`: spin up parallel sub-agents to design the interface several radically different ways, then compare.

---

## Architecture Review

Surface architectural friction and propose deepening opportunities — refactors that turn shallow modules into deep ones.

### Process

1. **Explore** — scope before you scan. Walk the commit history for hot spots. Read `CONTEXT.md` and ADRs first. Note where you experience friction:
   - Where does understanding one concept require bouncing between many small modules?
   - Where are modules shallow (interface nearly as complex as implementation)?
   - Where have pure functions been extracted just for testability but bugs hide in how they're called?

2. **Present as HTML report** — write to `<tmpdir>/architecture-review-<timestamp>.html`. Each candidate gets: files, problem, solution, benefits, before/after diagram, recommendation strength. Use Tailwind + Mermaid via CDN.

3. **Grilling loop** — once the user picks a candidate, run `/grilling` to walk the decision tree. Update `CONTEXT.md` inline as terms resolve.

### See Also

- `references/HTML-REPORT.md` — full HTML scaffold, diagram patterns, styling guidance.

---

## Domain Modeling

Actively build and sharpen the project's domain model as you design.

### File Structure

```
/CONTEXT.md              ← domain glossary
/docs/adr/               ← architectural decision records
```

For multi-context repos: `CONTEXT-MAP.md` at root points to per-context `CONTEXT.md` files.

### During the Session

- **Challenge against the glossary.** When a term conflicts with `CONTEXT.md`, call it out.
- **Sharpen fuzzy language.** Propose precise canonical terms for vague/overloaded terms.
- **Discuss concrete scenarios.** Stress-test domain relationships with specific edge cases.
- **Cross-reference with code.** If the user says X but code does Y, surface the contradiction.
- **Update `CONTEXT.md` inline.** Don't batch — capture terms as they resolve.

### ADR Rules

Only offer an ADR when ALL three are true:
1. **Hard to reverse** — meaningful cost to change later
2. **Surprising without context** — future reader will wonder "why?"
3. **Real trade-off** — genuine alternatives existed

### See Also

- `references/ADR-FORMAT.md` — ADR template
- `references/CONTEXT-FORMAT.md` — glossary format
