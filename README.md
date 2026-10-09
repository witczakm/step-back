# step-back

> **Stop patching the patch.** A frame review for AI-agent work that goes in circles.
>
> When your agent keeps adding judges, guards, rules and exceptions to a step that keeps failing,
> `step-back` makes it look at **what the step produces** — and change that, or remove the step.
>
> 🇵🇱 Wersja polska: **[README.pl.md](README.pl.md)** (skill `krok-wstecz`)

[![Version](https://img.shields.io/badge/version-0.1.0-blue)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platforms](https://img.shields.io/badge/platforms-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Claude%20app-orange)](#install)
[![Format](https://img.shields.io/badge/format-Agent%20Skills-blueviolet)](https://agentskills.io)
[![Status](https://img.shields.io/badge/status-experimental-lightgrey)](EVALS.md)
[![test](https://github.com/witczakm/step-back/actions/workflows/test.yml/badge.svg)](.github/workflows/test.yml)

<details>
<summary><b>Contents</b></summary>

- [The loop it breaks](#the-loop-it-breaks)
- [Quick start](#quick-start)
- [A worked example](#a-worked-example)
- [How it works](#how-it-works)
- [Is it for you?](#is-it-for-you)
- [Install](#install)
- [The rounds log](#the-rounds-log)
- [Wiring it into your workflow](#wiring-it-into-your-workflow)
- [Privacy and safety](#privacy-and-safety)
- [Limitations](#limitations)
- [Evidence](#evidence)
- [Prior art and credits](#prior-art-and-credits)
- [Contributing and license](#contributing-and-license)

</details>

---

## The loop it breaks

```
round 1   the judge says NO        →  add a rule
round 2   the judge says NO        →  add an exception to the rule
round 3   review finds a hole      →  add a second judge to vote
round 4   the two judges disagree  →  add a tie-break rule
   …      every round is reasonable on its own; together they never converge
```

Everyone in the loop — the executor, the reviewer, the lead — looks at the newest version of the
control mechanism and asks *“does it work?”*. Nobody asks *“should it exist?”* or *“what does this
step actually produce?”*. `step-back` fills that empty seat.

It was built after one working day with three such loops in a real AI-agent project
(9, 36 and 10 rounds). None of them was closed by a better controller. One closed when a human
narrowed what counts as true, one when the step was removed, and one when the thing being guarded was deleted.

## Quick start

In Claude Code:

```text
/plugin marketplace add witczakm/step-back
/plugin install step-back@step-back        # English edition
```

Create `docs/ROUNDS.md` in your project. One section per *track* (a step that goes through several rounds), three header lines, one row per round:

```markdown
## Track: evidence check
Output: quote from the source document + verdict (records: out/verdicts.jsonl)
Gates: judge=model
Budget: 2
| r | gate | result | measure | kind | note |
|---|---|---|---|---|---|
| 1 | judge | NO | 14 | C | added a numeric-claim rule |
| 2 | judge | NO | 5  | C | added a proper-noun rule |
```

After each accepted round, run:

```text
/step-back:step-back
```

The signals are counted first, without a model. For the log above:

```text
ALARM     | evidence check | rounds: 2
          - A: gate "judge" (model, no reference set) said NO in rounds 1 and 2
```

On ALARM the review runs in a fresh context and returns a one-page decision card: what the step
really produces, five alternatives, one recommendation and a box for your decision
([a full real card](docs/evidence/e2e-alarm-card.txt)). On a converging track you get
[one line](docs/evidence/e2e-ok-oneliner.txt) and nothing else.

## A worked example

An importer ran every minute. To match the deployed version, a script extracted a **per-release copy**
of the importer from the repository. One day the copy was incomplete and nothing was imported for 24 hours.

What followed was ten rounds of hardening the *guard around the copy*: a trial load, a dependency list,
a hand-made lock (four rounds of lock bugs), a custom timeout, child-process handling. Every review
found a new edge case **in the guard itself**. The tests passed; only model reviewers kept saying NO.

`step-back` raises an alarm after the second of those rounds (signal A: a model gate with no reference
set said NO twice), notes that the oracle passes, and walks the ladder from the top:
**remove the step**. The importer ships with the application; the copy, its checks and its lock disappear.
The mechanism count goes from five or six to two (a system lock and a “no import for 3 hours” alarm).

## How it works

```
BRIEF (before round 1)          ROUND REPORT (executor)                 THRESHOLD
Output: what the step makes     ROUND n | gate | PASS/NO |              signals.py (no model):
Gates:  who decides             #problems | C/O/M/R                     OK · NOTE · ALARM · ESCALATE
Budget: 2 rounds                                                               │ ALARM
                                                                               ▼
                         /step-back — fresh-context subagent → one-page card → a human decides
```

**1 · Signals are counted, not felt.** A small standard-library script reads the log:

| Signal | Fires when | Why |
|---|---|---|
| **A** | a gate of type `model` (no human-approved reference set) said NO in its two latest rounds | the yardstick moves with every fix, so “progress” is not measurable |
| **B** | rounds exceed the budget, the gate still says NO, and its problem count did not drop | the budget is spent without convergence |

A previous step-back on the same track turns a new alarm into **ESCALATE**: a human decides; the skill
does not review itself in circles. The design rests on one observation: *activity is not progress*. By construction, a circuit breaker that counts file changes would not have fired on any of the three
original loops, because every round changed files.

**2 · Who gives the verdict decides whether you need a reference set.**

| Who decides | Reference set from a human? | Consequence |
|---|---|---|
| Oracle — test, execution, checksum | no | only check the oracle tests what changed |
| Convention or taste — summary, style, naming | no, and no model checker either | mechanical checks, or drop the controller |
| Factual truth — does the evidence prove the claim | yes, 20–60 cases, part frozen | until then a third state “for human decision”, not another rule |

When an oracle says PASS and the NO comes from a model reviewer, the model's findings **do not block**.

**3 · The review runs in a fresh context** (`context: fork`): it knows the log and the real records, not
the session's reasoning. It reads 10–20 actual records of the step's output first. In one of the original
loops the root cause was a plain bug (batches above number 99 silently skipped), visible only in the records.

**4 · Alternatives come from a ladder, top first:**

1. **Remove the step**, after checking why it exists (Chesterton's fence).
2. **Change what the step produces**: fields instead of prose, a full sentence instead of a fragment.
3. **Move the check to the source**, so the defect cannot arise (poka-yoke).
4. **A third state instead of a verdict**: “for human decision”. These decisions become your reference set.
5. **A better controller**, last, and labelled *“still a controller”*.

**5 · One recommendation on one page.** It comes with a control method (same sample, second method,
one number), a failure criterion after two rounds, and *what would change the recommendation*. External
models are optional, with a budget of at most 5 calls per use. No model is allowed to decide what is true.

## Is it for you?

✅ You run multi-round work with AI agents: you brief, they deliver, someone reviews.  
✅ You use models to judge or check other models, or you keep guards and validators around flaky steps.  
✅ You have caught yourself writing “one more exception” for the third time.

❌ One-off tasks, or quick bug fixes with a clear cause.  
❌ Rounds that already converge. The skill will tell you so in one line and stop.  
❌ You want an automatic gate that blocks merges. This skill is advisory by design.

## Install

### Claude Code: plugin (recommended)

```text
/plugin marketplace add witczakm/step-back
/plugin install step-back@step-back        # English
/plugin install krok-wstecz@step-back      # Polish
```

Plugin skills are namespaced, so the command is `/step-back:step-back` (or `/krok-wstecz:krok-wstecz`).

<details>
<summary><b>Claude Code and Codex: install script (no network, backs up existing installs)</b></summary>

```bash
git clone https://github.com/witczakm/step-back.git
cd step-back
./install.sh                 # English into ~/.claude/skills and ~/.codex/skills
./install.sh --lang pl       # Polish edition (krok-wstecz)
./install.sh --dry-run       # preview only
```

Installed this way, the command is simply `/step-back`. Requires `python3`.
</details>

<details>
<summary><b>Claude app (web, desktop): upload a zip</b></summary>

Download `dist/step-back-en.zip` (or `dist/krok-wstecz-pl.zip`) and add it under
Customize → Skills. In the app there is no forked context or pre-executed command: the skill runs the
signals script itself and works in the main conversation. See [Limitations](#limitations).
</details>

## The rounds log

One Markdown file per project: `docs/ROUNDS.md` (English keywords) or `docs/RUNDY.md` (Polish). Both
are accepted. Full template: [`assets/ROUNDS_template.md`](plugins/step-back/skills/step-back/assets/ROUNDS_template.md).

| Field | Values |
|---|---|
| `Gates:` | `name=oracle` · `name=reference` · `name=model` |
| `result` | `PASS` / `NO`. Each gate in a round is its own row. |
| `measure` | problems found this round (lower is better). Keep the same unit; a new unit means a new gate. |
| `kind` | `C` control · `O` output · `M` measurement · `R` removal · `X` decision after a step-back |

## Wiring it into your workflow

The skill works best at three points you already have. The ready-made lines are in
[`snippets/`](plugins/step-back/skills/step-back/snippets/):

- **Brief:** the three track lines, plus a required last line in every executor report:
  `ROUND n | gate | PASS/NO | #problems | C/O/M/R`.
- **Review requests:** add *“should this mechanism exist at all, and what would we remove so this class
  of defects cannot arise?”*.
- **Acceptance:** add the row, run `/step-back` (`/step-back:step-back` if installed as a plugin).
  ALARM: act on the card. ESCALATE: a human decides.

Paste `CLAUDE.md.snippet` into your `CLAUDE.md` and `AGENTS.md.snippet` into Codex's `AGENTS.md` if you
want the agents to keep the log for you.

## Privacy and safety

- `signals.py` uses only the Python standard library. **No network, no telemetry**, always exit code 0.
- The review reads files in your repository (the log and the records named in `Output:`). Keep secrets
  out of both.
- It calls other model families **only if you already have such a tool** (a second agent CLI or a
  consensus script), within a budget of 5 calls and subject to your normal permission prompts. Otherwise the card says `DEGRADED: one model family`.
  Whatever you would not send to a cloud model, do not point it at.
- It never blocks, edits code or commits. It issues a card; you decide.

## Limitations

- **Small evidence base.** The signals were derived from one project's real loops and tested on 12 cases
  (5 loops, 5 converging tracks, 2 early-warning cases), several of them invented to cover edges.
  The thresholds (two rounds, budget 2) are a starting point, not a calibration.
- **Weak auto-triggering.** In trigger tests the skill fired on its own for 2 of 9 (English) and 3 of 9
  (Polish) prompts where it should have, and 0 of 9 where it should not. Do not rely on Claude picking it up unprompted: run
  it yourself when you accept a round, or use the snippet.
- **It depends on log discipline.** No rows means no signals. Without a measure there is no signal B.
- **Gate types are declared by people.** Calling a model gate an `oracle` silences signal A.
- **Platform differences.** `context: fork` and pre-executed commands are Claude Code features. In Codex
  and the Claude app the skill runs in the main context and executes the script itself.
- Cross-model alternatives have not been exercised end to end yet. All recorded runs were
  single-family (`DEGRADED`).

## Evidence

Small and transparent; details in [EVALS.md](EVALS.md).

| Check | Result | Read it as |
|---|---|---|
| Signals backtest, 12 cases in English and Polish, both editions | 50 / 50 | rules derived from these same cases, some invented; overfitting likely |
| Blind runs, 3 tasks, with vs without the skill | 12 / 12 vs 7 / 12 criteria | one run per task, graded by the author; one criterion (card format) favours the skill |
| End to end through the installed plugin | one-line OK on a converging log; ALARM and an exact-format card on a loop | the Claude Code mechanics work |
| Auto-trigger, 18 prompts per language | recall 2 / 9 (EN), 3 / 9 (PL); false triggers 0 / 9 | invoke it yourself; do not wait for it |

The clearest difference showed on the copy guard. Without the skill, the agent proposed a better lock and
more tests, i.e. another controller. With it, the agent proposed removing the copy, which is what actually
closed the original case.

## Prior art and credits

No code is copied from these projects. The ideas behind the design come from:
- the **Toyota Production System**: 5 Whys, *jidoka* / stop-the-line, *poka-yoke*;
- Gary Klein's **pre-mortem**;
- Google SRE's **error budget policy**: decide in advance what happens when the budget is spent;
- Martin Fowler's **strangler fig**: replace, don't patch;
- **Chesterton's fence**;
- Hamel Husain and Shreya Shankar's **evals skills**: validate a judge against human labels;
- [obra/superpowers](https://github.com/obra/superpowers) `systematic-debugging`: “≥ 3 failed fixes, question the architecture”;
- [frankbria/ralph-claude-code](https://github.com/frankbria/ralph-claude-code): its circuit breaker, which taught the lesson that file changes are not progress;
- [lessdumb](https://github.com/enkhbold470/lessdumb): delete before you optimise.

**What is new here:** the alarm is computed from *who gives the verdict* and *whether the problem count
drops* on a plain rounds log. The alternatives come from a ladder that puts “better controller” last.
The review runs as a fresh-context auditor that reads real records, and the outcome is a one-page card
on which a human decides. See [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

Related: [konsylium](https://github.com/witczakm/konsylium), a multi-perspective council for decisions, and
[cycle-lifecycle](https://github.com/witczakm/cycle-lifecycle), project memory across agent sessions.

## Contributing and license

Issues and pull requests are welcome, especially **real loops** (anonymised round logs) that the signals
miss or flag wrongly. See [CONTRIBUTING.md](CONTRIBUTING.md).

[MIT](LICENSE) © 2026 Michał Witczak
