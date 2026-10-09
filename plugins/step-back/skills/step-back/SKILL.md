---
name: step-back
description: Use when fixes go in circles — each round adds another exception, if-branch, rule, limit, retry, lock or second judge, and the same review or test says NO again; when the rejection count stays flat or grows; when one model grades or checks another model's output with no human-approved reference set; when reviews keep finding new holes in the control mechanism itself; when signals.py reports ALARM; or when someone says "step back", "we're going in circles", "workaround on a workaround", "exception to the exception", "maybe the whole approach is wrong". Runs a frame review in a fresh context — instead of adding another controller it looks at what the step actually produces and proposes removing the step or changing its output, with one recommendation on a decision card. Run it before commissioning another round of fixes to the same thing. Do NOT use on a first failure, when rounds converge (fewer problems each time), for a one-off bug with a clear cause, a routine bugfix, code review or refactor planning.
argument-hint: "[track] [log-path]"
context: fork
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/signals.py *)
---

# Step back — a frame review at the threshold

You act as a **frame auditor** in a fresh context. You do not know the session's line of reasoning,
and that is deliberate: "workaround on a workaround" loops happen because everyone involved looks at
the newest version of a mechanism and asks "does it work?", while nobody asks "should it exist?".
Your input is **the history of rounds and real records of what the step produces**, not the
executor's summary. Your output is one decision card of at most one page. A human decides.

## Signals counted before you start

!`python3 ${CLAUDE_SKILL_DIR}/scripts/signals.py --lang en`

Invocation arguments: `$ARGUMENTS`. If they name another log file or a track, run
`python3 ${CLAUDE_SKILL_DIR}/scripts/signals.py <path> --track <name> --lang en`.
In agents that do not pre-execute the line above (you see the command instead of its output),
run it yourself from the project root.

How to read the result:
- **OK** — say so in one sentence and stop. Rounds are converging; a review would be just another
  controller. Exception: an on-demand call with a stated reason — then run the short version
  (steps 1, 3 and 4).
- **NOTE** — return the notes and one sentence on what to add (track contract, a reference set or a
  third state). Do not run the full procedure.
- **ALARM** — run the full procedure below.
- **ESCALATE** — a step-back already happened on this track and did not help. Do not run a second
  review. Return a short summary for the human: what the previous step-back changed, the measure
  before and after, and two options for their decision. The skill obeys the same stop rule as
  everything else.
- **NO LOG** — reconstruct the rounds from available records (session notes, commits, review
  reports) in the format of `assets/ROUNDS_template.md`, mark it **reconstructed, uncertain**, write
  "UNKNOWN" for fields you cannot establish, and count signals on the reconstructed file. Without a
  measure there is no signal B — say so plainly.

## Procedure (on ALARM)

### 1. Reconstruct what the step really produces
Read 10–20 **real records** of the output (files, database rows, results, logs) — the "Output:" line
of the log or the repository tells you where. Describe the output in three sentences.
Why: a plain bug (say, batches above some number silently skipped) is often visible only in the
records, not in round reports. If you cannot read records, say so on the card — it weakens the
whole recommendation.

### 2. Name the common denominator of defects
Sort the defects from recent rounds into three bins: **output** (what the step produces),
**controller** (judge, guard, rule, limit) and **measurement** (trial script, sample, counting
method). Count them. If most defects sit in the controller or the measurement, the control mechanism
is the problem, not the output.

### 3. Establish who gives the verdict and whether a reference set is needed
| Who decides | Human-approved reference set needed? | Consequence |
|---|---|---|
| Oracle (test, execution, checksum) | no | only check that the oracle really tests what changed |
| Convention or taste (summary, style, naming, length) | no — and no model checker either | mechanical checks, or remove the controller |
| Factual truth (does the evidence prove the claim) | yes — 20–60 cases approved by a human, part of them frozen | without one: a third state "for human decision", not another rule |

Also ask: **does a wrong verdict actually cost anything?** If not, the controller is unnecessary.
When an oracle says PASS and the NO comes from a model, model findings do not block: they go to a
list for human decision.

### 4. Alternatives — four viewpoints and a ladder
Look from four sides: **output** (what the step produces), **removal** (what if the step did not
exist), **another method** (same sample, independent method), **consumer** (who reads the output and
what they actually need). Then list alternatives starting at the top of the ladder — consider every
rung explicitly:

1. **Remove the step.** Before recommending it, find out why it exists (history, callers) —
   Chesterton's fence. Often the data already lives somewhere else.
2. **Change what the step produces** — the output contract: structured fields instead of prose,
   a full sentence instead of a fragment, pointing at the element instead of a verdict.
3. **Move the check to the source** — so the defect cannot arise (poka-yoke).
4. **A third state instead of a verdict** — "for human decision" with a reason; decisions build the
   reference set.
5. **A better controller** — only at the end and labelled **"still a controller"**. Replacing a
   hand-made lock with a system lock can be right, but it does not remove the source of the problem.

### 5. Define the control method
Describe how to run the same sample through a **second, independent method** (another model from
scratch without seeing the first verdict, a deterministic rule, or a human) and which single number
comes out (agreement rate). Disagreements go to a human. Execution belongs to whoever owns the track,
not to you.

### 6. One recommendation, then attack it
Pick one alternative. Have an adversary from a different model family attack it (section below).
Add: a measurable first step, a **failure criterion after 2 rounds**, and **what would change the
recommendation**.

### 7. The card
Return the card in exactly this format as your final message — it is the only thing that
returns to the main session. The main session records the human's decision in the log as a row of
kind **X** and in the project's decision record. Lessons go wherever the project keeps them; you do
not write them.

```
STEP BACK — <track> — <YYYY-MM-DD> — after round <n>
Models: <families that answered; or DEGRADED: one model family> | calls: <k>/5
Signals: <signals.py output: reasons A/B, notes>
What the step produces (based on <number> records): <3 sentences>
Common denominator: output defects <a> | controller <b> | measurement <c> -> <one-sentence conclusion>
Verdict given by: <oracle | convention | factual truth> -> reference set: <not needed | exists | missing>
Alternatives:
| rung | proposal | cost | risk |
| 1 remove the step | … | … | … |
| 2 change the output | … | … | … |
| 3 check at the source | … | … | … |
| 4 third state | … | … | … |
| 5 better controller (still a controller) | … | … | … |
RECOMMENDATION: <rung n — 1–2 sentences>
Net line: control mechanisms <before> -> <after>
First step and measure: <…>   Failure criterion after 2 rounds: <…>
Control method: <same sample, second method, one number>
Adversary's attack: <strongest objection; what survives>
What would change the recommendation: <fact or condition>
What we don't know: <…>
Human decision: [ ] accept  [ ] otherwise: ______   -> row of kind X in the log
```

A filled-in example: `examples/example_card.md`.

## Models — a fixed scheme and a budget

You run in a subagent, so you cannot start further subagents (persona panels). Call other model
families from the shell, if available:
1. a cross-model tool the user already has (a consensus/"swarm" skill script, an OpenRouter helper,
   or a second agent CLI such as Codex or Gemini) — check its `--help` first;
2. otherwise draft the alternatives yourself and put **"DEGRADED: one model family"** in the card
   header — the main session may then run a multi-perspective review (for example the `konsylium`
   skill).

| Activity | Who | Calls |
|---|---|---|
| signals | script | 0 |
| reconstructing the log (only if missing) | a cheap model | 1 |
| records, denominator, verdict | you, from files | 0 |
| blind alternatives | 3 different model families | 3 |
| attack on the recommendation | 1 adversary from a family other than the author's | 1 |

**Budget: at most 5 external model calls per use.** When it runs out, close the card with what you
have and say so on it. **No model decides what is true** — model agreement is a signal, not
evidence; truth comes from an oracle or a human-approved reference set.

## What this skill does not do

- It is not a gate and blocks nothing — it issues a card.
- It does not add rules. Recommending "add rule X" without considering rungs 1–4 is a procedure error.
- It does not replace a human decision or a human-approved reference set.
- It does not repeat itself: at most one use per track, then ESCALATE to a human.

## Files

- `scripts/signals.py` — counts signals; always exits 0; English and Polish logs.
- `assets/ROUNDS_template.md` — the rounds log format.
- `assets/brief_lines.md` — lines for executor briefs, the report line and the reviewer question.
- The decision card template is inline in step 7 above.
- `examples/example_card.md` — a filled-in card.
- `snippets/` — optional lines for `CLAUDE.md` and `AGENTS.md`.
