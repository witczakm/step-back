# Security

- `signals.py` reads one local file, uses only the Python standard library, makes no network calls and
  writes nothing.
- `install.sh` copies files into `~/.claude/skills` and/or `~/.codex/skills`, moves any existing
  install to `skills-backups/` and makes no network calls. Run it with `--dry-run` first if in doubt.
- The skill itself may call other model CLIs **only if they are already installed and configured** on
  your machine, within a budget of 5 calls per use. It never commits, pushes or edits code.
- It reads the rounds log and the records named in `Output:`. Do not point it at files containing
  secrets or data you would not send to a cloud model.

Report a vulnerability privately via GitHub's "Report a vulnerability" (Security tab) rather than a
public issue.
