# Technical article archetypes

Choose one primary archetype. A secondary archetype may supply a section, but
must not compete for the main line.

## Engineering practice or retrospective

Use for a real project, migration, incident, implementation, or team process.

```text
context and constraints
→ failure or friction
→ decision criteria
→ implementation
→ measured result
→ what failed or changed
→ transferable lessons and limits
```

Evidence should include project artifacts, measurements, screenshots, code, or
a clear record of the author's involvement.

## Source code or architecture deep dive

Use for a repository, framework, runtime path, protocol, or system design.

```text
problem the system solves
→ whole-system map
→ one representative execution path
→ key components and invariants
→ design tradeoffs
→ failure and extension points
→ what readers can reuse
```

Anchor explanations to concrete files, symbols, messages, or diagrams. Avoid a
directory-by-directory tour with no organizing question.

## Tool or product evaluation

Use when the author has actually operated the product or can run a reproducible
test.

```text
task and evaluation dimensions
→ environment and procedure
→ test cases shown one by one
→ results and evidence
→ strengths, failures, and comparison
→ suitable and unsuitable users
```

Use the same dimensions for every compared option. Do not change the standard
to create a more dramatic ranking.

## Tutorial or methodology

Use for a reproducible workflow, guide, checklist, or operating method.

```text
goal and finished result
→ prerequisites and boundary
→ steps with verification points
→ common failures and recovery
→ why the method works
→ condensed checklist
```

Every major section should leave the reader with an executable action. State
the learning curve and the cases where the method is a poor fit.

## Trend or phenomenon analysis

Use for a current technical change, industry pattern, or repeated observation.

```text
observable phenomenon
→ why the surface explanation is insufficient
→ evidence from multiple perspectives
→ mechanism or structural cause
→ Leslie's judgment
→ uncertainties and signals to watch
```

Separate reporting from prediction. Time-sensitive facts require current,
authoritative sources.

## Comparative research

Use for multiple systems, agents, models, libraries, or design strategies.

```text
shared question
→ comparison dimensions and constraints
→ each option shown with the same template
→ cross-option synthesis
→ decision matrix
→ recommendation by scenario
```

Preserve experimental conditions and disclose missing data. “Best” without a
defined scenario is not a useful conclusion.

