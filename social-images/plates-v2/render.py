#!/usr/bin/env python3
"""Plates v2 renderer — four-template social image system (adopted 2026-08-26).

Usage:
    python3 render.py week-YYYY-MM-DD.json              # render every plate in the spec
    python3 render.py week-YYYY-MM-DD.json plate-3-wed-snowload.png [...]
                                                        # re-render only the named file(s)

Spec format (JSON):
    {
      "outdir": "out/week-of-YYYY-MM-DD",
      "phone": "(406) 709-5404",          <- REQUIRED. Read POSITIONING.md; never hardcode.
      "plates": [
        {"file": "plate-1-mon-something.png",
         "template": "frontpage" | "bigsky" | "fieldnotes" | "signal",
         "vars": { ... per-template, see DESIGN-SYSTEM-V2.md ... }}
      ]
    }

Inline markup allowed inside any var value:
    \n                      line break
    [[circle]]...[[/circle]]  fieldnotes only: red hand-drawn circle (size via CIRCLE_W)
    [[strike]]...[[/strike]]  signal only: red strike-through
    [[gap]]                 fieldnotes LINES: one empty ruled line
    [[i]]...[[/i]]          italic (bigsky headline)

Output: 1080x1080 PNG, rendered @2x and downsampled, quantized to 256 colors
(~60-85 KB). Requires: `npm i` once in this folder (local fonts), playwright
with the preinstalled chromium, Pillow.
"""
import html
import io
import json
import os
import sys
import tempfile

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(HERE, "templates")

DEFAULTS = {
    "frontpage": {
        "TAG": "West and Company &middot; Flathead Valley",
        "KICKER": "",
        "HEADLINE": "",
        "DECK": "",
        "HEADLINE_SIZE": "96",
    },
    "bigsky": {
        "KICKER": "",
        "HEADLINE": "",
        "SUB": "",
        "HEADLINE_SIZE": "84",
    },
    "fieldnotes": {
        "TITLE": "",
        "LINES": "",
        "NOTE": "",
        "NOTE_TOP": "845",
        "CIRCLE_W": "auto",
        "PEN": "#C3271B",
    },
    "signal": {
        "KICKER": "",
        "LINE1": "",
        "LINE2": "",
        "SUB": "",
        "LINE1_SIZE": "92",
        "LINE2_SIZE": "92",
    },
}

RAW_KEYS = {"HEADLINE_SIZE", "LINE1_SIZE", "LINE2_SIZE", "NOTE_TOP", "CIRCLE_W", "PEN", "TAG"}


def markup(value: str) -> str:
    """Escape HTML then re-enable the small inline markup vocabulary."""
    s = html.escape(str(value), quote=False)
    s = s.replace("[[circle]]", '<span class="circle-me">').replace("[[/circle]]", "</span>")
    s = s.replace("[[strike]]", '<span class="strike">').replace("[[/strike]]", "</span>")
    s = s.replace("[[i]]", "<i>").replace("[[/i]]", "</i>")
    s = s.replace("[[gap]]", '<div class="gap"></div>')
    s = s.replace("\n", "<br>")
    return s


def build_html(template: str, vars_in: dict, phone: str) -> str:
    path = os.path.join(TEMPLATES, template + ".html")
    if not os.path.exists(path):
        raise SystemExit(f"unknown template '{template}' (expected one of {sorted(DEFAULTS)})")
    with open(path, encoding="utf-8") as f:
        doc = f.read()
    merged = dict(DEFAULTS[template])
    for k, v in vars_in.items():
        if isinstance(v, list):
            v = "\n".join(str(x) for x in v)
        merged[str(k)] = v
    merged.setdefault("PHONE", phone)
    for key, val in merged.items():
        rendered = str(val) if key in RAW_KEYS else markup(val)
        doc = doc.replace("{{%s}}" % key, rendered)
    leftovers = [t for t in DEFAULTS[template] if "{{%s}}" % t in doc]
    if leftovers:
        raise SystemExit(f"template '{template}': unfilled placeholders {leftovers}")
    return doc


def render_plate(page, template: str, vars_in: dict, phone: str, out_path: str) -> int:
    doc = build_html(template, vars_in, phone)
    # temp html must sit inside templates/ so _base.css and ../node_modules/ resolve
    fd, tmp = tempfile.mkstemp(suffix=".html", prefix=".render-", dir=TEMPLATES)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(doc)
        page.goto("file://" + tmp)
        page.evaluate("document.fonts.ready.then(() => {})")
        page.wait_for_timeout(120)
        png = page.screenshot(clip={"x": 0, "y": 0, "width": 1080, "height": 1080})
    finally:
        os.unlink(tmp)
    im = Image.open(io.BytesIO(png)).convert("RGB")
    if im.size != (1080, 1080):
        im = im.resize((1080, 1080), Image.LANCZOS)
    im.quantize(colors=256).save(out_path, optimize=True)
    return os.path.getsize(out_path)


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    spec_path = sys.argv[1]
    only = set(sys.argv[2:])
    with open(spec_path, encoding="utf-8") as f:
        spec = json.load(f)
    phone = spec.get("phone", "").strip()
    if not phone:
        raise SystemExit("spec is missing \"phone\" — read POSITIONING.md for the current office number")
    outdir = os.path.join(os.path.dirname(os.path.abspath(spec_path)), spec.get("outdir", "out"))
    os.makedirs(outdir, exist_ok=True)
    plates = spec.get("plates", [])
    if only:
        plates = [p for p in plates if p["file"] in only]
        missing = only - {p["file"] for p in plates}
        if missing:
            raise SystemExit(f"not in spec: {sorted(missing)}")
    if not plates:
        raise SystemExit("nothing to render")
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=2)
        for p in plates:
            out = os.path.join(outdir, p["file"])
            size = render_plate(page, p["template"], p.get("vars", {}), phone, out)
            print(f"  {p['file']:<38} {p['template']:<11} {size/1024:6.1f} KB")
        browser.close()
    print(f"done -> {outdir}")


if __name__ == "__main__":
    main()
