# Changelog

## 0.1.0 — 2026-10-09
First public release (experimental).
- Two editions of one skill: `step-back` (English) and `krok-wstecz` (Polish).
- `signals.py`: deterministic loop signals A and B from a Markdown rounds log; English and Polish
  keywords; statuses OK / NOTE / ALARM / ESCALATE; never aborts the skill (exit code 0).
- Frame review in a fresh context (`context: fork` in Claude Code): reads real records, sorts defects
  into output / controller / measurement, decides by who gives the verdict, walks a five-rung ladder
  with "better controller" last, returns a one-page card. Budget: at most 5 external model calls.
- Templates: rounds log, brief lines, decision card; snippets for `CLAUDE.md` and `AGENTS.md`.
- Distribution: Claude Code plugin marketplace, `install.sh` for Claude Code and Codex, zips for the
  Claude app.
- Backtest of 12 cases in both languages; blind with/without runs; end-to-end runs through the plugin.
