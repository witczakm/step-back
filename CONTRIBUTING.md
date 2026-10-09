# Contributing

The most valuable contribution is a **real loop**: an anonymised rounds log (the format in
`assets/ROUNDS_template.md`) where the signals fire wrongly or stay silent when they should not.

1. Add the log as `tests/cases/en/<id>.md` (or `pl/`) and its expected status to `tests/expected.json`.
2. Run `python3 tests/run_tests.py`. A failing case is a welcome PR on its own — say what you expected and why.
3. If you change `signals.py`, change it in **both** editions (CI checks they are identical) and keep it
   standard-library only and exit-code-0.
4. Changes to `SKILL.md` should land in both languages. Keep `description` under 1024 characters
   (the Claude app's limit).

Please do not include secrets, client names or personal data in logs or records.
