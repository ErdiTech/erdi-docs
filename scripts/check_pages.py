"""Check generated model pages against the product database: every spec row on a page must equal the
KB row (label, value, cleaned condition), no KB row may be missing, no page may contain a price, and
the red-line words must not appear anywhere in docs/.
    python scripts/check_pages.py        exit code 0 = no differences
"""
import json, os, re, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
KB_DIR = os.environ.get("ERDI_KB_DIR", "D:/erdi-kb")
kb = {m["model"]: m for m in json.load(open(os.path.join(KB_DIR, "api", "kb.json"), encoding="utf-8"))["models"]}
sys.path.insert(0, HERE)
import importlib.util
spec = importlib.util.spec_from_file_location("gen_models", os.path.join(HERE, "gen_models.py"))
gm = importlib.util.module_from_spec(spec); spec.loader.exec_module(gm)

diffs = 0; checked = 0; rows = 0
for m in gm.PUBLIC:
    t = open(os.path.join(ROOT, "docs", "models", m.lower() + ".mdx"), encoding="utf-8").read()
    sec = t[t.index("## Specification"): t.index("## Pinout")]
    page = [tuple(x.strip() for x in l.strip().strip("|").split("|")) for l in sec.splitlines() if l.startswith("|") and not l.startswith("|---") and not l.startswith("| Parameter")]
    want = [tuple(r) for r in gm.spec_rows(m)]
    page = [tuple(list(p) + [""] * (3 - len(p))) for p in page]
    if page != want:
        diffs += 1
        print("DIFF", m, len(page), len(want))
    # protocol fields vs KB
    f = {k: v["value"] for k, v in kb[m]["protocol"]["fields"].items()}
    if f"{f['baud']} bps" not in t:
        diffs += 1; print("DIFF baud", m)
    if re.search(r"\$\s?\d|USD", t):
        diffs += 1; print("PRICE-LIKE TEXT in", m)
    checked += 1; rows += len(want)
bad = re.compile(r"military|weapon|missile|artillery|designator|targeting|fire control|erdicn|erditechs|surertech|\u6292\u5fae|\u7167\u5c04|\u76ee\u6807\u6307\u793a", re.I)
for f in glob.glob(os.path.join(ROOT, "docs", "**", "*.md*"), recursive=True):
    if bad.search(open(f, encoding="utf-8").read()):
        diffs += 1; print("RED LINE", f)
print(f"models checked {checked}, spec rows compared {rows}, differences {diffs}")
sys.exit(1 if diffs else 0)
