#!/usr/bin/env python3
"""Big Sky Ledger — week of 2026-08-10 — seven survey plates, 1080x1080 @2x."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2
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
        fade = max(18, 120 - int(i * 100 / n))
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
    return

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

def title_block(dr, f, kicker, word, mono_top, word_font=None):
    dr.text((W/2, 146*S), mono_top, font=f["mono_sm"], fill=alpha(CREAM, 130), anchor="ma")
    letterspace(dr, (W/2, 178*S), kicker, f["label"], alpha(GOLD_HI, 235), 15*S, "ms")
    wf = word_font or f["display"]
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

def qbez(p0, c, p1, n=90):
    pts = []
    for t in [i/n for i in range(n+1)]:
        x = (1-t)**2 * p0[0] + 2*(1-t)*t*c[0] + t*t*p1[0]
        y = (1-t)**2 * p0[1] + 2*(1-t)*t*c[1] + t*t*p1[1]
        pts.append((x, y))
    return pts


# ------------------------------------------------ PL. I — MON — THE READING (market)
def plate_reading():
    img = base_plate((13, 19, 31), (24, 33, 48))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    m = 70*S
    # faint section lines
    for i in range(5):
        y = (430 + i*95)*S
        dr.line([(m+50*S, y), (W-m-50*S, y)], fill=alpha(CREAM, 15), width=1*S)
    # low ridge strata
    r1 = ridge(53, 796*S, 78*S, 2.5, W)
    draw_ridge_strata(dr, r1, 820*S, CREAM, gap=9*S)
    dr.line(r1, fill=alpha(CREAM, 100), width=1*S)
    # the instrument — a surveyor's level arc, mid-plate
    cx, cy, R = 540*S, 668*S, 300*S
    for k in range(25):
        ang = math.pi + k*math.pi/24
        ca, sa = math.cos(ang), math.sin(ang)
        L = 22*S if k % 4 == 0 else 13*S
        x0, y0 = cx+R*ca, cy+R*sa
        x1, y1 = cx+(R-L)*ca, cy+(R-L)*sa
        a = 150 if k % 4 == 0 else 90
        dr.line([(x0, y0), (x1, y1)], fill=alpha(CREAM, a), width=1*S)
    dr.arc([cx-R, cy-R, cx+R, cy+R], 180, 360, fill=alpha(CREAM, 120), width=1*S)
    for lab, k in (("JUN", 3), ("JUL", 9), ("AUG", 15), ("SEP", 21)):
        ang = math.pi + k*math.pi/24
        x = cx+(R+40*S)*math.cos(ang)
        y = cy+(R+34*S)*math.sin(ang)
        dr.text((x, y), lab, font=f["mono_sm"], fill=alpha(CREAM, 115), anchor="mm")
    # the needle — gold, spent once, reading mid-August true
    ang = math.pi + 16.4*math.pi/24
    nx, ny = cx+(R-34*S)*math.cos(ang), cy+(R-34*S)*math.sin(ang)
    dr.line([(cx, cy), (nx, ny)], fill=alpha(GOLD, 235), width=3*S)
    d = 10*S
    dr.polygon([(cx, cy-d), (cx+d, cy), (cx, cy+d), (cx-d, cy)], fill=GOLD_HI)
    tx, ty = cx+(R-92*S)*math.cos(ang-0.16), cy+(R-92*S)*math.sin(ang-0.16)
    dr.text((tx, ty-26*S), "MID-AUGUST · TRUE", font=f["mono"], fill=alpha(GOLD_HI, 225), anchor="ma")
    title_block(dr, f, "FLATHEAD VALLEY MARKET UPDATE", "The Reading", "MID-AUGUST · 2026")
    registration(dr, f, "PL. I", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-1-mon-reading.png")

# ------------------------------------------------ PL. II — TUE — THE CONSTANT (divorce, school year)
def plate_constant():
    img = base_plate((14, 17, 29), (26, 30, 44))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    # two homes drift apart; one point holds
    hA = (306*S, 664*S)
    hB = (816*S, 706*S)
    sc = (556*S, 500*S)
    def small_home(p, a):
        x, y = p
        hw, hh = 76*S, 54*S
        x0, y0 = x-hw/2, y-hh/2
        dr.polygon([(x0-8*S, y0), (x, y0-40*S), (x0+hw+8*S, y0)], outline=alpha(CREAM, a))
        dr.rectangle([x0, y0, x0+hw, y0+hh], outline=alpha(CREAM, a), width=2*S)
    small_home(hA, 200)
    small_home(hB, 200)
    # both routes hold to the same constant, dashed and patient
    for h in (hA, hB):
        route = qbez((h[0], h[1]-46*S), ((h[0]+sc[0])/2, min(h[1], sc[1])-60*S), (sc[0], sc[1]+56*S), 80)
        dashed(dr, route, alpha(CREAM, 140), width=2*S, dash=12*S, gap=9*S)
    # section grid, faint, beneath everything
    for i in range(6):
        y = (430 + i*82)*S
        dr.line([(150*S, y), (W-150*S, y)], fill=alpha(CREAM, 13), width=1*S)
    # the schoolhouse — gold, the one point that does not move
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([sc[0]-70*S, sc[1]-70*S, sc[0]+70*S, sc[1]+70*S], fill=alpha(GOLD, 55))
    glow = glow.filter(ImageFilter.GaussianBlur(32*S))
    img = Image.alpha_composite(img, glow); dr = ImageDraw.Draw(img, "RGBA")
    x, y = sc
    hw, hh = 92*S, 62*S
    x0, y0 = x-hw/2, y-hh/2
    dr.polygon([(x0-9*S, y0), (x, y0-46*S), (x0+hw+9*S, y0)], outline=alpha(GOLD_HI, 245))
    dr.rectangle([x0, y0, x0+hw, y0+hh], outline=alpha(GOLD_HI, 245), width=2*S)
    # the bell tower
    dr.rectangle([x-9*S, y0-72*S, x+9*S, y0-46*S], outline=alpha(GOLD_HI, 220), width=2*S)
    dr.ellipse([x-4*S, y0-64*S, x+4*S, y0-56*S], fill=GOLD_HI)
    dr.text((x, y+58*S), "THE DISTRICT · HELD", font=f["mono"], fill=alpha(GOLD_HI, 225), anchor="ma")
    # scrims for title and footer
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    sd.rectangle([0, 96*S, W, 352*S], fill=(15, 18, 30, 190))
    sd.rectangle([0, 856*S, W, H-56*S], fill=(24, 28, 41, 190))
    scrim = scrim.filter(ImageFilter.GaussianBlur(24*S))
    img = Image.alpha_composite(img, scrim); dr = ImageDraw.Draw(img, "RGBA")
    title_block(dr, f, "DIVORCE · THE SCHOOL YEAR", "The Constant", "TWO ROUTES · ONE BELL")
    registration(dr, f, "PL. II", "48.20° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-2-tue-constant.png")

# ------------------------------------------------ PL. III — WED — GROUNDWORK (well & septic)
def plate_groundwork():
    img = base_plate((12, 18, 30), (22, 32, 44))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    ground = 560*S
    # the surface line and the home upon it
    dr.line([(120*S, ground), (W-120*S, ground)], fill=alpha(CREAM, 170), width=2*S)
    for i in range(19):
        x = (150 + i*42)*S
        dr.line([(x, ground), (x, ground-9*S)], fill=alpha(CREAM, 55), width=1*S)
    cx = 420*S
    hw, hh = 130*S, 84*S
    x0, y0 = cx-hw/2, ground-hh
    dr.polygon([(x0-12*S, y0), (cx, y0-58*S), (x0+hw+12*S, y0)], outline=alpha(CREAM, 200))
    dr.rectangle([x0, y0, x0+hw, ground], outline=alpha(CREAM, 200), width=2*S)
    # below: the section nobody looks at — strata hatch
    rnd = random.Random(12)
    for yy in range(int(ground+26*S), int(856*S), int(15*S)):
        a = 26 - int((yy - ground) / (360*S) * 14)
        for x in range(int(140*S), int(W-140*S), int(17*S)):
            if rnd.random() < 0.82:
                dr.line([(x, yy), (x+9*S, yy)], fill=alpha(CREAM, max(8, a)), width=1*S)
    # the well shaft — dashed, descending to the one thing that matters
    wx = 700*S
    dashed(dr, [(wx, ground), (wx, 756*S)], alpha(CREAM, 170), width=2*S, dash=11*S, gap=8*S)
    dr.rectangle([wx-16*S, ground-30*S, wx+16*S, ground], outline=alpha(CREAM, 180), width=2*S)
    for lab, yy in (("CASING", 646*S), ("STATIC LEVEL", 696*S)):
        dr.line([(wx+22*S, yy), (wx+66*S, yy)], fill=alpha(CREAM, 90), width=1*S)
        dr.text((wx+76*S, yy), lab, font=f["mono_sm"], fill=alpha(CREAM, 120), anchor="lm")
    # the aquifer — gold, spent once, the water you're actually buying
    ay = 786*S
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.rectangle([220*S, ay-26*S, 860*S, ay+26*S], fill=alpha(GOLD, 46))
    glow = glow.filter(ImageFilter.GaussianBlur(26*S))
    img = Image.alpha_composite(img, glow); dr = ImageDraw.Draw(img, "RGBA")
    for i in range(3):
        yy = ay + (i-1)*14*S
        amp = 7*S
        pts = [(x, yy + amp*math.sin(x/(46*S) + i*1.7)) for x in range(int(240*S), int(840*S), int(6*S))]
        dr.line(pts, fill=alpha(GOLD_HI, 210 - i*40), width=2*S)
    dr.ellipse([wx-6*S, ay-6*S, wx+6*S, ay+6*S], fill=GOLD_HI)
    dr.text((540*S, ay+44*S), "THE AQUIFER · KNOW BEFORE YOU BUY", font=f["mono"], fill=alpha(GOLD_HI, 220), anchor="ma")
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    sd.rectangle([0, 872*S, W, H-56*S], fill=(18, 27, 38, 210))
    scrim = scrim.filter(ImageFilter.GaussianBlur(20*S))
    img = Image.alpha_composite(img, scrim); dr = ImageDraw.Draw(img, "RGBA")
    title_block(dr, f, "BUYER BRIEF · WELL & SEPTIC", "Groundwork", "WHAT THE LISTING WON'T SAY")
    registration(dr, f, "PL. III", "48.24° N   114.30° W")
    footer(dr, f)
    finish(grain(img), "plate-3-wed-groundwork.png")

# ------------------------------------------------ PL. IV — THU — THE BASELINE (step-up basis, dusk)
def plate_baseline():
    img = base_plate((26, 20, 26), (48, 34, 33))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    m = 150*S
    # the ledger field — patient ruled lines
    for i in range(11):
        yy = (430 + i*40)*S
        dr.line([(m, yy), (W-m, yy)], fill=alpha(CREAM, 26), width=1*S)
    # the old basis — faint, dated, nearly forgotten
    oy = 806*S
    dr.line([(m, oy), (W-m, oy)], fill=alpha(CREAM, 110), width=1*S)
    dr.text((m, oy+16*S), "ORIGINAL BASIS · YEARS AGO", font=f["mono_sm"], fill=alpha(CREAM, 110), anchor="la")
    # the step — a dashed rise at the date that changed it
    sx = 560*S
    ny = 512*S
    dashed(dr, [(sx, oy), (sx, ny)], alpha(CREAM, 150), width=2*S, dash=11*S, gap=8*S)
    dr.text((sx-22*S, (oy+ny)/2), "DATE OF DEATH", font=f["mono_sm"], fill=alpha(CREAM, 130), anchor="rm")
    # the new baseline — gold, the value that matters now
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.rectangle([m-20*S, ny-20*S, W-m+20*S, ny+20*S], fill=alpha(GOLD, 42))
    glow = glow.filter(ImageFilter.GaussianBlur(24*S))
    img = Image.alpha_composite(img, glow); dr = ImageDraw.Draw(img, "RGBA")
    dr.line([(sx, ny), (W-m, ny)], fill=alpha(GOLD, 240), width=3*S)
    dr.ellipse([sx-8*S, ny-8*S, sx+8*S, ny+8*S], fill=GOLD_HI)
    dr.text((W-m, ny-30*S), "STEPPED-UP BASIS · TODAY'S VALUE", font=f["mono"], fill=alpha(GOLD_HI, 230), anchor="ra")
    # small homestead resting on the old line, left of the step
    hx = 306*S
    hw, hh = 96*S, 64*S
    x0, y0 = hx-hw/2, oy-hh
    dr.polygon([(x0-10*S, y0), (hx, y0-46*S), (x0+hw+10*S, y0)], fill=(22, 17, 21), outline=alpha(CREAM, 180))
    dr.rectangle([x0, y0, x0+hw, oy], fill=(22, 17, 21), outline=alpha(CREAM, 180), width=1*S)
    title_block(dr, f, "ESTATE · THE STEP-UP BASIS", "The Baseline", "RESET AT THE DATE OF DEATH")
    registration(dr, f, "PL. IV", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-4-thu-baseline.png")

# ------------------------------------------------ PL. V — FRI — SHORELINE (Flathead Lake, three harbors)
def plate_shoreline():
    img = base_plate((12, 22, 34), (20, 38, 52))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    # the lake — contour of the north shore, drawn as depth lines
    def shore(off, a):
        pts = []
        for x in range(0, W+1, 6):
            t = x / W
            y = (486 + off + 60*math.sin(t*3.1 + 0.7) + 34*math.sin(t*6.7 + 2.1))*S
            pts.append((x, y))
        dr.line(pts, fill=alpha(CREAM, a), width=1*S)
        return pts
    top = shore(0, 170)
    for i in range(1, 12):
        shore(26 + i*30, max(12, 70 - i*5))
    # water hatch below the last depth line
    rnd = random.Random(21)
    for yy in range(int(880*S), int(960*S), int(12*S)):
        for x in range(int(60*S), int(W-60*S), int(26*S)):
            if rnd.random() < 0.6:
                dr.line([(x, yy), (x+14*S, yy)], fill=alpha(CREAM, 16), width=1*S)
    # three harbors along the shore — survey stations
    def station(x, name, lx, ly, anchor):
        y = None
        for px, py in top:
            if px >= x:
                y = py
                break
        dr.ellipse([x-14*S, y-14*S, x+14*S, y+14*S], outline=alpha(CREAM, 210), width=2*S)
        t = 7*S
        dr.polygon([(x, y-t), (x+t*0.87, y+t*0.5), (x-t*0.87, y+t*0.5)], outline=alpha(CREAM, 210))
        dr.text((x+lx, y+ly), name, font=f["mono"], fill=alpha(CREAM, 190), anchor=anchor)
        return (x, y)
    pL = station(268*S, "LAKESIDE", -6*S, -52*S, "ma")
    pS = station(548*S, "SOMERS", 0, -52*S, "ma")
    pB = station(848*S, "BIGFORK", -6*S, -52*S, "ma")
    dashed(dr, [pL, pS], alpha(CREAM, 110), width=1*S, dash=10*S, gap=8*S)
    dashed(dr, [pS, pB], alpha(CREAM, 110), width=1*S, dash=10*S, gap=8*S)
    # the sun on the water — gold, spent once
    gx, gy = 700*S, 764*S
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([gx-72*S, gy-72*S, gx+72*S, gy+72*S], fill=alpha(GOLD, 58))
    glow = glow.filter(ImageFilter.GaussianBlur(30*S))
    img = Image.alpha_composite(img, glow); dr = ImageDraw.Draw(img, "RGBA")
    dr.ellipse([gx-20*S, gy-20*S, gx+20*S, gy+20*S], fill=GOLD_HI)
    for i, wamp in enumerate((30, 46, 62)):
        yy = gy + 34*S + i*16*S
        dr.line([(gx-wamp*S, yy), (gx+wamp*S, yy)], fill=alpha(GOLD_HI, 160 - i*40), width=2*S)
    dr.text((gx, gy+96*S), "ONE LAKE · THREE LIVES", font=f["mono"], fill=alpha(GOLD_HI, 220), anchor="ma")
    title_block(dr, f, "FLATHEAD LAKE · THE NORTH SHORE", "Shoreline", "LAKESIDE · SOMERS · BIGFORK")
    registration(dr, f, "PL. V", "47.96° N   114.19° W")
    footer(dr, f)
    finish(grain(img), "plate-5-fri-shoreline.png")

# ------------------------------------------------ PL. VI — SAT — FIRST GLANCE (staging)
def plate_firstglance():
    img = base_plate((13, 19, 31), (24, 33, 48))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    # ridge behind the home — the view buyers came for
    r1 = ridge(31, 596*S, 110*S, 2.2, W)
    draw_ridge_strata(dr, r1, 620*S, CREAM, gap=8*S)
    dr.line(r1, fill=alpha(CREAM, 140), width=1*S)
    ground = 796*S
    dr.line([(120*S, ground), (W-120*S, ground)], fill=alpha(CREAM, 150), width=1*S)
    for i in range(17):
        x = (150 + i*46)*S
        dr.line([(x, ground), (x, ground+9*S)], fill=alpha(CREAM, 55), width=1*S)
    # the home, drawn whole and calm
    cx = 540*S
    hw, hh = 300*S, 170*S
    x0, y0 = cx-hw/2, ground-hh
    dr.polygon([(x0-22*S, y0), (cx, y0-118*S), (x0+hw+22*S, y0)], outline=alpha(CREAM, 210))
    dr.rectangle([x0, y0, x0+hw, ground], outline=alpha(CREAM, 210), width=2*S)
    # hatch the body lightly — cared for, not busy
    for yy in range(int(y0+14*S), int(ground-8*S), int(14*S)):
        dr.line([(x0+10*S, yy), (x0+hw-10*S, yy)], fill=alpha(CREAM, 16), width=1*S)
    # door and dark window
    dr.rectangle([cx+62*S, ground-92*S, cx+108*S, ground], outline=alpha(CREAM, 170), width=2*S)
    dr.rectangle([x0+34*S, y0+40*S, x0+106*S, y0+104*S], outline=alpha(CREAM, 150), width=2*S)
    # the lit window — gold, spent once: the first thing they notice
    wx0, wy0, wx1, wy1 = cx-40*S, y0+40*S, cx+36*S, y0+104*S
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.rectangle([wx0-26*S, wy0-26*S, wx1+26*S, wy1+26*S], fill=alpha(GOLD, 66))
    glow = glow.filter(ImageFilter.GaussianBlur(30*S))
    img = Image.alpha_composite(img, glow); dr = ImageDraw.Draw(img, "RGBA")
    dr.rectangle([wx0, wy0, wx1, wy1], fill=alpha(GOLD, 200), outline=GOLD_HI, width=2*S)
    dr.line([( (wx0+wx1)/2, wy0), ((wx0+wx1)/2, wy1)], fill=(122, 96, 50), width=2*S)
    dr.line([(wx0, (wy0+wy1)/2), (wx1, (wy0+wy1)/2)], fill=(122, 96, 50), width=2*S)
    dr.text((cx, ground+34*S), "LIGHT · VIEW · EASE", font=f["mono_sm"], fill=alpha(CREAM, 150), anchor="ma")
    title_block(dr, f, "SELLER BRIEF · STAGING", "First Glance", "WHAT THEY NOTICE · BEFORE THE PILLOWS")
    registration(dr, f, "PL. VI", "48.23° N   114.33° W")
    footer(dr, f)
    finish(grain(img), "plate-6-sat-firstglance.png")

# ------------------------------------------------ PL. VII — SUN — THE DEBRIEF (after-action)
def plate_debrief():
    img = base_plate((11, 16, 27), (22, 28, 42))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    # the completed route — waypoints crossed, reviewed in order
    route = [(206*S, 758*S), (330*S, 620*S), (472*S, 668*S), (610*S, 540*S), (760*S, 586*S), (866*S, 472*S)]
    for a, b in zip(route, route[1:]):
        dashed(dr, [a, b], alpha(CREAM, 140), width=2*S, dash=12*S, gap=9*S)
    labels = ["LIST", "INSPECT", "APPRAISE", "NEGOTIATE", "CLEAR", "CLOSE"]
    for (x, y), lab in zip(route, labels):
        dr.ellipse([x-11*S, y-11*S, x+11*S, y+11*S], outline=alpha(CREAM, 190), width=2*S)
        dr.line([(x-6*S, y), (x+6*S, y)], fill=alpha(CREAM, 190), width=1*S)
        dr.line([(x, y-6*S), (x, y+6*S)], fill=alpha(CREAM, 190), width=1*S)
        dr.text((x, y+30*S), lab, font=f["mono_sm"], fill=alpha(CREAM, 125), anchor="ma")
    # quiet hatch field beneath the route
    rnd = random.Random(5)
    for x in range(int(140*S), int(W-140*S), int(9*S)):
        a = 10 + int(8 * (0.5+0.5*math.sin(x/(80*S))))
        dr.line([(x, 812*S+rnd.randint(0, 12)*S), (x, 900*S-rnd.randint(0, 12)*S)],
                fill=alpha(CREAM, a), width=1*S)
    # the lesson — gold, spent once: the mark carried to the next map
    lx, ly = 866*S, 472*S
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([lx-64*S, ly-64*S, lx+64*S, ly+64*S], fill=alpha(GOLD, 58))
    glow = glow.filter(ImageFilter.GaussianBlur(28*S))
    img = Image.alpha_composite(img, glow); dr = ImageDraw.Draw(img, "RGBA")
    dr.ellipse([lx-18*S, ly-18*S, lx+18*S, ly+18*S], outline=GOLD_HI, width=3*S)
    dr.line([(lx-8*S, ly+1*S), (lx-2*S, ly+8*S), (lx+10*S, ly-8*S)], fill=GOLD_HI, width=3*S)
    dr.text((lx-30*S, ly-40*S), "LESSON · CARRIED FORWARD", font=f["mono"], fill=alpha(GOLD_HI, 225), anchor="ra")
    title_block(dr, f, "AFTER THE CLOSE · EVERY TIME", "The Debrief", "WHAT WORKED · WHAT CHANGES", f["display_sm"])
    registration(dr, f, "PL. VII", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-7-sun-debrief.png")

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    plate_reading(); plate_constant(); plate_groundwork(); plate_baseline()
    plate_shoreline(); plate_firstglance(); plate_debrief()
