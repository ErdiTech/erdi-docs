"""Copy protocol and guide pages from ErdiTech/erdi-lrf-drivers/docs (single source of truth).

The pages are copied as CommonMark (`format: md`) with front matter added, relative links
rewritten to the new locations, and an "Edit on GitHub" URL pointing at the original file.
Run before every build.   python scripts/sync_repo_docs.py [path-to-erdi-lrf-drivers]
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = sys.argv[1] if len(sys.argv) > 1 else "D:/AgentWork/ERDI/erdi-lrf-drivers"
GH = "https://github.com/ErdiTech/erdi-lrf-drivers"

MAP = {  # source file -> (target path under docs/, sidebar_position, short description)
    "protocol-A-55AA.md": ("protocols/family-a-55aa.md", 1, "Family A protocol: 8-byte 55 AA command and reply frames, checksums, commands and status codes for ERDI laser rangefinder modules."),
    "protocol-B-5C.md": ("protocols/family-b-5c.md", 2, "Family B protocol: free-running 5C data frames, 5A command frames, units, out-of-range markers and checksum for ERDI laser rangefinder modules."),
    "uart-hardware-notes.md": ("guides/uart-hardware-notes.md", 1, "UART wiring notes for laser rangefinder modules: logic level versus supply voltage, grounding, cable length."),
    "field-troubleshooting.md": ("guides/field-troubleshooting.md", 2, "Field troubleshooting for UART laser rangefinder modules: no data, wrong distance, checksum errors."),
    "blind-zone-and-minimum-range.md": ("guides/blind-zone-and-minimum-range.md", 3, "Blind zone and minimum range of laser rangefinder modules and how to handle short readings."),
    "mixed-target-return-validation.md": ("guides/mixed-target-return-validation.md", 4, "Validating readings when several targets return a signal to a laser rangefinder module."),
    "request-response-association.md": ("guides/request-response-association.md", 5, "Matching replies to requests when polling a UART laser rangefinder module."),
    "evaluation-checklist.md": ("guides/evaluation-checklist.md", 6, "Evaluation checklist for a laser rangefinder module: what to measure on the bench before you design it in."),
    "905nm-vs-1535nm.md": ("guides/905nm-vs-1535nm.md", 7, "905 nm versus 1535 nm laser rangefinder modules: range, eye safety class, cost and when to pick which."),
    "vendor-host-tool.md": ("guides/vendor-host-tool.md", 8, "What the factory serial tool does with units, and how that relates to the module's frames."),
    "flight-controller-integration.md": ("guides/flight-controller-integration.md", 9, "Flight controller integration notes for UART laser rangefinder modules."),
}
LINKMAP = {k: v[0] for k, v in MAP.items()}
LINKMAP["models.md"] = "models/index.md"
LINKMAP["evidence/ardupilot-bench-20261105/README.md"] = None  # external


def fix_links(text, here):
    def rep(m):
        label, url = m.group(1), m.group(2)
        if re.match(r"^(https?:|#|mailto:)", url):
            return m.group(0)
        base = url.split("#")[0]
        frag = url[len(base):]
        if base in LINKMAP and LINKMAP[base]:
            rel = os.path.relpath(os.path.join("docs", LINKMAP[base]), os.path.join("docs", os.path.dirname(here)))
            return f"[{label}]({rel.replace(os.sep, '/')}{frag})"
        if base.startswith("evidence/"):
            return f"[{label}]({GH}/tree/main/docs/{os.path.dirname(base)})"
        if base.endswith((".svg", ".png", ".jpg")):
            return f"[{label}]({GH}/blob/main/docs/{base})"
        return f"[{label}]({GH}/blob/main/docs/{base}{frag})"
    return re.sub(r"\[([^\]]*)\]\(([^)]+)\)", rep, text)


NOTE_B = "\n> Models covered in the original document: LRF50H, LRF100H, LRF200H, LRF300H, LRF600H, LRF1500H, LRF22VB, LRF50VB. LRF10VB uses the same 4-byte `5C` frame in millimetres with out-of-range marker 65535, see its [model page](../models/lrf10vb.mdx).\n"


def main():
    for src, (dst, pos, desc) in MAP.items():
        text = open(os.path.join(SRC, "docs", src), encoding="utf-8").read()
        h1 = re.match(r"# (.+)\n", text)
        title = h1.group(1).strip() if h1 else src
        title = title.replace("`", "")
        body = fix_links(text, dst).replace(" — ", " - ").replace("—", "-")
        title = title.replace("—", "-")
        body = body.replace("✅", "Yes")
        if src == "protocol-B-5C.md":
            body = body.replace("\n\n", NOTE_B + "\n", 1) if False else body
        fm = (
            "---\n"
            f"title: \"{title}\"\n"
            f"sidebar_position: {pos}\n"
            f"description: \"{desc}\"\n"
            "format: md\n"
            f"custom_edit_url: {GH}/edit/main/docs/{src}\n"
            "---\n\n"
        )
        # insert the family-B note after the H1 block's first paragraph
        if src == "protocol-B-5C.md":
            parts = body.split("\n\n", 2)
            body = parts[0] + "\n\n" + parts[1] + "\n" + NOTE_B + "\n" + parts[2]
        out = os.path.join(ROOT, "docs", dst)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8", newline="\n").write(fm + body)
    print("synced", len(MAP))


if __name__ == "__main__":
    main()
