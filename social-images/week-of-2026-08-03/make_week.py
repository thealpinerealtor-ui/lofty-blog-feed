#!/usr/bin/env python3
"""Big Sky Ledger — week of 2026-08-03 — seven survey plates, 1080x1080 @2x."""
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
    letterspace(dr, (W/2, y+84*S), "(406) 602-1418  ·  ANSWERED AROUND THE CLOCK", f["mono_sm"], alpha(CREAM, 115), 3*S, "ms")

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

# ------------------------------------------------ PL. I — MON — THE CREST (market)
def plate_crest():
    img = base_plate((13, 19, 31), (24, 33, 48))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    m = 70*S
    # faint section lines
    for i in range(5):
        y = (430 + i*95)*S
        dr.line([(m+50*S, y), (W-m-50*S, y)], fill=alpha(CREAM, 15), width=1*S)
    # distant ridges, low
    r1 = ridge(37, 772*S, 90*S, 2.3, W)
    draw_ridge_strata(dr, r1, 800*S, CREAM, gap=9*S)
    dr.line(r1, fill=alpha(CREAM, 100), width=1*S)
    # month ticks along the baseline of the season
    months = ["MAY", "JUN", "JUL", "AUG", "SEP", "OCT"]
    xs = [(190 + i*140)*S for i in range(6)]
    base_y = 824*S
    dr.line([(xs[0]-30*S, base_y), (xs[5]+30*S, base_y)], fill=alpha(CREAM, 70), width=1*S)
    for x, mo in zip(xs, months):
        dr.line([(x, base_y), (x, base_y-14*S)], fill=alpha(CREAM, 110), width=1*S)
        dr.text((x, base_y+12*S), mo, font=f["mono_sm"], fill=alpha(CREAM, 110), anchor="ma")
    # the season's arc — gold, cresting in late July, easing off in August
    arc = qbez((xs[0], 752*S), (540*S, 396*S), (xs[5], 732*S), 120)
    dr.line(arc, fill=alpha(GOLD, 235), width=3*S)
    # survey points along the arc
    for t in (0.18, 0.50, 0.62, 0.86):
        px, py = arc[int(t*120)]
        dr.ellipse([px-6*S, py-6*S, px+6*S, py+6*S], outline=GOLD_HI, width=2*S)
    # the turn — annotated just past the crest
    px, py = arc[int(0.62*120)]
    dr.line([(px, py-12*S), (px, py-74*S)], fill=alpha(GOLD_HI, 160), width=1*S)
    dr.text((px, py-104*S), "THE TURN · AUGUST", font=f["mono"], fill=alpha(GOLD_HI, 225), anchor="ma")
    title_block(dr, f, "FLATHEAD VALLEY MARKET UPDATE", "The Crest", "EARLY AUGUST · 2026")
    registration(dr, f, "PL. I", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-1-mon-crest.png")

# ------------------------------------------------ PL. II — TUE — THE KEEPING (divorce buyout)
def plate_keeping():
    img = base_plate((14, 17, 29), (26, 30, 44))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    ox, oy = 440*S, 566*S
    # quiet contour field around the kept home
    for i in range(15):
        r = (66 + i*46)*S
        fade = max(10, 58 - i*3)
        dr.ellipse([ox-r, oy-r*0.6, ox+r, oy+r*0.6], outline=alpha(CREAM, fade), width=1*S)
    # one path departs, gently, toward its own whole place
    dep = qbez((ox+74*S, oy+30*S), (700*S, 700*S), (866*S, 806*S), 80)
    dashed(dr, dep, alpha(CREAM, 150), width=2*S, dash=13*S, gap=10*S)
    p = dep[-1]
    dr.ellipse([p[0]-11*S, p[1]-11*S, p[0]+11*S, p[1]+11*S], outline=alpha(CREAM, 190), width=2*S)
    # the home, kept — gold spent here, once
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([ox-84*S, oy-84*S, ox+84*S, oy+84*S], fill=alpha(GOLD, 52))
    glow = glow.filter(ImageFilter.GaussianBlur(38*S))
    img = Image.alpha_composite(img, glow); dr = ImageDraw.Draw(img, "RGBA")
    hw, hh = 96*S, 66*S
    hx0, hy0 = ox-hw/2, oy-hh/2+12*S
    dr.polygon([(hx0-10*S, hy0), (ox, hy0-52*S), (hx0+hw+10*S, hy0)], outline=alpha(GOLD_HI, 245))
    dr.rectangle([hx0, hy0, hx0+hw, hy0+hh], outline=alpha(GOLD_HI, 245), width=2*S)
    dr.rectangle([ox-11*S, hy0+22*S, ox+11*S, hy0+hh], outline=alpha(GOLD_HI, 200), width=1*S)
    # quiet scrims so title and footer sit clear of the contour field
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    sd.rectangle([0, 96*S, W, 352*S], fill=(15, 18, 30, 200))
    sd.rectangle([0, 856*S, W, H-56*S], fill=(24, 28, 41, 200))
    scrim = scrim.filter(ImageFilter.GaussianBlur(24*S))
    img = Image.alpha_composite(img, scrim); dr = ImageDraw.Draw(img, "RGBA")
    title_block(dr, f, "DIVORCE · THE BUYOUT", "The Keeping", "ONE KEEPS · ONE BEGINS AGAIN")
    registration(dr, f, "PL. II", "48.20° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-2-tue-keeping.png")

# ------------------------------------------------ PL. III — WED — TWO BUILDS (new vs resale)
def plate_twobuilds():
    img = base_plate((12, 18, 30), (22, 32, 44))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    ground = 744*S
    dr.line([(140*S, ground), (W-140*S, ground)], fill=alpha(CREAM, 140), width=1*S)
    for i in range(17):
        x = (170 + i*46)*S
        dr.line([(x, ground), (x, ground+10*S)], fill=alpha(CREAM, 60), width=1*S)
    def gable(cx, solid):
        bw, bh = 200*S, 128*S
        x0, y0 = cx-bw/2, ground-bh
        peak = (cx, y0-92*S)
        if solid:
            # resale — settled, hatched, whole
            for i in range(1, 11):
                t = i/11
                yA = peak[1] + (y0 - peak[1]) * t
                xL = peak[0] + (x0 - 20*S - peak[0]) * t
                xR = peak[0] + (x0 + bw + 20*S - peak[0]) * t
                dr.line([(xL, yA), (xR, yA)], fill=alpha(CREAM, 26), width=1*S)
            for yy in range(int(y0+16*S), int(ground-8*S), int(13*S)):
                dr.line([(x0+8*S, yy), (x0+bw-8*S, yy)], fill=alpha(CREAM, 20), width=1*S)
            dr.polygon([(x0-20*S, y0), peak, (x0+bw+20*S, y0)], outline=alpha(CREAM, 200))
            dr.rectangle([x0, y0, x0+bw, ground], outline=alpha(CREAM, 200), width=2*S)
            dr.rectangle([cx+40*S, y0-160*S+92*S, cx+66*S, y0], outline=alpha(CREAM, 170), width=2*S)
        else:
            # new construction — still only framed, drawn in dashes
            dashed(dr, [(x0-20*S, y0), peak, (x0+bw+20*S, y0)], alpha(CREAM, 190), width=2*S, dash=11*S, gap=8*S)
            dashed(dr, [(x0, y0), (x0+bw, y0), (x0+bw, ground), (x0, ground), (x0, y0)],
                   alpha(CREAM, 190), width=2*S, dash=11*S, gap=8*S)
            for i in range(1, 6):
                x = x0 + bw*i/6
                dr.line([(x, y0+6*S), (x, ground-4*S)], fill=alpha(CREAM, 55), width=1*S)
        return peak
    gable(330*S, solid=False)
    gable(750*S, solid=True)
    dr.text((330*S, ground+34*S), "NEW · BUILT TO ORDER", font=f["mono_sm"], fill=alpha(CREAM, 150), anchor="ma")
    dr.text((750*S, ground+34*S), "RESALE · PROVEN GROUND", font=f["mono_sm"], fill=alpha(CREAM, 150), anchor="ma")
    # the plumb line — gold, the measure both are held to
    px = 540*S
    dr.line([(px, 428*S), (px, 636*S)], fill=alpha(GOLD, 225), width=2*S)
    d = 13*S
    dr.polygon([(px, 636*S-d), (px+d, 636*S), (px, 636*S+d), (px-d, 636*S)], fill=GOLD_HI)
    dr.line([(px-30*S, 428*S), (px+30*S, 428*S)], fill=alpha(GOLD_HI, 190), width=2*S)
    title_block(dr, f, "BUYER BRIEF · NEW VS. RESALE", "Two Builds", "EYES OPEN · EITHER DOOR")
    registration(dr, f, "PL. III", "48.24° N   114.30° W")
    footer(dr, f)
    finish(grain(img), "plate-3-wed-twobuilds.png")

# ------------------------------------------------ PL. IV — THU — THE WATCH (probate, dusk)
def plate_watch():
    img = base_plate((26, 20, 26), (48, 34, 33))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    cx, cy = W/2, 608*S
    # the thirty days — a ring of ticks held around the homestead
    rx, ry = 300*S, 196*S
    for k in range(30):
        ang = -math.pi/2 + k*math.tau/30
        ca, sa = math.cos(ang), math.sin(ang)
        x0, y0 = cx+rx*ca, cy+ry*sa
        L = 20*S if k % 5 == 0 else 12*S
        x1, y1 = cx+(rx+L)*ca, cy+(ry+L*0.7)*sa
        if k == 0:
            continue
        a = 150 if k % 5 == 0 else 95
        dr.line([(x0, y0), (x1, y1)], fill=alpha(CREAM, a), width=1*S)
    for lab, k in (("10", 10), ("20", 20)):
        ang = -math.pi/2 + k*math.tau/30
        x = cx+(rx+52*S)*math.cos(ang)
        y = cy+(ry+40*S)*math.sin(ang)
        dr.text((x, y), lab, font=f["mono_sm"], fill=alpha(CREAM, 120), anchor="mm")
    # day one — gold, spent once, at the top of the ring
    dr.line([(cx, cy-ry), (cx, cy-ry-24*S)], fill=alpha(GOLD, 240), width=3*S)
    dr.ellipse([cx-7*S, cy-ry-38*S, cx+7*S, cy-ry-24*S], fill=GOLD_HI)
    dr.text((cx+24*S, cy-ry-31*S), "DAY 1 · SECURE THE HOUSE", font=f["mono"], fill=alpha(GOLD_HI, 225), anchor="lm")
    # the homestead, held — dark gable, cream line, unlit and safe
    hw, hh = 132*S, 96*S
    hx0, hy0 = cx-hw/2, cy-hh/2+16*S
    dr.polygon([(hx0-13*S, hy0), (cx, hy0-68*S), (hx0+hw+13*S, hy0)], fill=(20, 15, 19), outline=alpha(CREAM, 180))
    dr.rectangle([hx0, hy0, hx0+hw, hy0+hh], fill=(20, 15, 19), outline=alpha(CREAM, 180), width=1*S)
    dr.rectangle([cx-15*S, hy0+34*S, cx+15*S, hy0+hh], outline=alpha(CREAM, 130), width=1*S)
    title_block(dr, f, "PROBATE · THE FIRST 30 DAYS", "The Watch", "SECURE · INSURE · HOLD STEADY")
    registration(dr, f, "PL. IV", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-4-thu-watch.png")

# ------------------------------------------------ PL. V — FRI — BASE CAMP (three towns)
def plate_basecamp():
    img = base_plate((12, 22, 34), (20, 38, 52))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    # faint ridge, far south — a low horizon band well clear of the stations
    r1 = ridge(41, 858*S, 34*S, 2.6, W)
    draw_ridge_strata(dr, r1, 874*S, CREAM, gap=8*S)
    dr.line(r1, fill=alpha(CREAM, 90), width=1*S)
    WF = (386*S, 446*S)
    CF = (768*S, 500*S)
    KA = (474*S, 714*S)
    # survey triangle, dashed
    for a, b in ((WF, CF), (CF, KA), (KA, WF)):
        dashed(dr, [a, b], alpha(CREAM, 130), width=1*S, dash=11*S, gap=8*S)
    # distances annotated at edge midpoints, nudged off the lines
    def midlab(a, b, text, ox_, oy_):
        mx, my = (a[0]+b[0])/2 + ox_, (a[1]+b[1])/2 + oy_
        dr.text((mx, my), text, font=f["mono_sm"], fill=alpha(CREAM, 120), anchor="mm")
    midlab(WF, CF, "±10 MI", 0, -28*S)
    midlab(CF, KA, "±12 MI", 66*S, 10*S)
    midlab(KA, WF, "±13 MI", -70*S, 0)
    # station marks — triangle in circle, the surveyor's monument
    def station(p, name, lx, ly, anchor):
        x, y = p
        dr.ellipse([x-15*S, y-15*S, x+15*S, y+15*S], outline=alpha(CREAM, 200), width=2*S)
        t = 8*S
        dr.polygon([(x, y-t), (x+t*0.87, y+t*0.5), (x-t*0.87, y+t*0.5)], outline=alpha(CREAM, 200))
        dr.text((x+lx, y+ly), name, font=f["mono"], fill=alpha(CREAM, 185), anchor=anchor)
    station(WF, "WHITEFISH", -26*S, -34*S, "rs")
    station(CF, "COLUMBIA FALLS", 30*S, -8*S, "lm")
    station(KA, "KALISPELL", -32*S, 6*S, "rm")
    # your base camp — the gold point inside the triangle, spent once
    gx, gy = 552*S, 560*S
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([gx-60*S, gy-60*S, gx+60*S, gy+60*S], fill=alpha(GOLD, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(30*S))
    img = Image.alpha_composite(img, glow); dr = ImageDraw.Draw(img, "RGBA")
    d = 15*S
    dr.polygon([(gx, gy-d), (gx+d, gy), (gx, gy+d), (gx-d, gy)], fill=GOLD_HI)
    dr.text((gx, gy+34*S), "YOUR BASE CAMP", font=f["mono"], fill=alpha(GOLD_HI, 225), anchor="ma")
    title_block(dr, f, "THREE TOWNS · ONE VALLEY", "Base Camp", "CHOOSE ON PURPOSE")
    registration(dr, f, "PL. V", "48.30° N   114.29° W")
    footer(dr, f)
    finish(grain(img), "plate-5-fri-basecamp.png")

# ------------------------------------------------ PL. VI — SAT — THE WINDOW (fall timing)
def plate_window():
    img = base_plate((13, 19, 31), (24, 33, 48))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    horizon = 706*S
    # ridge and strata beneath the horizon line
    r1 = ridge(29, horizon, 74*S, 2.1, W)
    draw_ridge_strata(dr, r1, horizon, CREAM, gap=8*S)
    dr.line(r1, fill=alpha(CREAM, 160), width=2*S)
    dr.line([(0, horizon), (W, horizon)], fill=alpha(CREAM, 110), width=1*S)
    # faint ground ticks below
    for i in range(9):
        x = (200 + i*85)*S
        dr.line([(x, horizon+22*S), (x, horizon+34*S)], fill=alpha(CREAM, 60), width=1*S)
    # the season's suns — five stations across the sky, one still worth chasing
    months = ["JUN", "JUL", "AUG", "SEP", "OCT"]
    arc = qbez((176*S, 540*S), (540*S, 386*S), (904*S, 540*S), 100)
    idxs = [0, 25, 50, 75, 100]
    for mo, i in zip(months, idxs):
        x, y = arc[i]
        if mo == "SEP":
            glow = Image.new("RGBA", (W, H), (0,0,0,0))
            gd = ImageDraw.Draw(glow)
            gd.ellipse([x-64*S, y-64*S, x+64*S, y+64*S], fill=alpha(GOLD, 62))
            glow = glow.filter(ImageFilter.GaussianBlur(28*S))
            img = Image.alpha_composite(img, glow); dr = ImageDraw.Draw(img, "RGBA")
            dr.ellipse([x-21*S, y-21*S, x+21*S, y+21*S], fill=GOLD_HI)
            dr.text((x, y-56*S), "SEP · THE SECOND WINDOW", font=f["mono"], fill=alpha(GOLD_HI, 230), anchor="ma")
        else:
            dr.ellipse([x-14*S, y-14*S, x+14*S, y+14*S], outline=alpha(CREAM, 150), width=2*S)
            ly = y+38*S if mo == "AUG" else y-58*S
            dr.text((x, ly), mo, font=f["mono_sm"], fill=alpha(CREAM, 120), anchor="ma")
    title_block(dr, f, "SELLER BRIEF · TIMING", "The Window", "THE QUIET SECOND SEASON")
    registration(dr, f, "PL. VI", "48.23° N   114.33° W")
    footer(dr, f)
    finish(grain(img), "plate-6-sat-window.png")

# ------------------------------------------------ PL. VII — SUN — THE QUIET SALE (discretion)
def plate_quietsale():
    img = base_plate((11, 16, 27), (22, 28, 42))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    # hushed vertical hatch field — everything held close
    rnd = random.Random(8)
    for x in range(int(120*S), int(W-120*S), int(8*S)):
        a = 12 + int(10 * (0.5+0.5*math.sin(x/(70*S))))
        dr.line([(x, 380*S+rnd.randint(0, 16)*S), (x, 812*S-rnd.randint(0, 16)*S)],
                fill=alpha(CREAM, a), width=1*S)
    # the ledger — bound, ruled, and closed
    lx0, ly0, lx1, ly1 = 348*S, 468*S, 732*S, 740*S
    dr.rectangle([lx0-16*S, ly0-16*S, lx1+16*S, ly1+16*S], outline=alpha(CREAM, 120), width=1*S)
    dr.rectangle([lx0, ly0, lx1, ly1], fill=(11, 15, 24), outline=alpha(CREAM, 200), width=2*S)
    # ruled entry lines, patient and even — the record kept, not shown
    for i in range(7):
        yy = ly0 + 36*S + i*30*S
        dr.line([(lx0+30*S, yy), (lx1-30*S, yy)], fill=alpha(CREAM, 60), width=1*S)
    # binding ticks along the spine
    for yy in range(int(ly0+14*S), int(ly1-10*S), int(24*S)):
        dr.line([(lx0, yy), (lx0+10*S, yy)], fill=alpha(CREAM, 110), width=1*S)
    # the seal — gold, spent once, holding the book shut
    sx, sy = 660*S, 742*S
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([sx-70*S, sy-70*S, sx+70*S, sy+70*S], fill=alpha(GOLD, 58))
    glow = glow.filter(ImageFilter.GaussianBlur(30*S))
    img = Image.alpha_composite(img, glow); dr = ImageDraw.Draw(img, "RGBA")
    dr.ellipse([sx-34*S, sy-34*S, sx+34*S, sy+34*S], fill=GOLD, outline=GOLD_HI, width=2*S)
    dr.ellipse([sx-20*S, sy-20*S, sx+20*S, sy+20*S], outline=(122, 96, 50), width=2*S)
    d = 9*S
    dr.polygon([(sx, sy-d), (sx+d, sy), (sx, sy+d), (sx-d, sy)], outline=(122, 96, 50))
    letterspace(dr, (W/2, 806*S), "IN CONFIDENCE", f["mono_sm"], alpha(CREAM, 130), 6*S, "ms")
    title_block(dr, f, "DISCRETION · BY DESIGN", "The Quiet Sale", "WHAT STAYS QUIET, STAYS YOURS", f["display_sm"])
    registration(dr, f, "PL. VII", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-7-sun-quietsale.png")

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    plate_crest(); plate_keeping(); plate_twobuilds(); plate_watch()
    plate_basecamp(); plate_window(); plate_quietsale()
