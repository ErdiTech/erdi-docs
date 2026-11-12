"""Generate model pages, the model index, the "more models" page and the compatibility matrix.

Inputs (read-only):
  D:/erdi-kb/api/kb.json            verified specs + protocol fields (the only source of numbers)
  D:/erdi-kb/products/<MODEL>.md    pin tables (first table of the "Pin definition" section)
  fixtures/catalog-names.json       model names of the full 59-model catalogue (names + titles only)
  src/lib/models.generated.mjs      wire facts from erdi-lrf 0.1.4 (cross-checked against the KB here)

Rules enforced here, not by hand:
  * No price anywhere (kb.json "price" is never read into a page).
  * No KB "source" excerpts are printed (they quote manuals and contain third-party brand text).
  * Fields that the KB does not carry are not written.
  * Cross-check: KB protocol fields (baud, frame bytes, out-of-range) must equal the erdi-lrf table.

    python scripts/gen_models.py
"""
import json, os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KB_DIR = os.environ.get("ERDI_KB_DIR", "D:/erdi-kb")
DOCS = os.path.join(ROOT, "docs")
SITE = "https://erdilrf.com"

kb = json.load(open(os.path.join(KB_DIR, "api", "kb.json"), encoding="utf-8"))["models"]
kb = {m["model"]: m for m in kb}
txt = open(os.path.join(ROOT, "src", "lib", "models.generated.mjs"), encoding="utf-8").read()
wire = json.loads(txt[txt.index("{"): txt.rindex("}") + 1])
names = json.load(open(os.path.join(ROOT, "fixtures", "catalog-names.json"), encoding="utf-8"))

PUBLIC = list(wire.keys())
assert len(PUBLIC) == 22

# Library model lists (from each project's README / header, 2026-11-13).  A model that is
# not in a library's list gets "No driver yet" in the matrix and no snippet on its page.
NOT_IN = {"arduino": {"LRF10VB"}, "esphome": {"LRF10VB"}, "ros2": {"LRF10VB"}}
# ArduPilot native driver PR #34983 covers these 8 models (types 49 and 50).
PR_MODELS = {"LRF10VB", "LRF22VB", "LRF50VB", "LRF50H", "LRF100H", "LRF200H", "LRF300H", "LRF600H"}
# ArduPilot Lua + SITL: synthetic 4-byte centimetre frames (ERDI_MODE=0, ERDI_UNIT=0.01, ERDI_LEN=4).
SITL_VERIFIED = {"LRF50H", "LRF100H", "LRF200H", "LRF300H", "LRF600H"}

FAMILY_NAME = {"A": "Family A (55 AA, polled)", "B": "Family B (5C, streaming)"}
CJK = re.compile(r"[\u3000-\u9fff\uff00-\uffef]")


def slug(m):
    return m.lower()


def kbrange(m):
    for lab in ("measurement range", "ranging range", "range"):
        for r in kb[m]["specs"]:
            if r["label"].strip().lower() == lab:
                return esc(str(r["value"]).replace("|", "/"))
    return "see specification"


def esc(t):
    """Escape characters that MDX would read as JSX or expressions."""
    return str(t).replace("<", "&lt;").replace("{", "&#123;").replace("}", "&#125;")


def clean_cond(c):
    c = (c or "").strip()
    c = re.sub(r"\s*·?\s*source technical table", "", c, flags=re.I).strip(" ·")
    return c


def spec_rows(m):
    rows = []
    for s in kb[m]["specs"]:
        v = str(s["value"]).replace("|", "/").strip()
        c = clean_cond(s.get("condition"))
        rows.append((esc(s["label"].strip()), esc(v), esc(c)))
    return rows


TRANS = [("（黑色）", " (Black)"), ("（红色）", " (Red)"), ("（绿色）", " (Green)"), ("（黄色）", " (Yellow)"),
         ("外部电源负", "External Power -"), ("外部电源正", "External Power +"),
         ("定义 / 线材颜色", "Definition / Wire Color"), ("用户接口", "User Interface"),
         ("3.3～5V", "3.3-5V"), ("（SDA）", " (SDA)"), ("（SCL）", " (SCL)")]


def pins(m):
    """Return (header, rows) from the first table of the product file's pin section, or None."""
    p = os.path.join(KB_DIR, "products", m + ".md")
    t = open(p, encoding="utf-8").read()
    i = t.find("## Pin definition")
    if i < 0:
        return None
    sec = t[i:]
    j = sec.find("\n## ", 5)
    sec = sec[: j if j > 0 else None]
    tbl = [l for l in sec.splitlines() if l.startswith("|")]
    if len(tbl) < 3:
        return None
    out = []
    for l in tbl:
        for a, b in TRANS:
            l = l.replace(a, b)
        l = re.sub(r"[（(]host[^)）]*[)）]", "", l)  # drop Chinese-annotated host notes
        l = re.sub(r"[（(]host 侧[^)）]*[)）]", "", l)
        out.append(l)
    body = "\n".join(out)
    if CJK.search(body) or "erdicn" in body.lower():
        return None
    return body


def code_block(lang, code):
    return "```" + lang + "\n" + code.strip("\n") + "\n```"


def snippets(m):
    w = wire[m]
    fam = w["family"]
    baud = w["default_baud"]
    tabs = []
    # Python (erdi-lrf 0.1.4, all 22)
    if fam == "B":
        py = f'''from erdi_lrf import ErdiLRF

# COM3 on Windows, /dev/ttyUSB0 or /dev/serial0 on Linux
with ErdiLRF("/dev/ttyUSB0", "{m}") as lrf:
    for r in lrf.stream():
        print("out of range" if r.out_of_range else f"{{r.metres:.3f}} m", "raw", r.raw)'''
    else:
        py = f'''from erdi_lrf import ErdiLRF

with ErdiLRF("/dev/ttyUSB0", "{m}") as lrf:   # COM3 on Windows
    r = lrf.measure()                          # single-shot (0x88)
    print(f"{{r.metres:.3f}} m", "raw", r.raw)'''
    tabs.append(("Python", "python", "pip install erdi-lrf   # PyPI, MIT\nerdi-lrf --port /dev/ttyUSB0 --model " + m + (" stream --count 20" if fam == "B" else " measure"), py))
    if m not in NOT_IN["arduino"]:
        ino = f'''#include <ErdiLRF.h>

ErdiLRF lrf(Serial1, ERDI_{m});

void setup() {{
  Serial.begin(115200);
  Serial1.begin(erdiDefaultBaud(ERDI_{m}));   // {baud} baud; ESP32: Serial1.begin(baud, SERIAL_8N1, RX_PIN, TX_PIN)
  lrf.setTimeout(1000);
}}

void loop() {{
  ErdiMeasurement m;
  if (lrf.measure(&m) == ERDI_OK) {{
    Serial.println(m.metres, 3);
  }}
  delay(200);
}}'''
        tabs.append(("Arduino", "cpp", "", ino))
    if m not in NOT_IN["esphome"]:
        yml = f'''external_components:
  - source: github://ErdiTech/erdi-lrf-home-assistant
    components: [erdi_lrf]

uart:
  id: lrf_uart
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: {baud}

sensor:
  - platform: erdi_lrf
    uart_id: lrf_uart
    model: {m}
    name: "Laser distance"
    update_interval: 1s'''
        tabs.append(("ESPHome", "yaml", "", yml))
    if m not in NOT_IN["ros2"]:
        ros = f'''cd ~/ros2_ws/src && git clone https://github.com/ErdiTech/erdi_lrf_driver.git
cd ~/ros2_ws && rosdep install --from-paths src --ignore-src -y && colcon build --packages-select erdi_lrf_driver
source install/setup.bash
ros2 launch erdi_lrf_driver erdi_lrf.launch.py port:=/dev/ttyUSB0 model:={m} rate:=10.0
ros2 topic echo /range'''
        tabs.append(("ROS 2", "bash", "", ros))
    out = ["<Tabs groupId=\"lang\">"]
    for i, (name, lang, pre, code) in enumerate(tabs):
        out.append(f'<TabItem value="{name.lower().replace(" ", "")}" label="{name}"{" default" if i == 0 else ""}>')
        out.append("")
        if pre and lang == "python":
            out.append(code_block("bash", pre))
            out.append("")
        out.append(code_block(lang, code))
        out.append("")
        out.append("</TabItem>")
    out.append("</Tabs>")
    return "\n".join(out)


def protocol_section(m):
    p = kb[m]["protocol"]
    f = {k: v["value"] for k, v in p["fields"].items()}
    w = wire[m]
    lines = []
    if w["family"] == "A":
        lines += [
            f"- Frame: 8 bytes, header `55 AA`, then function code, four data bytes, checksum.",
            f"- Default baud: {f['baud']} bps, 8 data bits.",
            "- Transmit checksum: lower 8 bits of function code + D1..D4 (the header is not included).",
            "- Reply checksum: lower 8 bits of header H + header L + function code + D1..D4 (the header is included). The two formulas differ on purpose.",
            "- Reply to a ranging command: `55 AA <fn> STA FF DIS_H DIS_L SUM`. `STA = 1` means the measurement succeeded.",
            "- Distance: `DIS_H:DIS_L` is the measured value in metres multiplied by 10.",
        ]
        cmds = p["commands"]
        if cmds:
            lines += ["", "| Command | Request frame |", "|---|---|"]
            for c in cmds:
                lines.append(f"| {c['name']} | `{c['send']}` |")
        if m in ("LRF1200A1", "LRF3000A1"):
            lines += ["", ":::caution Continuous ranging",
                      "For this model the manual's continuous-ranging request uses function byte `0x89` while the recorded reply uses `0x88`. Poll with single-shot (`0x88`) until ERDI confirms the behaviour for your batch.",
                      ":::"]
    else:
        n = w["frame_len"]
        d = w["distance_bytes"]
        unit = {"cm": "centimetres", "mm": "millimetres"}[w["unit"]]
        if n == 4:
            fr = "`5C <dist_lo> <dist_hi> <check>`"
        else:
            fr = "`5C <dist_lo> <dist_mid> <dist_hi> <check>`"
        lines += [
            f"- Data frame: {n} bytes, {fr}, free-running.",
            f"- Default baud: {f['baud']} bps, 8 data bits, 1 stop bit, no parity.",
            f"- Distance: {d} bytes, little-endian, unit **{unit}**. The VB series reports millimetres and the H series centimetres, so `5C 02 11 EC` is 4.354 m on a VB module and 43.54 m on an H module.",
            f"- Out-of-range marker: the module outputs {w['out_of_range_raw']} when there is no valid target. Treat it as no target, not as a distance.",
            "- Checksum: bitwise inverse of the 8-bit sum of all bytes between the header and the check byte.",
        ]
        if w["start_stop"]:
            lines += ["", "| Command | Request frame |", "|---|---|",
                      "| Start ranging | `5A 0A 02 02 00 F1` |",
                      "| Stop ranging | `5A 0A 02 00 00 F3` |"]
    return "\n".join(lines)


def cross_check(m):
    f = {k: v["value"] for k, v in kb[m]["protocol"]["fields"].items()}
    w = wire[m]
    assert int(f["baud"]) == w["default_baud"], (m, "baud", f["baud"], w["default_baud"])
    assert int(f["frame_bytes"]) == w["frame_len"], (m, "frame", f["frame_bytes"])
    if w["family"] == "B":
        assert int(f["out_of_range"]) == w["out_of_range_raw"], (m, "oor", f["out_of_range"])
        assert f["unit_example"].endswith(w["unit"]), (m, "unit", f["unit_example"])
        assert int(f["dist_bytes"]) == w["distance_bytes"]
    else:
        assert "10" in f["scale"], (m, f["scale"])


KNOWN = {
    "LRF1200A1": ["The datasheet notes that the send and receive checksums are computed over different bytes (see Protocol). Use separate functions for the two directions."],
    "LRF3000A1": ["The datasheet notes that the send and receive checksums are computed over different bytes (see Protocol). Use separate functions for the two directions."],
    "SPD1200N0": ["The datasheet states that request and reply checksum scopes differ but does not print the transmit formula. The erdi-lrf driver uses the family A transmit formula, which reproduces every example frame the datasheet does print."],
    "SPD1200N2": ["The datasheet gives the lower bound of the update rate as either 2 Hz or 4 Hz (2-15 Hz or 4-15 Hz, adaptive). ERDI confirms the value for the delivered batch.",
                  "The datasheet states that request and reply checksum scopes differ but does not print the transmit formula. The erdi-lrf driver uses the family A transmit formula, which reproduces every example frame the datasheet does print."],
    "SPD1200N4": ["The datasheet states that request and reply checksum scopes differ but does not print the transmit formula. The erdi-lrf driver uses the family A transmit formula, which reproduces every example frame the datasheet does print."],
    "LRF50VB": ["The printed example request for reading the serial number does not reproduce with the datasheet's own checksum function. The streaming data frames follow the checksum rule above; build command frames with the rule, not by copying the printed bytes."],
    "LRF1500H": ["The datasheet's example frame `5C 02 11 03 EC` does not satisfy its own checksum rule (the rule gives `E9`). The driver and the serial monitor use the rule.",
                 "The datasheet writes the out-of-range marker as `0xFFFF (16777215)`. With a 3-byte distance field the marker is 16777215."],
    "LRF50H": ["Factory bench capture, 2026-11-06, wall at 1.9 m: 3 of 2000 frames carried a distance of 315 to 397 m with a valid checksum, far past the 50 m rating. Filter outliers in your application (median of a few readings). [Capture notes](https://github.com/ErdiTech/erdi-lrf-drivers/tree/main/docs/evidence/ardupilot-bench-20261105)."],
}
GENERIC_KNOWN = "UART logic level is not stated as a separate field for most models. Supply voltage is not the UART voltage: check the module's TX level against your host before wiring, or ask us."


def platform_rows(m):
    rows = []
    rows.append(("Python (erdi-lrf)", "Untested", "[Python / Raspberry Pi / Jetson](../platforms/raspberry-pi-jetson.md)"))
    rows.append(("Arduino / PlatformIO", "No driver yet" if m in NOT_IN["arduino"] else "Untested", "[Arduino / PlatformIO](../platforms/arduino-platformio.md)"))
    rows.append(("ESPHome / Home Assistant", "No driver yet" if m in NOT_IN["esphome"] else "Untested", "[ESPHome](../platforms/esphome-home-assistant.md)"))
    rows.append(("ROS 2", "No driver yet" if m in NOT_IN["ros2"] else "Untested", "[ROS 2](../platforms/ros2.md)"))
    rows.append(("ArduPilot (Lua script)", "Verified (SITL)" if m in SITL_VERIFIED else "Untested", "[ArduPilot](../platforms/ardupilot.mdx)"))
    rows.append(("ArduPilot native driver", "In review (PR #34983, not merged)" if m in PR_MODELS else "No driver yet", "[ArduPilot](../platforms/ardupilot.mdx)"))
    return rows


def model_page(m):
    k = kb[m]
    w = wire[m]
    cross_check(m)
    s = slug(m)
    title = esc(k["title"].strip())
    desc = f"{m} UART protocol, wiring, specification and code examples (Python, Arduino, ESPHome, ROS 2) for the ERDI {m} laser rangefinder module."
    rows = spec_rows(m)
    spec_tbl = ["| Parameter | Value | Condition |", "|---|---|---|"]
    for a, v, c in rows:
        spec_tbl.append(f"| {a} | {v} | {c} |")
    pn = pins(m)
    if pn:
        pin_md = pn
    else:
        pin_md = "The pin table for this exact variant is in the model datasheet (see Resources). The connector and wire specification is in the specification table above."
    known = KNOWN.get(m, [])
    known_md = "\n".join(f"- {x}" for x in known + [GENERIC_KNOWN])
    plat = platform_rows(m)
    plat_tbl = ["| Platform | Status | Guide |", "|---|---|---|"] + [f"| {a} | {b} | {c} |" for a, b, c in plat]
    apps = esc(", ".join(k.get("applications") or []))
    unit_note = {"m": "metres x 10", "cm": "centimetres", "mm": "millimetres"}[w["unit"]]
    rng = kbrange(m)
    glance = [
        "| | |", "|---|---|",
        f"| Protocol family | {FAMILY_NAME[w['family']]} |",
        f"| Default baud | {w['default_baud']} bps, 8N1 |",
        f"| Frame | {w['frame_len']} bytes |",
        f"| Distance unit on the wire | {unit_note} |",
        f"| Measurement range (datasheet) | {rng} |",
    ]
    out = f'''---
id: {s}
title: "{m} UART protocol and integration"
sidebar_label: {m}
description: "{desc}"
keywords: [{m}, laser rangefinder module, UART protocol, {w['family']} family, ERDI]
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<div className="erdi-lead">{title}</div>

{('Typical applications: ' + apps + '.') if apps else ''}

<div className="erdi-actions">
  <a className="button button--primary" href="{SITE}/models/{s}/">Price and buy on erdilrf.com</a>
  <a className="button button--secondary" href="{SITE}/contact/?model={m}&request_type=cad">Request STEP file</a>
</div>

## At a glance

{chr(10).join(glance)}

## Specification

Values come from the ERDI datasheet for this model. Where the datasheet gives a condition, it is shown.

{chr(10).join(spec_tbl)}

## Pinout and wiring

{pin_md}

Cross TX and RX (module TX to host RX), share ground, and power the module from a supply that matches the supply voltage in the specification table. See [Wiring and power](../get-started/wiring-and-power.md).

## Protocol summary

{protocol_section(m)}

The full frame description is in [Family {w['family']} protocol](../protocols/family-{'a-55aa' if w['family'] == 'A' else 'b-5c'}.md). Try it without installing anything in the [browser serial monitor](../tools/serial-monitor.mdx).

## Code examples

{snippets(m)}

## Platform status

Only rows with evidence say Verified. See the [compatibility matrix](../compatibility/index.mdx) for what that means and where the evidence is.

{chr(10).join(plat_tbl)}

## Known issues

{known_md}

## Resources

- Model page with datasheet download: [{SITE}/models/{s}/]({SITE}/models/{s}/)
- Datasheet and specification page: [{m} datasheet and specs]({SITE}/lrf/{s}-datasheet-specs/)
- Interactive 3D view: [{m} 3D viewer]({SITE}/3d-viewer/{s}/)
- STEP model: available on request, [Request STEP]({SITE}/contact/?model={m}&request_type=cad)
- Drivers and protocol notes: [ErdiTech/erdi-lrf-drivers](https://github.com/ErdiTech/erdi-lrf-drivers)
- Questions: tommy@erdimail.com, +86 133 0819 5790
'''
    return out


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    mdir = os.path.join(DOCS, "models")
    for m in PUBLIC:
        write(os.path.join(mdir, slug(m) + ".mdx"), model_page(m))
    # index
    A = [m for m in PUBLIC if wire[m]["family"] == "A"]
    B = [m for m in PUBLIC if wire[m]["family"] == "B"]

    def row(m):
        w = wire[m]
        return f"| [{m}](./{slug(m)}.mdx) | {w['default_baud']} | {w['frame_len']} | {w['unit']} | {kbrange(m)} |"

    idx = f'''---
id: index
title: Models with a published protocol
sidebar_label: Models
description: "22 ERDI laser rangefinder module models with a published UART protocol: frame format, baud rate, unit, pinout and code examples."
---

Twenty-two models have a published UART protocol and a page here: {len(A)} in family A and {len(B)} in family B. Every number on these pages comes from the ERDI datasheet for that model. The other models are listed on [Models with protocol on request](./more-models.md).

:::tip Which family?
Family A modules answer 8-byte `55 AA` commands at 115200 baud (you poll them). Family B modules stream `5C` frames at 460800 baud on their own. The unit of the distance field depends on the model, not the family: see [Units and out-of-range](../protocols/units-and-out-of-range.md).
:::

## Family A (55 AA, polled)

| Model | Baud | Frame (bytes) | Wire unit | Range |
|---|---|---|---|---|
{chr(10).join(row(m) for m in A)}

## Family B (5C, streaming)

| Model | Baud | Frame (bytes) | Wire unit | Range |
|---|---|---|---|---|
{chr(10).join(row(m) for m in B)}

Wire unit for family A is metres multiplied by 10; the table shows the unit of the physical value (`m`).
'''
    write(os.path.join(mdir, "index.md"), idx)

    # more models
    rest = [n for n in names if n["model"] not in PUBLIC]
    lines = ["| Model | Description |", "|---|---|"]
    for n in rest:
        lines.append(f"| [{n['model']}]({SITE}/models/{n['model'].lower()}/) | {n['title'].replace('|', '/')} |")
    more = f'''---
id: more-models
title: Models with protocol on request
sidebar_label: Other models
description: "ERDI laser rangefinder and laser source models whose UART protocol is provided on request."
---

The {len(rest)} models below do not have a public protocol document yet. We do not publish protocol details until they are confirmed against the manual and the delivered batch. If you are designing one of these into a product, tell us the model and your host platform and we send the protocol and connector details.

[Ask for the protocol](https://erdilrf.com/contact/?request_type=technical) &nbsp; tommy@erdimail.com &nbsp; +86 133 0819 5790

{chr(10).join(lines)}
'''
    write(os.path.join(mdir, "more-models.md"), more)

    # compatibility matrix
    head = "| Model | Family | ArduPilot Lua | ArduPilot native | ROS 2 | ESPHome | Arduino | Python |"
    sep = "|---|---|---|---|---|---|---|---|"
    mrows = []
    for m in PUBLIC:
        p = {a: b for a, b, _ in platform_rows(m)}
        mrows.append("| [{0}](../models/{1}.mdx) | {2} | {3} | {4} | {5} | {6} | {7} | {8} |".format(
            m, slug(m), wire[m]["family"], p["ArduPilot (Lua script)"], p["ArduPilot native driver"], p["ROS 2"],
            p["ESPHome / Home Assistant"], p["Arduino / PlatformIO"], p["Python (erdi-lrf)"]))
    write(os.path.join(ROOT, "docs", "compatibility", "_matrix.md"), "\n".join([head, sep] + mrows) + "\n")
    print("pages:", len(PUBLIC) + 3, "other models listed:", len(rest))


if __name__ == "__main__":
    main()
