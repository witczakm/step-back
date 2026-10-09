# Evals

Small and transparent. This is not a benchmark, and the numbers below are not proof that the skill
works in your setting. Treat them as a sanity check.

## TL;DR

| Check | n | Result | What it shows |
|---|---|---|---|
| Signals backtest | 12 cases × EN + PL × 2 editions (+2 missing-log checks) | 50 / 50 | the deterministic part does what it says on cases written for it |
| Blind runs, with vs without the skill | 3 tasks, 1 run each | 12 / 12 vs 7 / 12 criteria | the procedure steers toward removing or changing the step, away from another controller |
| End to end through the installed plugin | 2 runs | OK in one line; ALARM with an exact-format card | `context: fork`, the pre-executed signals line and the card format work in Claude Code |
| Auto-trigger | 18 prompts × 2 runs, per language | recall 2 / 9 (EN), 3 / 9 (PL); false triggers 0 / 9 | do not rely on unprompted triggering; invoke it at acceptance |

## 1. Signals backtest

`python3 tests/run_tests.py` runs every case in `tests/cases/{en,pl}` through both editions' copy of
`signals.py` and compares the status with `tests/expected.json`.

| Case | Origin | Expected |
|---|---|---|
| P1 quote judge, after round 2 | real loop (9 rounds), anonymised | ALARM (A) |
| P2 model checks model, after round 2 | real loop (36 rounds), anonymised | ALARM (A) |
| P3 copy guard: oracle PASS, model review NO | real loop (10 rounds), anonymised | ALARM (A) + note |
| P4 screenshot scenario, 3 identical failures | real, anonymised | ALARM (B) |
| P5 alarm after an earlier step-back | invented | ESCALATE |
| N1 test suite 44 → 43 → 1 | real, anonymised | OK |
| N2 screen prototype 7 → 2 → 0 | real, anonymised | OK |
| N3 deploy dry run 1 → 4 → 1 → 0 | real, anonymised (a hard negative: the trial itself had defects but converged) | OK |
| N4 refactor 12 → 3 → 0 | invented | OK |
| N5 judge with a reference set 9 → 6 → 3 → PASS | invented | OK |
| U1 quote judge after round 1 | real, truncated | NOTE (unanchored model gate) |
| U2 log without a track contract | invented | NOTE |

**Caveat:** the rules were derived from P1–P3 and the same day's negatives. Overfitting is likely.
Loops from other projects are the most useful contribution.

## 2. Blind runs (with vs without the skill)

Separate agents worked on copies of three small projects. Each copy had a rounds log and real-looking
records. The task was a realistic user message. Graded on four criteria per task. See
[`docs/evidence/blind-runs-benchmark.md`](docs/evidence/blind-runs-benchmark.md).

| Task | With skill | Without | Notes |
|---|---|---|---|
| Quote judge, about to add "two model families must agree" | 4 / 4 | 3 / 4 | both advised against the new rule. The baseline was good but had no card format |
| Copy guard, about to commission round 8 (system lock) | 4 / 4 | 1 / 4 | **baseline proposed a better lock and more tests, i.e. another controller**. With the skill: remove the per-release copy |
| Converging prototype, "step back and check" | 4 / 4 | 3 / 4 | skill answered in 3 lines. The baseline proposed another verification round, but it also spotted a unit inconsistency in the log. That became a template rule ("a new unit is a new gate") |

**Caveats:** one run per task; graded by the author, not an independent grader. One criterion
(card format) favours the skill by construction. All runs were single-family (no external models
available).

## 3. End to end through the plugin

Installed with `claude plugin install step-back@step-back` from a local marketplace, then run with
`claude -p "/step-back:step-back"`:
- converging log → [one line](docs/evidence/e2e-ok-oneliner.txt);
- copy-guard log with a script and a log file as records → [ALARM card](docs/evidence/e2e-alarm-card.txt)
  in the exact format. The card spotted that the log listed 2 rounds while the code comments showed 8.

The first ALARM run exposed a defect: in non-interactive mode the subagent could not read the card
template from the plugin cache. The fix was to inline the template in `SKILL.md` rather than add a
permission.

## 4. Auto-trigger

Run with skill-creator's `run_eval` on 18 realistic prompts (9 should trigger, 9 near-misses), two runs
each, per language.

| Description | Recall (should trigger) | False triggers |
|---|---|---|
| Polish, first version | 2 / 9 | 0 / 9 |
| Polish, rewritten | 3 / 9 | 0 / 9 |
| English | 2 / 9 | 0 / 9 |

Rewriting the Polish description moved recall by one prompt; after two rounds on the description,
tuning stopped there, by the skill's own two-round rule. The design does not depend on unprompted triggering: you invoke it at acceptance.
**A measurement defect worth knowing about:** the first English run scored 0 / 9 because the
plugin was also installed globally, and the model called that copy instead of the one under test.
After uninstalling it, the score was 2 / 9. Prompts:
[`trigger-prompts-en.json`](docs/evidence/trigger-prompts-en.json),
[`trigger-prompts-pl.json`](docs/evidence/trigger-prompts-pl.json).

## What this is not

- Not a measure of decision quality over time. Nobody has yet tracked whether the recommended changes
  held up weeks later.
- Not independent. The author designed, ran and graded the checks.
- Not cross-model. The 3-family alternatives path has not been exercised end to end.
