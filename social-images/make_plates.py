#!/usr/bin/env python3
"""Big Sky Ledger — five survey plates, 1080x1080, rendered at 2x and downsampled."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2               # supersample
W = H = 1080 * S
F = "/root/.claude/skills/canvas-design/canvas-fonts/"

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
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] + (bottom[0]-top[0])*t)
        g = int(top[1] + (bottom[1]-top[1])*t)
        b = int(top[2] + (bottom[2]-top[2])*t)
        for x_ in range(0, w, w):
            pass
        px_row = [(r, g, b)] * w
        img.paste(Image.new("RGB", (w, 1), (r, g, b)), (0, y))
    return img

def alpha(c, a):
    return (c[0], c[1], c[2], a)

def letterspace(draw, xy, text, font, fill, tracking, anchor="ls"):
    """Draw letterspaced text. anchor: ls=left baseline-ish top, ms=centered."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text)-1)
    x, y = xy
    if anchor == "ms":
        x -= total / 2
    for ch, w_ in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w_ + tracking
    return total

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
    """Hatch-fill below a ridgeline with fine horizontal-ish strata following the ridge."""
    max_off = y_floor - min(p[1] for p in pts)
    n = n or int(max_off // gap)
    for i in range(1, n+1):
        off = i * gap
        seg = [(x, min(y + off, y_floor)) for x, y in pts]
        fade = max(18, 120 - int(i * 100 / n))
        dr.line(seg, fill=alpha(line_col, fade), width=1*S)

def registration(dr, f, plate_no, coord, m=70*S):
    c = alpha(CREAM, 110)
    L = 26*S
    for (cx, cy, dx, dy) in [(m, m, 1, 1), (W-m, m, -1, 1), (m, H-m, 1, -1), (W-m, H-m, -1, -1)]:
        dr.line([(cx, cy), (cx+dx*L, cy)], fill=c, width=1*S)
        dr.line([(cx, cy), (cx, cy+dy*L)], fill=c, width=1*S)
    dr.text((W-m, m+14*S), plate_no, font=f["mono_sm"], fill=alpha(CREAM, 140), anchor="ra")
    dr.text((m, m+14*S), coord, font=f["mono_sm"], fill=alpha(CREAM, 140), anchor="la")
    # margin ticks
    for i in range(1, 10):
        x = m + (W - 2*m) * i / 10
        dr.line([(x, H-m), (x, H-m+8*S)], fill=alpha(CREAM, 70), width=1*S)

def footer(dr, f, y=None):
    y = y or H - 118*S
    letterspace(dr, (W/2, y), "RYAN BERNER", f["label"], alpha(CREAM, 225), 14*S, "ms")
    letterspace(dr, (W/2, y+46*S), "WEST AND COMPANY  ·  BROKERED BY EXP REALTY", f["label_sm"], alpha(CREAM, 130), 8*S, "ms")

def title_block(dr, f, kicker, word, y_kick, y_word, word_font=None):
    letterspace(dr, (W/2, y_kick), kicker, f["label"], alpha(GOLD_HI, 235), 16*S, "ms")
    wf = word_font or f["display"]
    dr.text((W/2, y_word), word, font=wf, fill=CREAM, anchor="ma")

def finish(img, name):
    out = img.resize((1080, 1080), Image.LANCZOS)
    out.save(name, "PNG")
    print("saved", name)

def base_plate(top, bottom):
    img = vgrad(W, H, top, bottom).convert("RGBA")
    return img

def grain(img, amount=6):
    rnd = random.Random(99)
    g = Image.effect_noise((W//2, H//2), 18).resize((W, H)).convert("L")
    overlay = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    overlay.putalpha(g.point(lambda v: amount if v > 128 else 0))
    return Image.alpha_composite(img, overlay)

# ---------------------------------------------------------------- PLATE I — THE MARKET
def plate_market():
    img = base_plate((13, 19, 31), (24, 33, 48))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    m = 70*S
    # faint section grid
    for i in range(1, 12):
        x = m + (W-2*m)*i/12
        dr.line([(x, 300*S), (x, 760*S)], fill=alpha(CREAM, 14), width=1*S)
    for i in range(6):
        y = 320*S + i*88*S
        dr.line([(m+40*S, y), (W-m-40*S, y)], fill=alpha(CREAM, 20), width=1*S)
        if i < 3:
            dr.text((m+40*S-12*S, y), f"{680-40*i}", font=f["mono_sm"], fill=alpha(CREAM, 80), anchor="rm")
    # back ridges (the market IS the mountain)
    r1 = ridge(7, 720*S, 210*S, 2.0, W)
    r2 = ridge(21, 760*S, 150*S, 3.1, W)
    draw_ridge_strata(dr, r1, 800*S, CREAM, gap=9*S)
    dr.line(r1, fill=alpha(CREAM, 150), width=2*S)
    draw_ridge_strata(dr, r2, 810*S, CREAM, gap=7*S)
    dr.line(r2, fill=alpha(CREAM, 100), width=1*S)
    # the gold price line — one spent gesture, tracing its own summit line
    gp = ridge(13, 690*S, 180*S, 1.6, W)
    gp = [(x, y-24*S) for x, y in gp if m <= x <= W-m]
    dr.line(gp, fill=alpha(GOLD, 235), width=3*S)
    # survey points on the gold line
    for t in (0.16, 0.42, 0.63, 0.86):
        px, py = gp[int(t*(len(gp)-1))]
        dr.ellipse([px-6*S, py-6*S, px+6*S, py+6*S], outline=GOLD_HI, width=2*S)
    # annotate one point like an instrument reading
    px, py = gp[int(0.63*(len(gp)-1))]
    dr.line([(px, py-10*S), (px, py-64*S)], fill=alpha(GOLD_HI, 160), width=1*S)
    dr.text((px, py-92*S), "MEDIAN $627K", font=f["mono"], fill=alpha(GOLD_HI, 220), anchor="ma")
    title_block(dr, f, "FLATHEAD VALLEY MARKET UPDATE", "The Market", 172*S, 208*S)
    dr.text((W/2, 148*S), "JULY · 2026", font=f["mono_sm"], fill=alpha(CREAM, 130), anchor="ma")
    registration(dr, f, "PL. I", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-1-wed-market.png")

# ---------------------------------------------------------------- PLATE II — THE ESTATE
def plate_estate():
    img = base_plate((26, 20, 26), (48, 34, 33))   # dusk plum → warm umber
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    cx, cy = W/2, 640*S
    # contour rings tightening toward the homestead
    for i in range(26):
        r = 70*S + i*34*S
        fade = max(12, 90 - i*3)
        wob = 6*S * math.sin(i*1.7)
        dr.ellipse([cx-r-wob, cy-r*0.62, cx+r+wob, cy+r*0.62],
                   outline=alpha(CREAM, fade), width=1*S)
    # the homestead: dark gable, one lit window — gold spent on the window alone
    hw, hh = 150*S, 110*S
    hx0, hy0 = cx-hw/2, cy-hh
    dr.polygon([(hx0-14*S, hy0), (cx, hy0-78*S), (hx0+hw+14*S, hy0)], fill=(16, 13, 16), outline=alpha(CREAM, 170))
    dr.rectangle([hx0, hy0, hx0+hw, hy0+hh], fill=(16, 13, 16), outline=alpha(CREAM, 170), width=1*S)
    wx, wy = cx+26*S, hy0+34*S
    dr.rectangle([wx, wy, wx+34*S, wy+44*S], fill=GOLD_HI)
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([wx-70*S, wy-60*S, wx+104*S, wy+110*S], fill=alpha(GOLD, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(40*S))
    img = Image.alpha_composite(img, glow)
    dr = ImageDraw.Draw(img, "RGBA")
    title_block(dr, f, "ESTATE  &  INHERITED HOMES", "The Homestead", 172*S, 208*S)
    dr.text((W/2, 148*S), "A STEADY HAND, WHEN IT MATTERS", font=f["mono_sm"], fill=alpha(CREAM, 130), anchor="ma")
    registration(dr, f, "PL. II", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-2-thu-estate.png")

# ---------------------------------------------------------------- PLATE III — THE VALLEY
def plate_valley():
    img = base_plate((12, 22, 34), (20, 38, 52))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    horizon = 640*S
    # gold sun — the single spent gesture
    scx, scy, sr = W*0.66, 470*S, 64*S
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([scx-sr*2.6, scy-sr*2.6, scx+sr*2.6, scy+sr*2.6], fill=alpha(GOLD, 46))
    glow = glow.filter(ImageFilter.GaussianBlur(50*S))
    img = Image.alpha_composite(img, glow); dr = ImageDraw.Draw(img, "RGBA")
    dr.ellipse([scx-sr, scy-sr, scx+sr, scy+sr], fill=GOLD_HI)
    # ridges above the waterline
    r1 = ridge(5, horizon, 200*S, 1.9, W)
    r2 = ridge(17, horizon, 120*S, 3.4, W)
    draw_ridge_strata(dr, r1, horizon, CREAM, gap=9*S)
    dr.line(r1, fill=alpha(CREAM, 170), width=2*S)
    dr.line(r2, fill=alpha(CREAM, 90), width=1*S)
    # mask ridge below horizon then draw the lake: mirrored, broken lines
    dr.rectangle([0, horizon, W, H], fill=(10, 18, 28, 255))
    for i, (x, y) in enumerate(r1):
        if i % 3:
            continue
        ry = horizon + (horizon - y) * 0.5
        if ry - horizon > 4*S:
            dr.line([(x, horizon+4*S), (x, ry)], fill=alpha(CREAM, 26), width=1*S)
    # sun path on water
    for k in range(22):
        yy = horizon + 14*S + k*10*S
        half = max(6*S, (56 - k*2.2)*S) * (0.7 + 0.3*math.sin(k*2.2))
        dr.line([(scx-half, yy), (scx+half, yy)], fill=alpha(GOLD, max(30, 150-6*k)), width=2*S)
    dr.line([(0, horizon), (W, horizon)], fill=alpha(CREAM, 120), width=1*S)
    title_block(dr, f, "LIFE IN THE FLATHEAD", "The Valley", 172*S, 208*S)
    dr.text((W/2, 148*S), "GLACIER TO LAKESHORE", font=f["mono_sm"], fill=alpha(CREAM, 130), anchor="ma")
    registration(dr, f, "PL. III", "48.41° N   114.34° W")
    footer(dr, f)
    finish(grain(img), "plate-3-fri-valley.png")

# ---------------------------------------------------------------- PLATE IV — THE THRESHOLD
def plate_threshold():
    img = base_plate((16, 18, 24), (28, 30, 38))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    # dense vertical hatch field — the labor of preparation
    rnd = random.Random(3)
    for x in range(int(90*S), int(W-90*S), int(7*S)):
        a = 16 + int(14 * (0.5+0.5*math.sin(x/(60*S))))
        dr.line([(x, 330*S+rnd.randint(0, 18)*S), (x, 800*S-rnd.randint(0, 18)*S)],
                fill=alpha(CREAM, a), width=1*S)
    # the door: a gold threshold standing in the field
    dw, dh = 190*S, 380*S
    dx0, dy0 = W/2-dw/2, 420*S
    dr.rectangle([dx0-26*S, dy0-26*S, dx0+dw+26*S, dy0+dh], outline=alpha(CREAM, 160), width=2*S)
    dr.rectangle([dx0, dy0, dx0+dw, dy0+dh], fill=(12, 13, 17), outline=alpha(GOLD, 240), width=3*S)
    # light under the door
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.rectangle([dx0-10*S, dy0+dh-6*S, dx0+dw+10*S, dy0+dh+26*S], fill=alpha(GOLD, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(18*S))
    img = Image.alpha_composite(img, glow); dr = ImageDraw.Draw(img, "RGBA")
    dr.ellipse([dx0+dw-34*S, dy0+dh/2-7*S, dx0+dw-20*S, dy0+dh/2+7*S], fill=GOLD_HI)
    # survey ticks pacing toward the door
    for i in range(9):
        y = 828*S
        x0 = 200*S + i*(W-400*S)/8
        dr.line([(x0, y), (x0, y+14*S)], fill=alpha(CREAM, 90), width=1*S)
    title_block(dr, f, "SELLING IN A FLAT MARKET", "The Threshold", 172*S, 208*S)
    dr.text((W/2, 148*S), "PRICED RIGHT ON DAY ONE", font=f["mono_sm"], fill=alpha(CREAM, 130), anchor="ma")
    registration(dr, f, "PL. IV", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-4-sat-threshold.png")

# ---------------------------------------------------------------- PLATE V — TRUE NORTH
def plate_north():
    img = base_plate((11, 16, 27), (22, 28, 42))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    cx, cy = W/2, 600*S
    # faint topo bed
    for i in range(20):
        r = 90*S + i*40*S
        dr.ellipse([cx-r, cy-r, cx+r, cy+r], outline=alpha(CREAM, max(10, 46-2*i)), width=1*S)
    # radiating survey lines — the discipline
    for k in range(72):
        ang = k*math.tau/72
        r0, r1_ = 120*S, 470*S
        if k % 18 == 0:
            r0 = 90*S
        a = 70 if k % 18 == 0 else 26
        dr.line([(cx+r0*math.cos(ang), cy+r0*math.sin(ang)),
                 (cx+r1_*math.cos(ang), cy+r1_*math.sin(ang))], fill=alpha(CREAM, a), width=1*S)
    # cardinal letters
    for txt, ang in (("N", -90), ("E", 0), ("S", 90), ("W", 180)):
        x = cx + 505*S*math.cos(math.radians(ang))
        y = cy + 505*S*math.sin(math.radians(ang))
        dr.text((x, y), txt, font=f["label"], fill=alpha(CREAM, 170), anchor="mm")
    # the gold star — north, spent once
    def star(cx_, cy_, R, r_):
        pts = []
        for i in range(8):
            ang = -math.pi/2 + i*math.pi/4
            rad = R if i % 2 == 0 else r_
            pts.append((cx_+rad*math.cos(ang), cy_+rad*math.sin(ang)))
        return pts
    dr.polygon(star(cx, cy, 96*S, 26*S), fill=GOLD, outline=GOLD_HI)
    dr.polygon(star(cx, cy, 40*S, 12*S), fill=(12, 16, 26))
    dr.line([(cx, cy-255*S), (cx, cy-130*S)], fill=alpha(GOLD_HI, 140), width=1*S)
    # soft scrim so the title zone stays quiet above the instrument
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    sd.rectangle([140*S, 120*S, W-140*S, 345*S], fill=(13, 18, 30, 175))
    scrim = scrim.filter(ImageFilter.GaussianBlur(30*S))
    img = Image.alpha_composite(img, scrim); dr = ImageDraw.Draw(img, "RGBA")
    title_block(dr, f, "THE MISSION BRIEF", "True North", 172*S, 208*S)
    dr.text((W/2, 148*S), "PLAN · PHASES · CONTINGENCIES", font=f["mono_sm"], fill=alpha(CREAM, 130), anchor="ma")
    registration(dr, f, "PL. V", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-5-sun-north.png")

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    plate_market(); plate_estate(); plate_valley(); plate_threshold(); plate_north()
