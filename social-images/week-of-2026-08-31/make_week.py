#!/usr/bin/env python3
"""Big Sky Ledger — week of 2026-08-31 — seven survey plates, 1080x1080 @2x.

Destination in the repo: social-images/week-of-2026-08-31/make_week.py

Motifs this week (all fresh; checked against week-of-2026-07-27 / 08-03 / 08-10 / 08-17 / 08-24):
  I   MON  The Fall Window — a year of density columns, gold = the September-November span
  II  TUE  Open Traverse   — a survey loop with one leg unrun, gold = the line that closes it
  III WED  Snow Load       — roof section under accumulated hatch, gold = the heat that holds
  IV  THU  The Inventory   — an accession grid of a household, gold = the one that is kept
  V   FRI  The Gateway     — canyon walls converging on the park, gold = the mouth of the canyon
  VI  SAT  The Punch List  — house elevation with margin findings, gold = the one found first
  VII SUN  The Cadence     — two traces to the same mark, gold = the pace that can be held
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2
W = H = 1080 * S

FONT_DIRS = [
    "/root/.claude/skills/synced/canvas-design/canvas-fonts/",
    "/root/.claude/skills/canvas-design/canvas-fonts/",
    "/mnt/skills/examples/canvas-design/canvas-fonts/",
    os.path.expanduser("~/.claude/skills/canvas-design/canvas-fonts/"),
]

def _font_dir():
    for d in FONT_DIRS:
        if os.path.exists(os.path.join(d, "Italiana-Regular.ttf")):
            return d
    raise SystemExit("canvas-fonts not found; checked: " + ", ".join(FONT_DIRS))

F = _font_dir()

CREAM = (238, 231, 216)
GOLD  = (198, 163, 92)
GOLD_HI = (222, 190, 120)

def fonts():
    return {
        "display": ImageFont.truetype(F+"Italiana-Regular.ttf", 108*S),
        "display_sm": ImageFont.truetype(F+"Italiana-Regular.ttf", 76*S),
        "label": ImageFont.truetype(F+"Jura-Light.ttf", 30*S),
        "label_sm": ImageFont.truetype(F+"Jura-Light.ttf", 24*S),
        "mono": ImageFont.truetype(F+"DMMono-Regular.ttf", 22*S),
        "mono_sm": ImageFont.truetype(F+"DMMono-Regular.ttf", 19*S),
    }

def vgrad(w, h, top, bottom):
    img = Image.new("RGB", (w, h))
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] + (bottom[0]-top[0])*t)
        g = int(top[1] + (bottom[1]-top[1])*t)
        b = int(top[2] + (bottom[2]-top[2])*t)
        img.paste(Image.new("RGB", (w, 1), (r, g, b)), (0, y))
    return img

def alpha(c, a):
    return (c[0], c[1], c[2], a)

def letterspace(draw, xy, text, font, fill, tracking, anchor="ls"):
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text)-1)
    x, y = xy
    if anchor == "ms":
        x -= total / 2
    for ch, w_ in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w_ + tracking
    return total

def ls_width(draw, text, font, tracking):
    return sum(draw.textlength(ch, font=font) for ch in text) + tracking * (len(text)-1)

def ridge(seed, base, amp, freq, w):
    rnd = random.Random(seed)
    phases = [rnd.uniform(0, math.tau) for _ in range(4)]
    amps = [amp * f for f in (1.0, 0.55, 0.3, 0.16)]
    freqs = [freq * f for f in (1.0, 2.1, 4.3, 8.9)]
    pts = []
    for x in range(0, w+1, 4):
        y = base
        for a, fq, ph in zip(amps, freqs, phases):
            y -= a * (0.5 + 0.5*math.sin(fq * x / w * math.tau + ph)) ** 1.6
        pts.append((x, y))
    return pts

def draw_ridge_strata(dr, pts, y_floor, line_col, n=None, gap=7*S):
    max_off = y_floor - min(p[1] for p in pts)
    n = n or int(max_off // gap)
    if n <= 0:
        return
    for i in range(1, n+1):
        off = i * gap
        seg = [(x, min(y + off, y_floor)) for x, y in pts]
        fade = max(16, 118 - int(i * 100 / n))
        dr.line(seg, fill=alpha(line_col, fade), width=1*S)

def dashed(dr, pts, fill, width=1, dash=12*S, gap=9*S):
    if len(pts) < 2:
        return
    on = True
    budget = dash
    cur = pts[0]
    for nxt in pts[1:]:
        remaining = math.dist(cur, nxt)
        dx, dy = nxt[0]-cur[0], nxt[1]-cur[1]
        while remaining > 1e-9:
            step = min(budget, remaining)
            t = step / math.dist(cur, nxt) if math.dist(cur, nxt) else 0
            new = (cur[0] + dx*t, cur[1] + dy*t)
            if on:
                dr.line([cur, new], fill=fill, width=width)
            dx, dy = nxt[0]-new[0], nxt[1]-new[1]
            remaining -= step
            budget -= step
            cur = new
            if budget <= 1e-9:
                on = not on
                budget = dash if on else gap

def registration(dr, f, plate_no, coord, m=70*S):
    c = alpha(CREAM, 110)
    L = 26*S
    for (cx, cy, dx, dy) in [(m, m, 1, 1), (W-m, m, -1, 1), (m, H-m, 1, -1), (W-m, H-m, -1, -1)]:
        dr.line([(cx, cy), (cx+dx*L, cy)], fill=c, width=1*S)
        dr.line([(cx, cy), (cx, cy+dy*L)], fill=c, width=1*S)
    dr.text((W-m, m+14*S), plate_no, font=f["mono_sm"], fill=alpha(CREAM, 140), anchor="ra")
    dr.text((m, m+14*S), coord, font=f["mono_sm"], fill=alpha(CREAM, 140), anchor="la")
    for i in range(1, 10):
        x = m + (W - 2*m) * i / 10
        dr.line([(x, H-m), (x, H-m+8*S)], fill=alpha(CREAM, 70), width=1*S)

def footer(dr, f):
    y = H - 186*S
    letterspace(dr, (W/2, y), "RYAN BERNER", f["label"], alpha(CREAM, 225), 14*S, "ms")
    letterspace(dr, (W/2, y+46*S), "WEST AND COMPANY  ·  BROKERED BY EXP REALTY", f["label_sm"], alpha(CREAM, 130), 8*S, "ms")
    letterspace(dr, (W/2, y+84*S), "(406) 709-5404  ·  ANSWERED AROUND THE CLOCK", f["mono_sm"], alpha(CREAM, 115), 3*S, "ms")

SAFE_W = 880*S

def title_block(dr, f, kicker, word, mono_top):
    dr.text((W/2, 146*S), mono_top, font=f["mono_sm"], fill=alpha(CREAM, 130), anchor="ma")
    # kicker: shrink tracking, then the face, until it fits inside the safe width
    kf, track = f["label"], 15*S
    if ls_width(dr, kicker, kf, track) > SAFE_W:
        track = 9*S
    if ls_width(dr, kicker, kf, track) > SAFE_W:
        kf, track = f["label_sm"], 8*S
    letterspace(dr, (W/2, 178*S), kicker, kf, alpha(GOLD_HI, 235), track, "ms")
    wf = f["display"]
    if dr.textlength(word, font=wf) > SAFE_W:
        wf = f["display_sm"]
    dr.text((W/2, 214*S), word, font=wf, fill=CREAM, anchor="ma")

def finish(img, name):
    out = img.resize((1080, 1080), Image.LANCZOS)
    out.save(name, "PNG")
    print("saved", name)

def base_plate(top, bottom):
    return vgrad(W, H, top, bottom).convert("RGBA")

def grain(img, amount=6):
    g = Image.effect_noise((W//2, H//2), 18).resize((W, H)).convert("L")
    overlay = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    overlay.putalpha(g.point(lambda v: amount if v > 128 else 0))
    return Image.alpha_composite(img, overlay)

def glow_rect(img, box, col, a, blur):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).rectangle(box, fill=alpha(col, a))
    return Image.alpha_composite(img, g.filter(ImageFilter.GaussianBlur(blur)))

def glow_ellipse(img, box, col, a, blur):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse(box, fill=alpha(col, a))
    return Image.alpha_composite(img, g.filter(ImageFilter.GaussianBlur(blur)))

def ledger_rules(dr, y0, y1, step, x0=150*S, x1=930*S, a=12, avoid=()):
    y = y0
    while y <= y1:
        if not any(lo <= y <= hi for lo, hi in avoid):
            dr.line([(x0, y), (x1, y)], fill=alpha(CREAM, a), width=1*S)
        y += step


def ridge_inset(seed, base, amp, freq, x0, x1):
    """Ridge generated inside a margin so no stratum ever reaches a plate edge."""
    pts = ridge(seed, base, amp, freq, int(x1 - x0))
    return [(x + x0, y) for x, y in pts]


def section_ends(dr, pts, y_floor, a=58):
    """Close a strata block with clean vertical cuts, the way a section sample is drawn."""
    for p in (pts[0], pts[-1]):
        dr.line([(p[0], p[1]), (p[0], y_floor)], fill=alpha(CREAM, a), width=1*S)

def tally_run(dr, x0, x1, y, col, a, step=14*S, h=26*S, width=1):
    n = int((x1 - x0) // step)
    for i in range(n):
        x = x0 + i*step
        if (i + 1) % 5 == 0:
            dr.line([(x - 4*step - 4*S, y + 3*S), (x + 4*S, y - h - 3*S)],
                    fill=alpha(col, a), width=width*S)
        else:
            dr.line([(x, y), (x, y - h)], fill=alpha(col, a), width=width*S)
    return x0 + n*step

def home(dr, cx, base, hw, hh, peak, col, a, w=2, fill=None):
    x0, y0 = cx - hw/2, base - hh
    dr.polygon([(x0 - hw*0.09, y0), (cx, y0 - peak), (x0 + hw*1.09, y0)],
               fill=fill, outline=alpha(col, a))
    dr.rectangle([x0, y0, x0 + hw, base], fill=fill, outline=alpha(col, a), width=w*S)

def in_poly(pt, poly):
    x, y = pt
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi:
            inside = not inside
        j = i
    return inside



def qbez(p0, p1, p2, n=48):
    """Quadratic bezier as a polyline."""
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append((u*u*p0[0] + 2*u*t*p1[0] + t*t*p2[0],
                    u*u*p0[1] + 2*u*t*p1[1] + t*t*p2[1]))
    return pts


def hatch_column(dr, cx, base, top, half, col, a, step=6*S):
    """A column built from fine horizontal strokes — density, never a solid bar."""
    y = base
    n = 0
    while y > top:
        w = half * (0.82 + 0.18 * ((n % 3) / 2))
        dr.line([(cx - w, y), (cx + w, y)], fill=alpha(col, a), width=1*S)
        y -= step
        n += 1


# ------------------------------------------- PL. I — MON — THE FALL WINDOW (seasonality)
def plate_fallwindow():
    img = base_plate((13, 19, 31), (24, 33, 48))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()

    axis_y = 812*S
    x0, x1 = 176*S, 916*S
    ledger_rules(dr, 452*S, 764*S, 52*S, 176*S, 916*S, 10)

    months = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    # relative depth of each column — the shape of a Flathead selling year
    depth = [0.24, 0.28, 0.42, 0.62, 0.82, 1.00, 0.96, 0.86, 0.72, 0.58, 0.40, 0.26]
    span = (x1 - x0) / 12
    half = span * 0.30
    top_reach = 300*S

    fall = (8, 9, 10)  # SEP OCT NOV
    for i, (m, d) in enumerate(zip(months, depth)):
        cx = x0 + span * (i + 0.5)
        a = 74 if i in fall else 46
        hatch_column(dr, cx, axis_y - 6*S, axis_y - 6*S - top_reach * d, half, CREAM, a)
        dr.line([(cx - half, axis_y - 6*S - top_reach * d), (cx + half, axis_y - 6*S - top_reach * d)],
                fill=alpha(CREAM, 150 if i in fall else 95), width=1*S)
        dr.text((cx, axis_y + 22*S), m, font=f["mono_sm"],
                fill=alpha(CREAM, 165 if i in fall else 100), anchor="ma")

    dr.line([(x0, axis_y), (x1, axis_y)], fill=alpha(CREAM, 150), width=2*S)
    for i in range(13):
        x = x0 + span * i
        dr.line([(x, axis_y), (x, axis_y + 10*S)], fill=alpha(CREAM, 80), width=1*S)
    dr.text((x0, 424*S), "SHOWING ACTIVITY · RELATIVE", font=f["mono_sm"],
            fill=alpha(CREAM, 118), anchor="ld")

    # the window — gold, spent once
    gx0 = x0 + span * 8
    gx1 = x0 + span * 11
    gy = 452*S
    img = glow_rect(img, [gx0 - 16*S, gy - 20*S, gx1 + 16*S, gy + 24*S], GOLD, 52, 26*S)
    dr = ImageDraw.Draw(img, "RGBA")
    dr.line([(gx0, gy), (gx1, gy)], fill=alpha(GOLD_HI, 240), width=3*S)
    for e in (gx0, gx1):
        dr.line([(e, gy), (e, gy + 20*S)], fill=alpha(GOLD_HI, 240), width=3*S)
    dr.text(((gx0 + gx1) / 2, gy - 34*S), "THE FALL WINDOW", font=f["mono"],
            fill=alpha(GOLD_HI, 235), anchor="md")

    title_block(dr, f, "FLATHEAD VALLEY MARKET UPDATE", "The Fall Window", "LATE AUGUST · 2026")
    registration(dr, f, "PL. I", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-1-mon-fallwindow.png")


# ------------------------------------------- PL. II — TUE — OPEN TRAVERSE (no cooperation)
def plate_opentraverse():
    img = base_plate((14, 17, 29), (26, 30, 44))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()

    A = (238*S, 742*S)
    B = (300*S, 468*S)
    C = (686*S, 434*S)
    D = (838*S, 700*S)

    # the ground the traverse encloses — faint stipple, only where the loop is run
    rnd = random.Random(17)
    for yy in range(452, 742, 12):
        for xx in range(250, 840, 12):
            p = (xx*S, yy*S)
            if in_poly(p, [A, B, C, D]) and rnd.random() < 0.55:
                dr.line([p, (p[0], p[1] + 3*S)], fill=alpha(CREAM, 26), width=1*S)

    legs = [
        (A, B, "N 12°04' E   274.8'", (-22*S, 0), "rm"),
        (B, C, "N 84°57' E   387.5'", (0, -22*S), "md"),
        (C, D, "S 29°38' E   306.1'", (26*S, 0), "lm"),
    ]
    for p, q, lab, (ox, oy), anc in legs:
        dr.line([p, q], fill=alpha(CREAM, 190), width=2*S)
        mx, my = (p[0]+q[0])/2, (p[1]+q[1])/2
        dr.text((mx + ox, my + oy), lab, font=f["mono_sm"], fill=alpha(CREAM, 122), anchor=anc)

    for (px, py), lab, below in ((A, "STA. 1", True), (B, "STA. 2", False), (C, "STA. 3", False), (D, "STA. 4", True)):
        dr.ellipse([px-13*S, py-13*S, px+13*S, py+13*S], outline=alpha(CREAM, 210), width=2*S)
        dr.line([(px-7*S, py), (px+7*S, py)], fill=alpha(CREAM, 200), width=1*S)
        dr.line([(px, py-7*S), (px, py+7*S)], fill=alpha(CREAM, 200), width=1*S)
        dr.text((px + (-26*S if px < 500*S else 26*S), py + 4*S), lab, font=f["mono_sm"],
                fill=alpha(CREAM, 140), anchor="rm" if px < 500*S else "lm") if below else \
        dr.text((px, py - 30*S), lab, font=f["mono_sm"], fill=alpha(CREAM, 140), anchor="md")

    dr.text((916*S, 398*S), "ONE LEG UNRUN", font=f["mono_sm"],
            fill=alpha(CREAM, 120), anchor="ra")

    # the leg that closes the loop — gold, spent once
    img = glow_rect(img, [A[0]-34*S, A[1]-30*S, D[0]+34*S, D[1]+56*S], GOLD, 40, 30*S)
    dr = ImageDraw.Draw(img, "RGBA")
    dashed(dr, [D, A], alpha(GOLD_HI, 245), width=3*S, dash=15*S, gap=10*S)
    for (px, py) in (A, D):
        dr.ellipse([px-7*S, py-7*S, px+7*S, py+7*S], fill=GOLD_HI)
    dr.text((538*S, 800*S), "THE LINE THAT CLOSES IT", font=f["mono"],
            fill=alpha(GOLD_HI, 232), anchor="ma")

    title_block(dr, f, "DIVORCE · WHEN COOPERATION STOPS", "Open Traverse", "BOTH SIDES · ONE PROCESS")
    registration(dr, f, "PL. II", "48.20° N   114.32° W")
    footer(dr, f)
    finish(grain(img), "plate-2-tue-opentraverse.png")


# ------------------------------------------- PL. III — WED — SNOW LOAD (winter readiness)
def plate_snowload():
    img = base_plate((12, 18, 30), (22, 32, 46))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()

    ground = 792*S
    cx = 540*S
    hw = 268*S
    eave = 668*S
    peak = 500*S
    L = (cx - hw, eave)
    R = (cx + hw, eave)
    P = (cx, peak)

    # the accumulation on the roof — fine strokes stacked off the pitch
    for side in (-1, 1):
        p0 = (cx, peak)
        p1 = (cx + side*hw, eave)
        for k in range(1, 15):
            off = k * 5*S
            fade = max(14, 96 - k*6)
            dr.line([(p0[0] + side*4*S, p0[1] - off), (p1[0] - side*10*S, p1[1] - off)],
                    fill=alpha(CREAM, fade), width=1*S)

    # the section itself
    dr.line([L, P], fill=alpha(CREAM, 205), width=2*S)
    dr.line([P, R], fill=alpha(CREAM, 205), width=2*S)
    dr.line([(L[0], eave), (L[0], ground)], fill=alpha(CREAM, 175), width=2*S)
    dr.line([(R[0], eave), (R[0], ground)], fill=alpha(CREAM, 175), width=2*S)
    dr.line([(L[0]-26*S, eave), (L[0], eave)], fill=alpha(CREAM, 150), width=2*S)
    dr.line([(R[0], eave), (R[0]+26*S, eave)], fill=alpha(CREAM, 150), width=2*S)
    dr.line([(150*S, ground), (930*S, ground)], fill=alpha(CREAM, 110), width=1*S)

    # interior — the unheated volume, hatched thin
    for yy in range(int(eave + 16*S), int(ground - 6*S), int(15*S)):
        dr.line([(L[0]+14*S, yy), (R[0]-14*S, yy)], fill=alpha(CREAM, 16), width=1*S)

    # load ticks down the left pitch
    for k in range(1, 9):
        t = k / 9
        px = L[0] + (P[0]-L[0]) * t
        py = L[1] + (P[1]-L[1]) * t
        dr.line([(px, py - 78*S), (px, py - 62*S)], fill=alpha(CREAM, 70), width=1*S)
    dr.text((300*S, 402*S), "LOAD · ACCUMULATED", font=f["mono_sm"], fill=alpha(CREAM, 120), anchor="la")
    dr.text((L[0]-34*S, eave), "EAVE", font=f["mono_sm"], fill=alpha(CREAM, 115), anchor="rm")
    dr.text((R[0]+34*S, ground - 16*S), "GRADE", font=f["mono_sm"], fill=alpha(CREAM, 115), anchor="ld")

    # the heat that holds — gold, spent once: the flue through the ridge
    fx = cx + 96*S
    t = (fx - cx) / hw
    roof_y = peak + (eave - peak) * t
    img = glow_rect(img, [fx-46*S, 400*S, fx+46*S, roof_y+30*S], GOLD, 54, 26*S)
    dr = ImageDraw.Draw(img, "RGBA")
    dr.rectangle([fx-13*S, 432*S, fx+13*S, roof_y + 6*S], outline=alpha(GOLD_HI, 240), width=3*S)
    dr.line([(fx-22*S, 432*S), (fx+22*S, 432*S)], fill=alpha(GOLD_HI, 240), width=3*S)
    for k in range(3):
        yy = 468*S + k*44*S
        dr.line([(fx-13*S, yy), (fx+13*S, yy)], fill=alpha(GOLD, 150), width=1*S)
    dr.line([(fx + 34*S, 470*S), (fx + 118*S, 470*S)], fill=alpha(GOLD_HI, 170), width=1*S)
    dr.text((fx + 128*S, 470*S), "THE HEAT THAT HOLDS", font=f["mono"],
            fill=alpha(GOLD_HI, 232), anchor="lm")

    title_block(dr, f, "BUYER BRIEF · BEFORE THE SNOW", "Snow Load", "SEPTEMBER WALKTHROUGH")
    registration(dr, f, "PL. III", "48.25° N   114.19° W")
    footer(dr, f)
    finish(grain(img), "plate-3-wed-snowload.png")


# ------------------------------------------- PL. IV — THU — THE INVENTORY (clearing out, dusk)
def plate_inventory():
    img = base_plate((26, 20, 26), (48, 34, 33))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()

    cols, rows = 8, 3
    box = 60*S
    gx, gy = 44*S, 58*S
    grid_w = cols*box + (cols-1)*gx
    x0 = (W - grid_w) / 2
    y0 = 470*S

    dr.line([(x0 - 14*S, y0 - 36*S), (x0 + grid_w + 14*S, y0 - 36*S)],
            fill=alpha(CREAM, 105), width=1*S)
    dr.text((x0 - 14*S, y0 - 46*S), "ACCESSION", font=f["mono_sm"], fill=alpha(CREAM, 128), anchor="ld")

    keep = (5, 1)  # col, row of the one that stays
    rnd = random.Random(31)
    for r in range(rows):
        for c in range(cols):
            bx = x0 + c*(box+gx)
            by = y0 + r*(box+gy)
            if (c, r) == keep:
                continue
            dr.rectangle([bx, by, bx+box, by+box], outline=alpha(CREAM, 92), width=1*S)
            # each item marked by hand — a few thin strokes, never a fill
            for k in range(rnd.randint(2, 5)):
                yy = by + 13*S + k*11*S
                if yy < by + box - 9*S:
                    dr.line([(bx + 9*S, yy), (bx + box - 9*S - rnd.randint(0, 15)*S, yy)],
                            fill=alpha(CREAM, rnd.randint(24, 46)), width=1*S)
            dr.text((bx + box/2, by + box + 10*S), "%02d" % (r*cols + c + 1),
                    font=f["mono_sm"], fill=alpha(CREAM, 78), anchor="ma")

    # the one that is kept — gold, spent once (annotated up on the header rule, never over the grid)
    kx = x0 + keep[0]*(box+gx)
    ky = y0 + keep[1]*(box+gy)
    img = glow_rect(img, [kx-26*S, ky-26*S, kx+box+26*S, ky+box+26*S], GOLD, 62, 28*S)
    dr = ImageDraw.Draw(img, "RGBA")
    dr.rectangle([kx, ky, kx+box, ky+box], outline=alpha(GOLD_HI, 245), width=3*S)
    home(dr, kx + box/2, ky + box - 16*S, 32*S, 20*S, 15*S, GOLD_HI, 235, 2, fill=None)
    dr.text((kx + box/2, ky + box + 10*S), "%02d" % (keep[1]*cols + keep[0] + 1),
            font=f["mono_sm"], fill=alpha(GOLD_HI, 230), anchor="ma")

    gold_lab = "ONE KEPT"
    gw = dr.textlength(gold_lab, font=f["mono"])
    dr.text((x0 + grid_w + 14*S, y0 - 46*S), gold_lab, font=f["mono"],
            fill=alpha(GOLD_HI, 235), anchor="rd")
    dr.text((x0 + grid_w + 14*S - gw - 16*S, y0 - 46*S), "024 ITEMS  ·", font=f["mono_sm"],
            fill=alpha(CREAM, 128), anchor="rd")

    title_block(dr, f, "ESTATE · CLEARING THE HOUSE", "The Inventory", "THE PART NOBODY PLANS FOR")
    registration(dr, f, "PL. IV", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-4-thu-inventory.png")


# ------------------------------------------- PL. V — FRI — THE GATEWAY (Columbia Falls / canyon)
def plate_gateway():
    img = base_plate((12, 21, 31), (21, 34, 45))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()

    horizon = 430*S
    floor = 824*S
    gap_l, gap_r = 494*S, 586*S

    # canyon walls — nested contours converging on the mouth
    for side, sgn in ((0, -1), (1, 1)):
        for k in range(13):
            t = k / 12
            start_x = (150*S if sgn < 0 else 930*S) + sgn * -1 * (t * 118*S)
            end_x = (gap_l if sgn < 0 else gap_r) + sgn * (t * 26*S)
            ctrl = ((start_x + end_x)/2 + sgn * 96*S, horizon + 148*S + t*126*S)
            pts = qbez((start_x, floor), ctrl, (end_x, horizon + 34*S + t*10*S))
            fade = max(18, 128 - k*8)
            dr.line(pts, fill=alpha(CREAM, fade), width=1*S)

    dr.line([(150*S, floor), (930*S, floor)], fill=alpha(CREAM, 95), width=1*S)
    for xx in range(160, 930, 20):
        dr.line([(xx*S, floor + 3*S), (xx*S - 7*S, floor + 12*S)], fill=alpha(CREAM, 34), width=1*S)

    # the river — a double line down the floor of the canyon
    for off in (-13*S, 13*S):
        pts = qbez((540*S + off*2.6, floor + 4*S), (508*S + off*1.6, 690*S), (536*S + off*0.5, horizon + 60*S))
        dr.line(pts, fill=alpha(CREAM, 128), width=1*S)
    for k in range(9):
        t = 0.08 + k*0.098
        y = floor - t * (floor - horizon - 70*S)
        wgt = 11*S * (1 - t*0.7)
        dr.line([(538*S - wgt, y), (538*S + wgt, y)], fill=alpha(CREAM, 40), width=1*S)
    dr.text((540*S, floor + 24*S), "MIDDLE FORK", font=f["mono_sm"], fill=alpha(CREAM, 128), anchor="ma")
    dr.text((904*S, floor + 24*S), "U.S. 2", font=f["mono_sm"], fill=alpha(CREAM, 115), anchor="ra")

    # the mouth of the canyon — gold, spent once
    img = glow_rect(img, [gap_l - 26*S, horizon - 26*S, gap_r + 26*S, horizon + 108*S], GOLD, 58, 30*S)
    dr = ImageDraw.Draw(img, "RGBA")
    dr.line([(gap_l, horizon + 96*S), (gap_l, horizon + 4*S)], fill=alpha(GOLD_HI, 240), width=3*S)
    dr.line([(gap_r, horizon + 96*S), (gap_r, horizon + 4*S)], fill=alpha(GOLD_HI, 240), width=3*S)
    dr.line([(gap_l - 16*S, horizon + 4*S), (gap_r + 16*S, horizon + 4*S)], fill=alpha(GOLD_HI, 240), width=3*S)
    dr.line([(gap_l + 14*S, horizon + 40*S), (gap_r - 14*S, horizon + 40*S)], fill=alpha(GOLD, 120), width=1*S)
    dr.text((540*S, horizon - 22*S), "WEST ENTRANCE", font=f["mono"],
            fill=alpha(GOLD_HI, 234), anchor="md")

    title_block(dr, f, "COLUMBIA FALLS & THE CANYON", "The Gateway", "THE GLACIER SIDE")
    registration(dr, f, "PL. V", "48.37° N   114.18° W")
    footer(dr, f)
    finish(grain(img), "plate-5-fri-gateway.png")


# ------------------------------------------- PL. VI — SAT — THE PUNCH LIST (pre-listing inspection)
def plate_punchlist():
    img = base_plate((13, 19, 31), (24, 33, 48))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()

    # ledger texture stays on the drawing side; the findings column is left clean
    ledger_rules(dr, 430*S, 828*S, 48*S, 156*S, 566*S, 9)

    ground = 792*S
    cx, hw = 352*S, 152*S
    eave, peak = 636*S, 506*S

    dr.line([(cx-hw-18*S, eave), (cx, peak)], fill=alpha(CREAM, 200), width=2*S)
    dr.line([(cx, peak), (cx+hw+18*S, eave)], fill=alpha(CREAM, 200), width=2*S)
    dr.rectangle([cx-hw, eave, cx+hw, ground], outline=alpha(CREAM, 190), width=2*S)
    for yy in range(int(eave+16*S), int(ground-10*S), int(16*S)):
        dr.line([(cx-hw+12*S, yy), (cx+hw-12*S, yy)], fill=alpha(CREAM, 17), width=1*S)
    dr.rectangle([cx-104*S, eave+40*S, cx-40*S, eave+104*S], outline=alpha(CREAM, 135), width=1*S)
    dr.rectangle([cx+34*S, ground-92*S, cx+90*S, ground], outline=alpha(CREAM, 150), width=2*S)
    dr.line([(156*S, ground), (cx+hw+72*S, ground)], fill=alpha(CREAM, 108), width=1*S)
    for xx in range(164, int((cx+hw+66*S)/S), 18):
        dr.line([(xx*S, ground + 3*S), (xx*S - 7*S, ground + 12*S)], fill=alpha(CREAM, 32), width=1*S)

    # findings ruled into the right-hand column; rows and anchors both run top to bottom,
    # so no two leaders ever cross
    col_l, col_r = 620*S, 912*S
    items = [
        (470*S, (cx + 74*S, 566*S), "01", "ROOF & FLASHING"),
        (550*S, (cx + hw, 668*S), "02", "SIDING · WATER"),
        (630*S, (cx + hw - 46*S, 712*S), "03", "PANEL · CAPACITY"),
        (710*S, (cx + hw - 70*S, 770*S), "04", "CRAWLSPACE · PIPE"),
        (790*S, (cx + hw + 56*S, ground), "05", "GRADE & DRAINAGE"),
    ]
    for i, (ly, ap, num, lab) in enumerate(items):
        if i == 0:
            continue
        dr.line([ap, (col_l - 14*S, ly)], fill=alpha(CREAM, 58), width=1*S)
        dr.ellipse([ap[0]-5*S, ap[1]-5*S, ap[0]+5*S, ap[1]+5*S], outline=alpha(CREAM, 150), width=1*S)
        dr.line([(col_l - 14*S, ly), (col_r, ly)], fill=alpha(CREAM, 52), width=1*S)
        dr.text((col_l, ly - 10*S), num, font=f["mono_sm"], fill=alpha(CREAM, 118), anchor="ld")
        dr.text((col_r, ly - 10*S), lab, font=f["mono_sm"], fill=alpha(CREAM, 152), anchor="rd")

    # the one found first — gold, spent once
    ly, ap, num, lab = items[0]
    img = glow_ellipse(img, [ap[0]-76*S, ap[1]-62*S, ap[0]+76*S, ap[1]+62*S], GOLD, 52, 30*S)
    dr = ImageDraw.Draw(img, "RGBA")
    dr.line([ap, (col_l - 14*S, ly)], fill=alpha(GOLD_HI, 205), width=2*S)
    dr.ellipse([ap[0]-8*S, ap[1]-8*S, ap[0]+8*S, ap[1]+8*S], fill=GOLD_HI)
    dr.line([(col_l - 14*S, ly), (col_r, ly)], fill=alpha(GOLD_HI, 200), width=2*S)
    dr.text((col_l, ly - 12*S), num, font=f["mono"], fill=alpha(GOLD_HI, 238), anchor="ld")
    dr.text((col_r, ly - 12*S), lab, font=f["mono"], fill=alpha(GOLD_HI, 238), anchor="rd")
    dr.text((col_r, ly + 14*S), "FOUND FIRST", font=f["mono_sm"], fill=alpha(GOLD, 195), anchor="ra")

    title_block(dr, f, "SELLER BRIEF · PRE-LISTING INSPECTION", "The Punch List", "FIND IT BEFORE THEY DO")
    registration(dr, f, "PL. VI", "48.22° N   114.34° W")
    footer(dr, f)
    finish(grain(img), "plate-6-sat-punchlist.png")


# ------------------------------------------- PL. VII — SUN — THE CADENCE (slow is smooth)
def plate_cadence():
    img = base_plate((10, 14, 24), (24, 30, 44))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()

    x0, x1 = 176*S, 856*S
    mark_x = 890*S
    top_y = 486*S
    bot_y = 692*S

    ledger_rules(dr, 452*S, 812*S, 46*S, 176*S, 890*S, 9,
                 avoid=[(462*S, 500*S), (606*S, 712*S), (746*S, 800*S)])

    # the closing mark
    dr.line([(mark_x, 442*S), (mark_x, 780*S)], fill=alpha(CREAM, 150), width=2*S)
    dr.text((mark_x, 800*S), "THE MARK", font=f["mono_sm"], fill=alpha(CREAM, 140), anchor="ma")

    # trace one — hurried: bursts and stalls, and it doesn't reach
    rnd = random.Random(5)
    dr.line([(x0, top_y), (798*S, top_y)], fill=alpha(CREAM, 70), width=1*S)
    x = x0
    bursts = [6*S, 7*S, 6*S, 44*S, 5*S, 6*S, 5*S, 6*S, 62*S, 8*S, 7*S, 34*S, 6*S, 5*S, 6*S,
              7*S, 52*S, 6*S, 5*S, 7*S, 6*S, 40*S, 6*S, 7*S, 5*S, 6*S, 28*S, 7*S, 6*S]
    for step in bursts:
        if x > 796*S:
            break
        h = 30*S if step < 12*S else 16*S
        dr.line([(x, top_y), (x, top_y - h)], fill=alpha(CREAM, 118 if step < 12*S else 62), width=1*S)
        x += step
    dr.line([(798*S, top_y - 12*S), (798*S, top_y + 12*S)], fill=alpha(CREAM, 90), width=1*S)
    dashed(dr, [(798*S, top_y), (mark_x - 6*S, top_y)], alpha(CREAM, 60), width=1*S, dash=7*S, gap=8*S)
    dr.text((x0, top_y - 54*S), "HURRIED · MOTION WITHOUT SEQUENCE", font=f["mono_sm"],
            fill=alpha(CREAM, 120), anchor="ld")

    # the elapsed axis
    ax = 760*S
    dr.line([(x0, ax), (mark_x, ax)], fill=alpha(CREAM, 110), width=1*S)
    for i in range(15):
        xx = x0 + (mark_x - x0) * i / 14
        major = i % 7 == 0
        dr.line([(xx, ax), (xx, ax + (12*S if major else 6*S))],
                fill=alpha(CREAM, 115 if major else 55), width=1*S)
    dr.text((x0, ax + 20*S), "CONTRACT", font=f["mono_sm"], fill=alpha(CREAM, 120), anchor="la")
    dr.text(((x0 + mark_x)/2, ax + 20*S), "ELAPSED", font=f["mono_sm"], fill=alpha(CREAM, 100), anchor="ma")

    # trace two — measured, evenly paced, arriving — gold, spent once
    img = glow_rect(img, [x0 - 20*S, bot_y - 58*S, mark_x + 20*S, bot_y + 26*S], GOLD, 46, 28*S)
    dr = ImageDraw.Draw(img, "RGBA")
    dr.line([(x0, bot_y), (mark_x, bot_y)], fill=alpha(GOLD_HI, 235), width=3*S)
    n = 22
    for i in range(n + 1):
        xx = x0 + (mark_x - x0) * i / n
        h = 34*S if i % 4 == 0 else 20*S
        dr.line([(xx, bot_y), (xx, bot_y - h)], fill=alpha(GOLD_HI, 235 if i % 4 == 0 else 165), width=2*S)
    dr.ellipse([mark_x-10*S, bot_y-10*S, mark_x+10*S, bot_y+10*S], fill=GOLD_HI)
    dr.text((x0, bot_y - 60*S), "MEASURED · THE PACE YOU CAN HOLD", font=f["mono"],
            fill=alpha(GOLD_HI, 232), anchor="ld")

    title_block(dr, f, "SLOW IS SMOOTH", "The Cadence", "SMOOTH IS FAST")
    registration(dr, f, "PL. VII", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-7-sun-cadence.png")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    plate_fallwindow(); plate_opentraverse(); plate_snowload(); plate_inventory()
    plate_gateway(); plate_punchlist(); plate_cadence()
