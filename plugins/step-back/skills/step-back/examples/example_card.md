(Illustrative example — anonymised case, numbers for illustration.)

STEP BACK — importer copy guard — 2026-10-09 — after round 2
Models: DEGRADED: one model family | calls: 0/5
Signals: ALARM — A: gate "model-review" (model, no reference set) said NO in rounds 1 and 2; oracle "stub-tests" PASS -> model findings do not block
What the step produces (based on 12 records): on every new release a script extracts a copy of the importer code for that commit from the repository. Once the copy was incomplete and the job wrote nothing for a day. Every later mechanism (trial import, dependency list, hand-made lock, timeout) guards that copy.
Common denominator: output defects 1 | controller 6 | measurement 1 -> the problem is the mechanism guarding the copy, not the importer.
Verdict given by: technical truth with an oracle (stub tests, 113/0) -> reference set not needed; the NO comes from model reviews
Alternatives:
| rung | proposal | cost | risk |
| 1 remove the step | stop extracting a per-release copy; install the importer with the application in one fixed directory | ~2 days | an importer fix needs an application deploy |
| 2 change the output | the copy as a packaged, checksummed build artifact | 3 days | still two sources of truth |
| 3 check at the source | trial import inside the deploy script | 0.5 day | — (adds to 1) |
| 4 third state | review findings go to a decision list, no new round | 0 | findings may wait |
| 5 better controller (still a controller) | a system lock instead of the hand-made one | 0.5 day | edge cases remain |
RECOMMENDATION: rungs 1 + 3 — remove the per-release copy; trial import in the deploy script; a silence alarm after 3 h without a successful import.
Net line: control mechanisms 6 -> 2 (system lock, silence alarm)
First step and measure: on a branch; 3 trial deploys with trial import 3/3   Failure criterion after 2 rounds: trial import fails in 2 consecutive deploys
Control method: the same 15 test files through the old and the new job; number of database differences = 0
Adversary's attack: "go straight to a job queue in the database" — kept as a later step, when volume grows
What would change the recommendation: a requirement to fix the importer without deploying the whole application
What we don't know: migration time on real data
Human decision: [ ] accept  [ ] otherwise: ______   -> row of kind X in the log
