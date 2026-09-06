"""hooks.py — hook gates and score, in the spirit of the Growth System's layer 3 / H rubric.

The Growth System (run_system.py, 2026-08-31) scores every opening line out of 12 and refuses to print a
concept that fails its Gap / Truth / Pull gates or the trademark check. That code was never pushed, so this
is a re-implementation of the same idea from the published description, kept deliberately simple:

    gates  : Gap (contrast / curiosity / question / number), Truth (every claim maps to a product fact),
             Pull (speaks to the viewer, a moment, a room or an action)
    score  : gates 0–3 · brevity 0–3 · specificity 0–3 · proven-family match 0–3   → /12

Use: python3 hooks.py "Nobody guesses how the colour changes."   or   from hooks import score_hook
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PRESETS = json.load(open(os.path.join(HERE, "presets.json"), encoding="utf-8"))
ENGINE = PRESETS["engine"]

FAMILIES = {
    "contrast":          r"\bnot\b|\bno\b\s+\w|\bwrong\b|\binstead\b|\b(warmer|colder|less|more)\b",
    "question":          r"\?$",
    "curiosity":         r"\bnobody\b|\bno one\b|\bguess\b|\bwatch\b|\bthere's no\b|\bsecret\b|\bhow\b",
    "pov":               r"^pov:|\byou\b|\byour\b|\b\d{1,2}\s?(am|pm)\b",
    "listicle":          r"\b(one|two|three|1|2|3)\b.*\b(moods?|reasons?|colours?|things?|lamps?|rooms?|sizes?|lines?|pieces?|feet|finishes)\b",
    "transformation":    r"\bsame\b.*\bdifferent\b|\bchanges?\b|\btransform\b|\bbefore\b|\bafter\b|\bturn\b",
    "pattern-interrupt": r"\bstop\b|\bstill\b|\bwait\b",
    "price":             r"₹|\bprice\b|\brupees\b",
    "festive":           r"\bgift\b|\bdiwali\b|\bwedding\b",
}
BANNED = set(PRESETS["banned_words"])
HYPE = {"best", "cheapest", "guaranteed", "perfect", "ultimate", "revolutionary", "world's"}


def words(s):
    return re.findall(r"[a-zA-Z₹0-9,'’.-]+", s)


def families(hook):
    h = hook.lower().strip()
    return [f for f, rx in FAMILIES.items() if re.search(rx, h)]


def gate_gap(hook):
    return bool(set(families(hook)) & {"contrast", "question", "curiosity", "pattern-interrupt", "transformation", "listicle"})


def gate_truth(hook, facts):
    """no banned/hype words; every number in the hook appears in the product facts"""
    h = hook.lower()
    if any(w in BANNED or w in HYPE for w in re.findall(r"[a-z']+", h)):
        return False
    # a clock time is not a product claim: "at 11 pm", "9:40 pm"
    h = re.sub(r"\b\d{1,2}(:\d{2})?\s*(am|pm)\b", " ", h)
    nums = re.findall(r"₹?\d[\d,]*", h)
    facts_l = " ".join(facts).lower()
    return all(n in facts_l for n in nums)


def gate_pull(hook):
    h = hook.lower()
    return bool(re.search(r"\byou\b|\byour\b|^pov:|\b\d{1,2}\s?(am|pm)\b|\b(room|wall|bedside|desk|corner|home|evening|night|tonight)\b|\b(watch|turn|look|stop)\b", h))


def trademark_hits(text):
    t = text.lower()
    return [term for term in ENGINE["trademark_terms"] if term in t]


def score_hook(hook, product="rubik"):
    facts = PRESETS["products"].get(product, {}).get("facts", [])
    gates = dict(gap=gate_gap(hook), truth=gate_truth(hook, facts), pull=gate_pull(hook))
    n = len(words(hook))
    brevity = 3 if n <= 6 else 2 if n <= 9 else 1 if n <= 12 else 0
    h = hook.lower()
    concrete = sum(1 for k in ("colour", "color", "glass", "wood", "sheesham", "lamp", "light", "wall", "room", "turn", "red", "green", "amber", "₹", "3", "three", "pm", "tubelight", "switch", "plastic")
                   if k in h)
    specificity = min(3, concrete)
    fam = families(hook)
    proven = [p for p in ENGINE["hooks_proven"] if set(families(p["line"])) & set(fam)]
    family = 3 if len(proven) >= 3 else 2 if proven else 1 if fam else 0
    total = sum(gates.values()) + brevity + specificity + family
    return dict(hook=hook, words=n, gates=gates, brevity=brevity, specificity=specificity, family=family,
                families=fam, score=total, out_of=12, trademark=trademark_hits(hook), passes=all(gates.values()))


def suggest(family=None, product=None):
    out = ENGINE["hooks_proven"]
    if family:
        out = [p for p in out if p["family"] == family]
    if product:
        out = [p for p in out if p["product"] in (product, "any")]
    return out


if __name__ == "__main__":
    for h in sys.argv[1:] or [p["line"] for p in ENGINE["hooks_proven"]]:
        r = score_hook(h)
        g = "".join("✓" if v else "✗" for v in r["gates"].values())
        print(f'{r["score"]:>2}/12  gates {g}  fam {",".join(r["families"]) or "-":28s} {h}')
