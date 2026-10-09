#!/usr/bin/env python3
"""step-back / krok-wstecz — loop signals from a rounds log.

Counts deterministic "step back" signals from a plain Markdown rounds log
(docs/ROUNDS.md or docs/RUNDY.md). No models, no network, standard library only.
Always exits 0: the skill runs it before the model sees anything, and a failing
command would abort the skill.

Usage:
    python3 signals.py [LOG] [--track NAME] [--json] [--lang en|pl]

Signals:
    A  a gate of type "model" (no human-approved reference set) said NO in its two
       most recent rounds — the yardstick moves together with every fix.
    B  rounds exceed the budget, the gate's latest result is NO, and its measure
       (number of problems; lower is better) did not drop since its previous round,
       or there is no measure at all.
Statuses (most severe first):
    ESCALATE  an alarm after an earlier step-back (kind X) — a human decides,
              not a second review
    ALARM     run the step-back review before the next round
    NOTE      missing contract, an unanchored model gate, or an oracle PASS
              while a model says NO
    OK
The log format accepts English and Polish keywords; see the skill's assets/.
"""
import json
import os
import re
import sys
from pathlib import Path

GATE_TYPES = {"oracle": "oracle", "wyrocznia": "oracle",
              "reference": "reference", "gold": "reference", "wzorzec": "reference",
              "model": "model"}
KINDS = {"C": "control", "K": "control", "O": "output", "W": "output",
         "M": "measure", "P": "measure", "R": "removal", "U": "removal", "X": "stepback"}
PASS_WORDS = {"pass", "ok", "yes", "tak", "rc0", "green", "zielone"}
H_OUTPUT = {"output", "wytwór", "wytwor"}
H_GATES = {"gates", "bramki"}
H_BUDGET = {"budget", "budżet", "budzet"}
RANK = {"OK": 0, "NOTE": 1, "ALARM": 2, "ESCALATE": 3}

T = {
    "en": {
        "status": {"OK": "OK", "NOTE": "NOTE", "ALARM": "ALARM", "ESCALATE": "ESCALATE"},
        "no_contract": "no track contract (\"Output:\" and \"Gates:\" lines) — add it before the next round",
        "unanchored": "gate \"{g}\" is a model with no reference set — consider a human-approved reference set or a third state \"for human decision\" before adding a rule",
        "sig_a": "A: gate \"{g}\" (model, no reference set) said NO in rounds {r1} and {r2}",
        "sig_b_nomeasure": "B: budget of {b} rounds exceeded ({n}), \"{g}\" still NO, no measure of progress",
        "sig_b": "B: budget of {b} rounds exceeded ({n}), \"{g}\" still NO, measure {m1:g} -> {m2:g} is not dropping",
        "oracle_pass": "the oracle says PASS while NO comes from a model ({g}) — model findings do not block; they go to a list for human decision",
        "already": "a step-back already happened in round {r} — a human decides now, not a second review",
        "no_log": "NO LOG: {p} does not exist. Signals cannot be counted — reconstruct the rounds from session records (mark them as reconstructed) or start a log from assets/ROUNDS_template.md.",
        "no_tracks": "NO TRACKS in {p} (expected a heading \"## Track: <name>\").",
        "rounds": "rounds",
        "error": "SCRIPT ERROR (signals not counted): {e}",
    },
    "pl": {
        "status": {"OK": "OK", "NOTE": "UWAGA", "ALARM": "ALARM", "ESCALATE": "ESKALACJA"},
        "no_contract": "brak kontraktu toru (linie „Wytwór:” i „Bramki:”) — dopisz przed kolejną rundą",
        "unanchored": "bramka „{g}” to model bez wzorca — rozważ wzorzec od człowieka albo trzeci stan „do decyzji”, zanim dodasz regułę",
        "sig_a": "A: bramka „{g}” (model bez wzorca) mówi NO w rundach {r1} i {r2}",
        "sig_b_nomeasure": "B: budżet {b} rund przekroczony ({n}), „{g}” nadal NO, brak miary postępu",
        "sig_b": "B: budżet {b} rund przekroczony ({n}), „{g}” nadal NO, miara {m1:g} → {m2:g} nie spada",
        "oracle_pass": "wyrocznia daje PASS, a NO pochodzi od modelu ({g}) — uwagi modelu nie blokują, trafiają na listę do decyzji człowieka",
        "already": "krok wstecz był już w rundzie {r} — teraz decyzja człowieka, nie drugi przegląd",
        "no_log": "BRAK DZIENNIKA: {p} nie istnieje. Sygnałów nie da się policzyć — odtwórz rundy z zapisów sesji (oznacz jako odtworzone) albo załóż dziennik z szablonu assets/RUNDY_szablon.md.",
        "no_tracks": "BRAK TORÓW w {p} (oczekiwany nagłówek „## Tor: <nazwa>”).",
        "rounds": "rund",
        "error": "BŁĄD SKRYPTU (sygnałów nie policzono): {e}",
    },
}


def _number(text):
    """First number in a cell ('43 errors' -> 43.0, '63 %' -> 63.0); none -> None."""
    m = re.search(r"-?\d+(?:[.,]\d+)?", text or "")
    return float(m.group().replace(",", ".")) if m else None


def _result(text):
    t = (text or "").strip().lower().replace(" ", "")
    return "PASS" if t in PASS_WORDS else "NO"


def parse(text):
    tracks, cur = [], None
    for line in text.splitlines():
        s = line.strip()
        m = re.match(r"^#{2,3}\s*(?:track|tor)\s*:\s*(.+)$", s, re.I)
        if m:
            cur = {"track": m.group(1).strip(), "output": None, "gates": {},
                   "budget": 2, "rows": []}
            tracks.append(cur)
            continue
        if cur is None:
            continue
        key, _, value = s.partition(":")
        k = key.strip().lower()
        if k in H_OUTPUT and value.strip():
            cur["output"] = value.strip()
        elif k in H_GATES:
            for item in re.split(r"[;,]", value):
                name, _, typ = item.partition("=")
                name, typ = name.strip().lower(), typ.strip().lower()
                if name:
                    cur["gates"][name] = GATE_TYPES.get(typ, "?")
        elif k in H_BUDGET:
            n = _number(value)
            if n is not None:
                cur["budget"] = int(n)
        elif s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 3 or not re.fullmatch(r"\d+", cells[0]):
                continue  # table header or separator
            kind = cells[4].strip().upper()[:1] if len(cells) > 4 else ""
            cur["rows"].append({
                "r": int(cells[0]),
                "gate": cells[1].lower(),
                "result": _result(cells[2]),
                "measure": _number(cells[3]) if len(cells) > 3 else None,
                "kind": KINDS.get(kind, ""),
            })
    return tracks


def evaluate(track, t):
    reasons, notes = [], []
    if not track["output"] or not track["gates"]:
        notes.append(t["no_contract"])
    rows = sorted(track["rows"], key=lambda x: x["r"])
    stepbacks = [x["r"] for x in rows if x["kind"] == "stepback"]
    since = max(stepbacks) if stepbacks else 0      # count only rounds after the last step-back
    after = [x for x in rows if x["r"] > since]
    rounds = sorted({x["r"] for x in after})
    for gate in sorted({x["gate"] for x in after}):
        typ = track["gates"].get(gate, "?")
        hist = [x for x in after if x["gate"] == gate]
        if typ == "model" and len(hist) == 1 and hist[-1]["result"] == "NO":
            notes.append(t["unanchored"].format(g=gate))
        if typ == "model" and len(hist) >= 2 and all(x["result"] == "NO" for x in hist[-2:]):
            reasons.append(t["sig_a"].format(g=gate, r1=hist[-2]["r"], r2=hist[-1]["r"]))
        if len(rounds) > track["budget"] and hist and hist[-1]["result"] == "NO":
            m_now = hist[-1]["measure"]
            m_prev = hist[-2]["measure"] if len(hist) >= 2 else None
            if m_now is None or m_prev is None:
                reasons.append(t["sig_b_nomeasure"].format(b=track["budget"], n=len(rounds), g=gate))
            elif m_now >= m_prev:
                reasons.append(t["sig_b"].format(b=track["budget"], n=len(rounds), g=gate,
                                                 m1=m_prev, m2=m_now))
    if rounds:
        last = [x for x in after if x["r"] == rounds[-1]]
        oracle_pass = any(track["gates"].get(x["gate"]) == "oracle" and x["result"] == "PASS"
                          for x in last)
        model_no = sorted({x["gate"] for x in last
                           if track["gates"].get(x["gate"]) == "model" and x["result"] == "NO"})
        if oracle_pass and model_no:
            notes.append(t["oracle_pass"].format(g=", ".join(model_no)))
    if reasons:
        status = "ESCALATE" if since else "ALARM"
        if since:
            reasons.append(t["already"].format(r=since))
    else:
        status = "NOTE" if notes else "OK"
    return {"track": track["track"], "status": status, "status_label": t["status"][status],
            "rounds": len(rounds), "reasons": reasons, "notes": notes}


def main(argv):
    lang = os.environ.get("STEP_BACK_LANG", "en")
    track_filter, positional, i = None, [], 0
    while i < len(argv):
        a = argv[i]
        if a in ("--track", "--tor") and i + 1 < len(argv):
            track_filter = argv[i + 1].lower(); i += 2; continue
        if a == "--lang" and i + 1 < len(argv):
            lang = argv[i + 1].lower(); i += 2; continue
        if not a.startswith("--"):
            positional.append(a)
        i += 1
    t = T.get(lang, T["en"])
    if positional:
        path = Path(positional[0])
    else:
        candidates = [Path("docs/RUNDY.md"), Path("docs/ROUNDS.md")] if lang == "pl" \
            else [Path("docs/ROUNDS.md"), Path("docs/RUNDY.md")]
        path = next((p for p in candidates if p.exists()), candidates[0])
    if not path.exists():
        print(t["no_log"].format(p=path))
        return 0
    results = [evaluate(tr, t) for tr in parse(path.read_text(encoding="utf-8"))]
    if track_filter:
        results = [r for r in results if track_filter in r["track"].lower()]
    if "--json" in argv:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    if not results:
        print(t["no_tracks"].format(p=path))
        return 0
    for r in sorted(results, key=lambda x: -RANK[x["status"]]):
        print(f"{r['status_label']:<9} | {r['track']} | {t['rounds']}: {r['rounds']}")
        for line in r["reasons"] + r["notes"]:
            print(f"          - {line}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:  # the script must never abort the skill
        lang = os.environ.get("STEP_BACK_LANG", "en")
        print(T.get(lang, T["en"])["error"].format(e=e))
        sys.exit(0)
