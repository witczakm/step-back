# For executor briefs (Claude Code, Codex, any agent)

## At the start of a new track — 3 lines (copy them into docs/ROUNDS.md too)
Output: <what the step should produce; one example record>
Gates: <who decides it is right: oracle | reference | model>   <- a model with no reference set: build one first, or use a third state
Budget: 2 rounds for this gate; after that a step-back review, not another rule

## At the end of the brief — required last line of the report
End your report with one line per gate:
ROUND <n> | <gate> | <PASS/NO> | <number of problems> | <C/O/M/R> | <what changed, one sentence>
Report the gate result from the FULL run, not from a subset of tests.

## In every review request (reviewer, another model)
Besides "is this correct?", answer: should this mechanism exist at all?
What would have to be removed, or changed in what the step produces, so that this class of defects cannot arise?
