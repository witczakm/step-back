#!/usr/bin/env python3
"""Build dist/*.zip for upload in the Claude app (Customize -> Skills).
The app's validator accepts a narrower frontmatter than Claude Code, so Claude Code-only
keys (context, argument-hint) are stripped from the copy that goes into the zip."""
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STRIP = re.compile(r"^(context|argument-hint):.*\n", re.M)
for skill_id, lang in (("step-back", "en"), ("krok-wstecz", "pl")):
    src = ROOT / "plugins" / skill_id / "skills" / skill_id
    out = ROOT / "dist" / f"{skill_id}-{lang}.zip"
    out.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(src.rglob("*")):
            if f.is_dir() or "__pycache__" in f.parts:
                continue
            arc = Path(skill_id) / f.relative_to(src)
            if f.name == "SKILL.md":
                z.writestr(str(arc), STRIP.sub("", f.read_text(encoding="utf-8")))
            else:
                z.write(f, str(arc))
    print(f"built {out.relative_to(ROOT)}")
