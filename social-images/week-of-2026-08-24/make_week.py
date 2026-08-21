#!/usr/bin/env python3
"""Big Sky Ledger — week of 2026-08-24 — seven survey plates, 1080x1080 @2x.

Motifs this week (all fresh; checked against week-of-2026-07-27 / 08-03 / 08-10 / 08-17):
  I   MON  The Ledger      — three tally runs, gold = the week-over-week difference
  II  TUE  Even Ground     — homestead over a measured bar, gold = the line that gets split
  III WED  The Corners     — surveyed parcel + monuments, gold = the recorded access easement
  IV  THU  Common Ground   — three stations triangulating one homestead (warm dusk variant)
  V   FRI  The Turning     — a stand of fine vertical strokes, one gold larch
  VI  SAT  The Plumb Line  — graduated rod + plumb bob, gold = the true reading
  VII SUN  First Light     — deep ridge strata + hour axis, gold = the band of first light
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


# ---------------------------------------------- PL. I — MON — THE LEDGER (rate math)
def plate_ledger():
    img = base_plate((13, 19, 31), (24, 33, 48))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    ledger_rules(dr, 400*S, 830*S, 46*S,
                 avoid=[(418*S, 448*S), (558*S, 588*S), (708*S, 738*S)])

    x0 = 170*S
    rows = [
        (500*S, 910*S, "6.67%   ONE WEEK AGO", 150),
        (640*S, 856*S, "6.65%   AUGUST 20", 190),
        (790*S, 800*S, "6.58%   ONE YEAR AGO", 90),
    ]
    for y, xe, lab, a in rows:
        dr.line([(x0, y), (930*S, y)], fill=alpha(CREAM, 40), width=1*S)
        dr.line([(x0, y), (xe, y)], fill=alpha(CREAM, min(190, a + 30)), width=2*S)
        tally_run(dr, x0 + 10*S, xe - 4*S, y - 6*S, CREAM, a)
        dr.text((x0, y - 68*S), lab, font=f["mono"], fill=alpha(CREAM, min(210, a + 60)), anchor="la")

    # the difference — gold, spent once: three strokes and a bracket
    y2 = 640*S
    img = glow_rect(img, [852*S, y2 - 58*S, 922*S, y2 + 40*S], GOLD, 60, 24*S)
    dr = ImageDraw.Draw(img, "RGBA")
    for i in range(3):
        x = 872*S + i*14*S
        dr.line([(x, y2 - 6*S), (x, y2 - 32*S)], fill=alpha(GOLD_HI, 240), width=2*S)
    dr.line([(864*S, y2 + 26*S), (912*S, y2 + 26*S)], fill=alpha(GOLD_HI, 230), width=2*S)
    for x in (864*S, 912*S):
        dr.line([(x, y2 + 26*S), (x, y2 + 16*S)], fill=alpha(GOLD_HI, 230), width=2*S)
    dr.text((912*S, y2 + 40*S), "WHAT THE DROP IS WORTH", font=f["mono"],
            fill=alpha(GOLD_HI, 230), anchor="ra")

    title_block(dr, f, "FLATHEAD VALLEY MARKET UPDATE", "The Ledger", "LATE AUGUST · 2026")
    registration(dr, f, "PL. I", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-1-mon-ledger.png")


# ---------------------------------------------- PL. II — TUE — EVEN GROUND (dividing equity)
def plate_evenground():
    img = base_plate((14, 17, 29), (26, 30, 44))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    ledger_rules(dr, 404*S, 512*S, 36*S, 190*S, 890*S, 11)

    ground = 566*S
    dr.line([(150*S, ground), (930*S, ground)], fill=alpha(CREAM, 120), width=1*S)
    home(dr, 540*S, ground, 176*S, 104*S, 74*S, CREAM, 205, fill=(16, 19, 31))
    for yy in range(int(ground - 92*S), int(ground - 8*S), int(13*S)):
        dr.line([(540*S - 78*S, yy), (540*S + 78*S, yy)], fill=alpha(CREAM, 22), width=1*S)
    dr.rectangle([540*S + 30*S, ground - 62*S, 540*S + 72*S, ground],
                 fill=(16, 19, 31), outline=alpha(CREAM, 160), width=2*S)

    # the measured bar
    bx0, bx1, by = 150*S, 930*S, 690*S
    dr.line([(bx0, by), (bx1, by)], fill=alpha(CREAM, 190), width=2*S)
    i = 0
    x = bx0
    while x <= bx1 + 1:
        L = 15*S if i % 5 == 0 else 8*S
        dr.line([(x, by), (x, by - L)], fill=alpha(CREAM, 95 if i % 5 == 0 else 55), width=1*S)
        x += 26*S; i += 1

    # what comes off the top, hatched away
    segs = [(bx0, 470*S, "PAYOFF"), (470*S, 566*S, "COSTS")]
    rnd = random.Random(9)
    for sx0, sx1, lab in segs:
        for xx in range(int(sx0), int(sx1), int(10*S)):
            dr.line([(xx, by + 4*S), (xx + 18*S, by + 40*S)], fill=alpha(CREAM, 30), width=1*S)
        dr.line([(sx0, by + 46*S), (sx1, by + 46*S)], fill=alpha(CREAM, 90), width=1*S)
        for e in (sx0, sx1):
            dr.line([(e, by + 46*S), (e, by + 38*S)], fill=alpha(CREAM, 90), width=1*S)
        dr.text(((sx0 + sx1) / 2, by + 54*S), lab, font=f["mono_sm"],
                fill=alpha(CREAM, 125), anchor="ma")

    # what's left
    nx0, nx1 = 566*S, bx1
    mid = (nx0 + nx1) / 2
    dr.line([(nx0, by + 92*S), (nx1, by + 92*S)], fill=alpha(CREAM, 130), width=1*S)
    for e in (nx0, nx1):
        dr.line([(e, by + 92*S), (e, by + 82*S)], fill=alpha(CREAM, 130), width=1*S)
    dr.text((mid, by + 100*S), "NET EQUITY", font=f["mono_sm"], fill=alpha(CREAM, 160), anchor="ma")

    # the split — gold, spent once
    img = glow_rect(img, [mid - 30*S, by - 80*S, mid + 30*S, by + 60*S], GOLD, 52, 26*S)
    dr = ImageDraw.Draw(img, "RGBA")
    dr.line([(mid, by - 62*S), (mid, by + 46*S)], fill=alpha(GOLD_HI, 240), width=3*S)
    d = 10*S
    dr.polygon([(mid, by - d*2 - 46*S), (mid + d, by - d - 46*S), (mid, by - 46*S),
                (mid - d, by - d - 46*S)], fill=GOLD_HI)
    dr.text((mid, by + 138*S), "THE ONLY NUMBER THAT GETS SPLIT", font=f["mono"],
            fill=alpha(GOLD_HI, 225), anchor="ma")

    title_block(dr, f, "DIVORCE · DIVIDING THE EQUITY", "Even Ground", "THREE NUMBERS · ONE COUNTS")
    registration(dr, f, "PL. II", "48.20° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-2-tue-evenground.png")


# ---------------------------------------------- PL. III — WED — THE CORNERS (raw land)
def plate_corners():
    img = base_plate((12, 18, 30), (22, 32, 44))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()

    poly = [(250*S, 446*S), (826*S, 480*S), (856*S, 722*S), (276*S, 694*S)]
    # interior — a faint dotted section grid
    rnd = random.Random(4)
    for yy in range(440, 730, 11):
        for xx in range(240, 870, 11):
            p = (xx*S, yy*S)
            if in_poly((p[0], p[1] + 9*S), poly) and in_poly(p, poly) and rnd.random() < 0.7:
                dr.line([p, (p[0], p[1] + 3*S)], fill=alpha(CREAM, 34), width=1*S)
    dr.line(poly + [poly[0]], fill=alpha(CREAM, 185), width=2*S)

    # corner monuments
    for (cx, cy) in poly:
        dr.ellipse([cx-12*S, cy-12*S, cx+12*S, cy+12*S], outline=alpha(CREAM, 210), width=2*S)
        dr.line([(cx-6*S, cy), (cx+6*S, cy)], fill=alpha(CREAM, 210), width=1*S)
        dr.line([(cx, cy-6*S), (cx, cy+6*S)], fill=alpha(CREAM, 210), width=1*S)

    dr.text((538*S, 402*S), "N 88°14' E   580.2'", font=f["mono_sm"], fill=alpha(CREAM, 130), anchor="ma")
    dr.text((240*S, 578*S), "248.6'", font=f["mono_sm"], fill=alpha(CREAM, 120), anchor="ra")
    dr.text((876*S, 604*S), "242.1'", font=f["mono_sm"], fill=alpha(CREAM, 120), anchor="la")
    dr.text((430*S, 740*S), "S 87°42' W   576.4'", font=f["mono_sm"], fill=alpha(CREAM, 130), anchor="ma")

    # the county road
    ry = 800*S
    dr.line([(120*S, ry), (960*S, ry)], fill=alpha(CREAM, 150), width=2*S)
    for xx in range(130, 960, 22):
        dr.line([(xx*S, ry + 3*S), (xx*S - 8*S, ry + 13*S)], fill=alpha(CREAM, 45), width=1*S)
    dr.text((150*S, ry + 22*S), "COUNTY ROAD", font=f["mono_sm"], fill=alpha(CREAM, 120), anchor="la")

    # the easement — gold, spent once: the only thing that makes the parcel a parcel
    ex = 700*S
    t = (ex - poly[3][0]) / (poly[2][0] - poly[3][0])
    ey = poly[3][1] + t * (poly[2][1] - poly[3][1])
    img = glow_rect(img, [ex - 30*S, ey - 16*S, ex + 30*S, ry + 16*S], GOLD, 46, 22*S)
    dr = ImageDraw.Draw(img, "RGBA")
    dashed(dr, [(ex, ry), (ex, ey)], alpha(GOLD_HI, 240), width=3*S, dash=13*S, gap=9*S)
    dr.ellipse([ex-9*S, ey-9*S, ex+9*S, ey+9*S], fill=GOLD_HI)
    dr.text((700*S, ry + 22*S), "LEGAL ACCESS · RECORDED", font=f["mono"],
            fill=alpha(GOLD_HI, 230), anchor="ma")

    title_block(dr, f, "BUYER BRIEF · RAW LAND", "The Corners", "BEFORE YOU BUY THE VIEW")
    registration(dr, f, "PL. III", "48.26° N   114.28° W")
    footer(dr, f)
    finish(grain(img), "plate-3-wed-corners.png")


# ---------------------------------------------- PL. IV — THU — COMMON GROUND (heirs, dusk)
def plate_commonground():
    img = base_plate((26, 20, 26), (48, 34, 33))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()

    stations = [((232*S, 492*S), "STATION I"), ((872*S, 500*S), "STATION II"), ((452*S, 786*S), "STATION III")]
    hx, hy = 604*S, 634*S

    # the network between the parties — faint
    pts = [p for p, _ in stations]
    for a_, b_ in ((0, 1), (1, 2), (2, 0)):
        dashed(dr, [pts[a_], pts[b_]], alpha(CREAM, 46), width=1*S, dash=9*S, gap=11*S)

    # sight lines, each holding on the same point
    for (px, py), _ in stations:
        d = math.dist((px, py), (hx, hy))
        t = (d - 96*S) / d
        dashed(dr, [(px, py), (px + (hx-px)*t, py + (hy-py)*t)],
               alpha(CREAM, 140), width=2*S, dash=12*S, gap=9*S)

    # station markers
    for (px, py), lab in stations:
        dr.ellipse([px-16*S, py-16*S, px+16*S, py+16*S], outline=alpha(CREAM, 205), width=2*S)
        t = 9*S
        dr.polygon([(px, py-t), (px+t*0.87, py+t*0.5), (px-t*0.87, py+t*0.5)], outline=alpha(CREAM, 205))
        dr.arc([px-30*S, py-30*S, px+30*S, py+30*S], 200, 265, fill=alpha(CREAM, 90), width=1*S)
        below = lab.endswith("III")
        dr.text((px, py + (32*S if below else -34*S)), lab, font=f["mono_sm"],
                fill=alpha(CREAM, 135), anchor="ma" if below else "md")

    # the house they all sight on — gold, spent once
    img = glow_ellipse(img, [hx-104*S, hy-104*S, hx+104*S, hy+104*S], GOLD, 54, 34*S)
    dr = ImageDraw.Draw(img, "RGBA")
    home(dr, hx, hy + 34*S, 108*S, 68*S, 50*S, GOLD_HI, 245, 2, fill=(30, 22, 25))
    dr.rectangle([hx - 12*S, hy + 34*S - 34*S, hx + 12*S, hy + 34*S],
                 outline=alpha(GOLD_HI, 230), width=2*S)
    dr.line([(hx + 62*S, hy + 6*S), (hx + 126*S, hy + 6*S)], fill=alpha(GOLD_HI, 180), width=1*S)
    dr.text((hx + 136*S, hy + 6*S), "HELD IN COMMON", font=f["mono"],
            fill=alpha(GOLD_HI, 230), anchor="lm")

    title_block(dr, f, "ESTATE · WHEN HEIRS DISAGREE", "Common Ground", "THREE STATIONS · ONE POINT")
    registration(dr, f, "PL. IV", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-4-thu-commonground.png")


# ---------------------------------------------- PL. V — FRI — THE TURNING (September)
def plate_turning():
    img = base_plate((12, 22, 32), (20, 36, 46))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()

    r1 = ridge_inset(64, 566*S, 74*S, 2.3, 150*S, 930*S)
    draw_ridge_strata(dr, r1, 706*S, CREAM, n=16, gap=9*S)
    dr.line(r1, fill=alpha(CREAM, 95), width=1*S)
    for p in (r1[0], r1[-1]):
        dr.line([p, (p[0], min(p[1] + 144*S, 706*S))], fill=alpha(CREAM, 34), width=1*S)

    def conifer(x, base, h, a, w=1):
        dr.line([(x, base), (x, base - h)], fill=alpha(CREAM, a), width=w*S)
        n = max(4, int(h / (15*S)))
        for i in range(n):
            t = (i + 1) / (n + 1)
            yy = base - h * (1 - t) - 6*S
            spread = 2*S + 8*S * t
            dr.line([(x, yy), (x - spread, yy + spread*0.9)], fill=alpha(CREAM, int(a*0.75)), width=1*S)
            dr.line([(x, yy), (x + spread, yy + spread*0.9)], fill=alpha(CREAM, int(a*0.75)), width=1*S)

    rnd = random.Random(88)
    bands = [(724*S, 52, 54*S, 84*S, 17*S), (766*S, 84, 70*S, 108*S, 20*S), (802*S, 126, 88*S, 140*S, 24*S)]
    for base, a, hmin, hmax, step in bands:
        x = 156*S
        while x < 926*S:
            conifer(x, base + rnd.randint(-3, 3)*S, rnd.uniform(hmin, hmax), a)
            x += step + rnd.randint(-3, 4)*S

    dr.line([(150*S, 812*S), (930*S, 812*S)], fill=alpha(CREAM, 90), width=1*S)

    # the one that turns — gold, spent once
    gx, gbase = 628*S, 800*S
    img = glow_ellipse(img, [gx-92*S, gbase-206*S, gx+92*S, gbase+30*S], GOLD, 52, 32*S)
    dr = ImageDraw.Draw(img, "RGBA")
    h = 152*S
    dr.line([(gx, gbase), (gx, gbase - h)], fill=alpha(GOLD_HI, 245), width=2*S)
    n = 11
    for i in range(n):
        t = (i + 1) / (n + 1)
        yy = gbase - h * (1 - t) - 6*S
        spread = 3*S + 13*S * t
        dr.line([(gx, yy), (gx - spread, yy + spread*0.9)], fill=alpha(GOLD_HI, 225), width=2*S)
        dr.line([(gx, yy), (gx + spread, yy + spread*0.9)], fill=alpha(GOLD_HI, 225), width=2*S)
    dr.text((gx, 828*S), "THE LARCH TURN · LATE SEPTEMBER", font=f["mono"],
            fill=alpha(GOLD_HI, 228), anchor="ma")

    title_block(dr, f, "SEPTEMBER IN THE FLATHEAD", "The Turning", "AFTER THE CROWDS GO HOME")
    registration(dr, f, "PL. V", "48.31° N   114.15° W")
    footer(dr, f)
    finish(grain(img), "plate-5-fri-turning.png")


# ---------------------------------------------- PL. VI — SAT — THE PLUMB LINE (pricing)
def plate_plumbline():
    img = base_plate((13, 19, 31), (24, 33, 48))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()

    ledger_rules(dr, 412*S, 836*S, 42*S, 170*S, 910*S, 10,
                 avoid=[(438*S, 468*S), (632*S, 660*S), (788*S, 816*S)])

    rod_x, top_y, bot_y = 560*S, 402*S, 836*S
    dr.line([(rod_x, top_y), (rod_x, bot_y)], fill=alpha(CREAM, 170), width=2*S)
    i = 0
    y = top_y
    while y <= bot_y:
        L = 20*S if i % 5 == 0 else 11*S
        dr.line([(rod_x, y), (rod_x + L, y)], fill=alpha(CREAM, 100 if i % 5 == 0 else 55), width=1*S)
        y += 14*S; i += 1

    # the suspension and the bob
    bob_top, tip = 578*S, 646*S
    dr.line([(620*S, top_y + 6*S), (620*S, bob_top)], fill=alpha(CREAM, 165), width=1*S)
    dr.ellipse([620*S-5*S, top_y, 620*S+5*S, top_y+10*S], fill=alpha(CREAM, 190))

    for yy, lab in ((452*S, "ASPIRATIONAL"), (802*S, "CHASED DOWN")):
        dr.line([(468*S, yy), (rod_x - 8*S, yy)], fill=alpha(CREAM, 70), width=1*S)
        dr.text((458*S, yy), lab, font=f["mono_sm"], fill=alpha(CREAM, 130), anchor="rm")

    # the chase — faint stair of reductions, right of the line
    sx, sy = 686*S, 566*S
    for k in range(5):
        x0_, y0_ = sx + k*46*S, sy + k*44*S
        dashed(dr, [(x0_, y0_), (x0_ + 42*S, y0_)], alpha(CREAM, 80), width=1*S, dash=8*S, gap=7*S)
        dashed(dr, [(x0_ + 42*S, y0_), (x0_ + 42*S, y0_ + 44*S)], alpha(CREAM, 55), width=1*S, dash=8*S, gap=7*S)
    dr.text((802*S, 822*S), "THE CHASE", font=f["mono_sm"], fill=alpha(CREAM, 120), anchor="ma")

    # the reading — gold, spent once
    img = glow_ellipse(img, [620*S-84*S, tip-116*S, 620*S+84*S, tip+52*S], GOLD, 56, 30*S)
    dr = ImageDraw.Draw(img, "RGBA")
    dr.polygon([(620*S-16*S, bob_top), (620*S+16*S, bob_top),
                (620*S+16*S, bob_top+26*S), (620*S, tip), (620*S-16*S, bob_top+26*S)],
               fill=alpha(GOLD, 210), outline=GOLD_HI)
    dr.rectangle([620*S-7*S, bob_top-13*S, 620*S+7*S, bob_top], outline=GOLD_HI, width=2*S)
    dr.line([(470*S, tip), (556*S, tip)], fill=alpha(GOLD_HI, 235), width=2*S)
    dr.text((458*S, tip), "TRUE", font=f["mono"], fill=alpha(GOLD_HI, 235), anchor="rm")

    title_block(dr, f, "SELLER BRIEF · PRICING", "The Plumb Line", "THE FIRST TWO WEEKS TELL YOU")
    registration(dr, f, "PL. VI", "48.23° N   114.33° W")
    footer(dr, f)
    finish(grain(img), "plate-6-sat-plumbline.png")


# ---------------------------------------------- PL. VII — SUN — FIRST LIGHT (discipline)
def plate_firstlight():
    img = base_plate((10, 14, 24), (24, 30, 44))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()

    r1 = ridge_inset(77, 700*S, 95*S, 2.0, 130*S, 950*S)
    crest = min(p[1] for p in r1)
    band_y = crest - 48*S

    # the band of first light — gold, spent once, behind the ridge
    img = glow_rect(img, [110*S, band_y - 18*S, 970*S, band_y + 18*S], GOLD, 58, 26*S)
    dr = ImageDraw.Draw(img, "RGBA")
    dr.line([(150*S, band_y), (930*S, band_y)], fill=alpha(GOLD_HI, 235), width=3*S)
    dr.line([(230*S, band_y + 16*S), (850*S, band_y + 16*S)], fill=alpha(GOLD, 110), width=1*S)
    dr.text((930*S, band_y - 40*S), "FIRST LIGHT · 0530", font=f["mono"],
            fill=alpha(GOLD_HI, 230), anchor="ra")

    draw_ridge_strata(dr, r1, 790*S, CREAM, gap=7*S)
    dr.line(r1, fill=alpha(CREAM, 150), width=1*S)
    section_ends(dr, r1, 790*S, 70)
    dr.line([(130*S, 790*S), (950*S, 790*S)], fill=alpha(CREAM, 70), width=1*S)

    # the hours nobody watches
    ax = 812*S
    dr.line([(160*S, ax), (920*S, ax)], fill=alpha(CREAM, 120), width=1*S)
    marks = ["0400", "0430", "0500", "0530", "0600"]
    for i in range(21):
        x = 160*S + (760*S) * i / 20
        major = i % 5 == 0
        dr.line([(x, ax), (x, ax + (13*S if major else 7*S))],
                fill=alpha(CREAM, 120 if major else 60), width=1*S)
        if major:
            dr.text((x, ax + 20*S), marks[i // 5], font=f["mono_sm"],
                    fill=alpha(CREAM, 125), anchor="ma")

    title_block(dr, f, "BEFORE THE DAY STARTS", "First Light", "THE HOURS NOBODY WATCHES")
    registration(dr, f, "PL. VII", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-7-sun-firstlight.png")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    plate_ledger(); plate_evenground(); plate_corners(); plate_commonground()
    plate_turning(); plate_plumbline(); plate_firstlight()
