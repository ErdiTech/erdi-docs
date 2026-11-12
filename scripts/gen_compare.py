"""Generate small partials from kb.json: a model comparison table and the ArduPilot Lua parameter table."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
KB = {m["model"]: m for m in json.load(open(os.path.join(os.environ.get("ERDI_KB_DIR", "D:/erdi-kb"), "api", "kb.json"), encoding="utf-8"))["models"]}
txt = open(os.path.join(ROOT, "src/lib/models.generated.mjs"), encoding="utf-8").read()
W = json.loads(txt[txt.index("{"): txt.rindex("}") + 1])


def row(m, *labels):
    for lab in labels:
        for r in KB[m]["specs"]:
            if r["label"].strip().lower() == lab:
                return str(r["value"]).replace("|", "/").replace("<", "&lt;")
    return "see datasheet"


lines = ["| Model | Wavelength | Measurement range | Interface | Supply voltage | Wire unit | Baud |", "|---|---|---|---|---|---|---|"]
for m in W:
    lines.append("| [{0}](../models/{1}.mdx) | {2} | {3} | {4} | {5} | {6} | {7} |".format(
        m, m.lower(), row(m, "laser wavelength"), row(m, "measurement range", "ranging range"),
        row(m, "interface", "communication interface"), row(m, "supply voltage"),
        {"m": "m x10", "cm": "cm", "mm": "mm"}[W[m]["unit"]], W[m]["default_baud"]))
open(os.path.join(ROOT, "docs/get-started/_compare.md"), "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")

lp = ["| Model | `ERDI_MODE` | `ERDI_BR` | `ERDI_UNIT` | `ERDI_LEN` | `ERDI_OOR` |", "|---|---|---|---|---|---|"]
for m in W:
    w = W[m]
    if w["family"] == "B":
        unit = {"cm": "0.01", "mm": "0.001"}[w["unit"]]
        lp.append(f"| {m} | 0 | {w['default_baud']} | {unit} | {w['frame_len']} | {w['out_of_range_raw']} |")
    else:
        lp.append(f"| {m} | 1 | {w['default_baud']} | n/a | n/a | n/a |")
open(os.path.join(ROOT, "docs/platforms/_lua-params.md"), "w", encoding="utf-8", newline="\n").write("\n".join(lp) + "\n")
print("ok")
