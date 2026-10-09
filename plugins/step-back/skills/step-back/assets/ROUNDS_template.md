# Rounds log — <project>

One file per project (default `docs/ROUNDS.md`). One section per track: a single step or problem
that goes through several rounds. Whoever accepts a round adds its row.

## Track: <short track name>
Output: <what the step produces; where the records live, e.g. out/summaries/*.json>
Gates: <name>=<oracle|reference|model>; <name>=<...>
Budget: 2

| r | gate | result | measure | kind | note |
|---|---|---|---|---|---|
| 1 | <name> | NO | 14 | C | <what changed> |

Fields:
- **Gates** — who gives the verdict:
  - `oracle` — a test, an execution, a checksum, a comparison with a database;
  - `reference` — a model or rule checked against a human-approved set, or a human decision;
  - `model` — a model with no reference set.
- **result** — `PASS` or `NO`. Each gate in a round is its own row with the same `r`.
- **measure** — number of problems the gate found this round (lower is better); the first number in
  the cell. Always count in the same unit as earlier rounds of that gate — switching units (e.g. from
  "defects in screenshots" to "red tests") makes it a new gate; otherwise a drop is illusory.
- **kind** — what changed this round:
  - `C` — control (rule, judge, guard, limit);
  - `O` — output;
  - `M` — measurement;
  - `R` — removal;
  - `X` — decision after a step-back review (counting starts again from this round).
