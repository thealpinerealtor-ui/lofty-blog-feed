#!/usr/bin/env python3
"""Big Sky Ledger — week of 2026-07-27 — seven survey plates, 1080x1080 @2x."""
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
    """Draw a dashed polyline."""
    if len(pts) < 2:
        return
    on = True
    budget = dash
    seg_start = pts[0]
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

# ------------------------------------------------ PL. I — MON — THE READING (market)
def plate_reading():
    img = base_plate((13, 19, 31), (24, 33, 48))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    m = 70*S
    # faint section lines
    for i in range(5):
        y = (430 + i*100)*S
        dr.line([(m+50*S, y), (W-m-50*S, y)], fill=alpha(CREAM, 16), width=1*S)
    # distant ridges, low
    r1 = ridge(31, 800*S, 120*S, 2.2, W)
    r2 = ridge(44, 828*S, 80*S, 3.3, W)
    draw_ridge_strata(dr, r1, 852*S, CREAM, gap=9*S)
    dr.line(r1, fill=alpha(CREAM, 120), width=1*S)
    dr.line(r2, fill=alpha(CREAM, 70), width=1*S)
    # the surveyor's staff — vertical graduated rod
    sx = W/2
    top_y, bot_y = 400*S, 828*S
    dr.line([(sx, top_y), (sx, bot_y)], fill=alpha(CREAM, 200), width=2*S)
    i = 0
    yy = top_y
    while yy <= bot_y:
        long = (i % 5 == 0)
        L = 26*S if long else 14*S
        a = 150 if long else 80
        dr.line([(sx-L, yy), (sx, yy)], fill=alpha(CREAM, a), width=1*S)
        yy += 26*S
        i += 1
    # base plate of the staff
    dr.line([(sx-52*S, bot_y), (sx+52*S, bot_y)], fill=alpha(CREAM, 160), width=2*S)
    # gold reading — spent once
    gy = 548*S
    dr.ellipse([sx-9*S, gy-9*S, sx+9*S, gy+9*S], fill=GOLD_HI)
    dr.line([(sx+9*S, gy), (sx+130*S, gy)], fill=alpha(GOLD, 220), width=2*S)
    dr.text((sx+142*S, gy), "PEAK INVENTORY", font=f["mono"], fill=alpha(GOLD_HI, 225), anchor="lm")
    dr.text((sx+142*S, gy+30*S), "LATE JULY · 2026", font=f["mono_sm"], fill=alpha(CREAM, 130), anchor="la")
    title_block(dr, f, "FLATHEAD VALLEY MARKET CHECK", "The Reading", "LATE JULY · 2026")
    registration(dr, f, "PL. I", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-1-mon-reading.png")

# ------------------------------------------------ PL. II — TUE — TWO PATHS (divorce)
def plate_twopaths():
    img = base_plate((14, 17, 29), (26, 30, 44))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    ox, oy = W/2, 462*S
    # quiet contour field around the origin
    for i in range(16):
        r = (60 + i*44)*S
        fade = max(10, 60 - i*3)
        dr.ellipse([ox-r, oy-r*0.6, ox+r, oy+r*0.6], outline=alpha(CREAM, fade), width=1*S)
    # two paths diverging — drawn gently, dashed, equal weight
    def path(sign):
        pts = []
        for t in [i/60 for i in range(61)]:
            x = ox + sign * (18*S + t*t * 300*S)
            y = oy + 34*S + t * 350*S
            x += sign * 26*S * math.sin(t*math.pi)
            pts.append((x, y))
        return pts
    pL, pR = path(-1), path(1)
    dashed(dr, pL, alpha(CREAM, 150), width=2*S)
    dashed(dr, pR, alpha(CREAM, 150), width=2*S)
    # each path arrives somewhere whole — small open circles
    for p in (pL[-1], pR[-1]):
        dr.ellipse([p[0]-10*S, p[1]-10*S, p[0]+10*S, p[1]+10*S], outline=alpha(CREAM, 190), width=2*S)
    # the home — one gold diamond, held with respect
    d = 20*S
    glow = Image.new("RGBA", (W, H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([ox-70*S, oy-70*S, ox+70*S, oy+70*S], fill=alpha(GOLD, 55))
    glow = glow.filter(ImageFilter.GaussianBlur(36*S))
    img = Image.alpha_composite(img, glow); dr = ImageDraw.Draw(img, "RGBA")
    dr.polygon([(ox, oy-d), (ox+d, oy), (ox, oy+d), (ox-d, oy)], fill=GOLD_HI)
    title_block(dr, f, "SELLING DURING DIVORCE", "Two Paths", "ONE HOME · TWO NEXT CHAPTERS")
    registration(dr, f, "PL. II", "48.20° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-2-tue-twopaths.png")

# ------------------------------------------------ PL. III — WED — EARNED GROUND (VA)
def plate_earnedground():
    img = base_plate((12, 18, 30), (22, 32, 44))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    # the parcel — a surveyed quadrilateral in gentle perspective
    A = (312*S, 540*S); B = (768*S, 522*S); C = (856*S, 796*S); D = (226*S, 812*S)
    # interior hatch: interpolate between left edge (A->D) and right edge (B->C)
    rows = 30
    for i in range(1, rows):
        t = i / rows
        lx = A[0] + (D[0]-A[0])*t; ly = A[1] + (D[1]-A[1])*t
        rx = B[0] + (C[0]-B[0])*t; ry = B[1] + (C[1]-B[1])*t
        inset = 14*S
        dr.line([(lx+inset, ly), (rx-inset, ry)], fill=alpha(CREAM, 22), width=1*S)
    dashed(dr, [A, B, C, D, A], alpha(CREAM, 180), width=2*S, dash=14*S, gap=10*S)
    # corner monuments
    for p in (A, C, D):
        dr.ellipse([p[0]-8*S, p[1]-8*S, p[0]+8*S, p[1]+8*S], outline=alpha(CREAM, 190), width=2*S)
    # the gold stake — one corner already claimed
    gx, gy = B
    dr.ellipse([gx-9*S, gy-9*S, gx+9*S, gy+9*S], fill=GOLD_HI)
    dr.line([(gx, gy-9*S), (gx, gy-120*S)], fill=alpha(GOLD, 230), width=2*S)
    dr.polygon([(gx, gy-120*S), (gx+56*S, gy-104*S), (gx, gy-88*S)], fill=GOLD)
    dr.text((gx-16*S, gy-128*S), "EARNED · 0% DOWN", font=f["mono"], fill=alpha(GOLD_HI, 225), anchor="rs")
    # small north arrow, top right of the field
    nx, ny = 880*S, 470*S
    dr.line([(nx, ny+34*S), (nx, ny-16*S)], fill=alpha(CREAM, 140), width=1*S)
    dr.polygon([(nx, ny-30*S), (nx-8*S, ny-10*S), (nx+8*S, ny-10*S)], fill=alpha(CREAM, 140))
    dr.text((nx, ny+48*S), "N", font=f["mono_sm"], fill=alpha(CREAM, 130), anchor="ma")
    title_block(dr, f, "VA HOME LOANS · BUYER BRIEF", "Earned Ground", "ZERO DOWN · FULLY EARNED")
    registration(dr, f, "PL. III", "48.19° N   114.27° W")
    footer(dr, f)
    finish(grain(img), "plate-3-wed-earnedground.png")

# ------------------------------------------------ PL. IV — THU — THE LONG WAY (estate, dusk)
def plate_longway():
    img = base_plate((26, 20, 26), (48, 34, 33))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    # low dusk ridge
    r1 = ridge(9, 812*S, 110*S, 2.4, W)
    draw_ridge_strata(dr, r1, 848*S, CREAM, gap=8*S)
    dr.line(r1, fill=alpha(CREAM, 110), width=1*S)
    # origin — far away
    P0 = (190*S, 470*S)
    dr.ellipse([P0[0]-9*S, P0[1]-9*S, P0[0]+9*S, P0[1]+9*S], outline=alpha(CREAM, 200), width=2*S)
    dr.text((P0[0], P0[1]+26*S), "ELSEWHERE", font=f["mono_sm"], fill=alpha(CREAM, 140), anchor="ma")
    # destination — the valley (quiet scrim so the marker reads against the strata)
    P1 = (856*S, 712*S)
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scrim)
    sd.ellipse([P1[0]-190*S, P1[1]-70*S, P1[0]+190*S, P1[1]+110*S], fill=(38, 28, 29, 215))
    scrim = scrim.filter(ImageFilter.GaussianBlur(26*S))
    img = Image.alpha_composite(img, scrim); dr = ImageDraw.Draw(img, "RGBA")
    sq = 11*S
    dr.rectangle([P1[0]-sq, P1[1]-sq, P1[0]+sq, P1[1]+sq], outline=alpha(CREAM, 210), width=2*S)
    dr.text((P1[0]+2*S, P1[1]+30*S), "FLATHEAD VALLEY", font=f["mono_sm"], fill=alpha(CREAM, 170), anchor="ma")
    # the gold route — one gesture, the distance handled
    Cx, Cy = 560*S, 330*S
    arc = []
    for t in [i/90 for i in range(91)]:
        x = (1-t)**2 * P0[0] + 2*(1-t)*t*Cx + t*t*P1[0]
        y = (1-t)**2 * P0[1] + 2*(1-t)*t*Cy + t*t*P1[1]
        arc.append((x, y))
    dashed(dr, arc, alpha(GOLD, 225), width=2*S, dash=16*S, gap=11*S)
    # waypoint ticks across the route
    for t in (0.25, 0.5, 0.75):
        i = int(t*90)
        x, y = arc[i]
        x2, y2 = arc[i+1]
        ang = math.atan2(y2-y, x2-x) + math.pi/2
        L = 9*S
        dr.line([(x-L*math.cos(ang), y-L*math.sin(ang)), (x+L*math.cos(ang), y+L*math.sin(ang))],
                fill=alpha(GOLD_HI, 190), width=2*S)
    title_block(dr, f, "INHERITED · OUT OF STATE", "The Long Way", "HANDLED HERE · WHEREVER YOU ARE")
    registration(dr, f, "PL. IV", "48.19° N   114.31° W")
    footer(dr, f)
    finish(grain(img), "plate-4-thu-longway.png")

# ------------------------------------------------ PL. V — FRI — THE LAKE (bathymetry)
def plate_lake():
    img = base_plate((12, 22, 34), (18, 40, 50))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    cx, cy = W/2, 640*S
    rnd = random.Random(12)
    ph = [rnd.uniform(0, math.tau) for _ in range(3)]
    def shore(scale, drift):
        pts = []
        for k in range(121):
            th = k/120 * math.tau
            r = 1.0 + 0.13*math.sin(2*th+ph[0]) + 0.08*math.sin(3*th+ph[1]) + 0.05*math.sin(5*th+ph[2])
            rx = 300*S * r * scale
            ry = 218*S * r * scale
            pts.append((cx + rx*math.cos(th), cy + drift + ry*math.sin(th)))
        return pts
    # shore ticks radiating outward
    outline = shore(1.0, 0)
    for k in range(0, 120, 6):
        x, y = outline[k]
        vx, vy = x-cx, y-cy
        L = math.hypot(vx, vy)
        ux, uy = vx/L, vy/L
        dr.line([(x+ux*8*S, y+uy*8*S), (x+ux*22*S, y+uy*22*S)], fill=alpha(CREAM, 60), width=1*S)
    dr.line(outline + [outline[0]], fill=alpha(CREAM, 190), width=2*S)
    # depth contours, drifting toward the deep point
    depths = [(0.80, "100"), (0.60, "200"), (0.42, "300")]
    for i, (sc, lab) in enumerate(depths):
        pts = shore(sc, (i+1)*14*S)
        dr.line(pts + [pts[0]], fill=alpha(CREAM, 110 - i*26), width=1*S)
        # labels cascade along the lower-left shore, clear of the sounding
        lx, ly = pts[66 + i*2]
        dr.text((lx-8*S, ly+6*S), lab, font=f["mono_sm"], fill=alpha(CREAM, 135), anchor="rm")
    # the gold sounding — deepest point, spent once
    gx, gy = cx + 30*S, cy + 52*S
    dr.ellipse([gx-8*S, gy-8*S, gx+8*S, gy+8*S], fill=GOLD_HI)
    dr.line([(gx, gy-8*S), (gx, gy-96*S)], fill=alpha(GOLD, 220), width=2*S)
    dr.text((gx, gy-122*S), "SOUNDING · 370 FT", font=f["mono"], fill=alpha(GOLD_HI, 225), anchor="ma")
    title_block(dr, f, "LIFE ON FLATHEAD LAKE", "The Lake", "BIGFORK · LAKESIDE · SOMERS")
    registration(dr, f, "PL. V", "47.90° N   114.07° W")
    footer(dr, f)
    finish(grain(img), "plate-5-fri-lake.png")

# ------------------------------------------------ PL. VI — SAT — THE INSPECTION (seller)
def plate_inspection():
    img = base_plate((16, 18, 24), (28, 30, 38))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    # house elevation — draftsman's callout sheet
    bx0, bx1 = 400*S, 680*S
    by0, by1 = 570*S, 736*S
    peak = (540*S, 452*S)
    # roof hatch
    for i in range(1, 12):
        t = i/12
        yA = peak[1] + (by0 - peak[1]) * t
        xL = peak[0] + (bx0 - 26*S - peak[0]) * t
        xR = peak[0] + (bx1 + 26*S - peak[0]) * t
        dr.line([(xL, yA), (xR, yA)], fill=alpha(CREAM, 26), width=1*S)
    # body hatch
    for x in range(int(bx0+10*S), int(bx1-8*S), int(9*S)):
        dr.line([(x, by0+8*S), (x, by1-6*S)], fill=alpha(CREAM, 16), width=1*S)
    dr.polygon([(bx0-26*S, by0), peak, (bx1+26*S, by0)], outline=alpha(CREAM, 190))
    dr.rectangle([bx0, by0, bx1, by1], outline=alpha(CREAM, 190), width=2*S)
    # chimney / stove flue
    dr.rectangle([612*S, 478*S, 640*S, 540*S], outline=alpha(CREAM, 170), width=2*S)
    # well (left of house) and septic (right, buried)
    dr.ellipse([292*S-10*S, 782*S-10*S, 292*S+10*S, 782*S+10*S], outline=alpha(CREAM, 180), width=2*S)
    dashed(dr, [(756*S, 776*S), (836*S, 776*S), (836*S, 806*S), (756*S, 806*S), (756*S, 776*S)],
           alpha(CREAM, 150), width=1*S, dash=8*S, gap=6*S)
    # callout leaders + labels (mono, clinical)
    def callout(from_pt, to_pt, text, anchor):
        dr.line([from_pt, to_pt], fill=alpha(CREAM, 120), width=1*S)
        dr.ellipse([from_pt[0]-4*S, from_pt[1]-4*S, from_pt[0]+4*S, from_pt[1]+4*S], fill=alpha(CREAM, 170))
        off = 12*S if anchor == "lm" else -12*S
        dr.text((to_pt[0]+off, to_pt[1]), text, font=f["mono_sm"], fill=alpha(CREAM, 160), anchor=anchor)
    callout((626*S, 486*S), (796*S, 442*S), "WOOD STOVE · FLUE", "lm")
    callout((660*S, 539*S), (800*S, 585*S), "ROOF · SNOW LOAD", "lm")
    callout((796*S, 791*S), (900*S, 700*S), "SEPTIC", "lm")
    callout((292*S, 772*S), (200*S, 640*S), "WELL · FLOW TEST", "lm")
    # the gold line — the foundation the whole deal rests on
    dr.line([(bx0-30*S, by1+16*S), (bx1+30*S, by1+16*S)], fill=alpha(GOLD, 235), width=3*S)
    title_block(dr, f, "SELLER BRIEF · INSPECTIONS", "The Inspection", "FOUND FIRST · FIXED FIRST")
    registration(dr, f, "PL. VI", "48.23° N   114.33° W")
    footer(dr, f)
    finish(grain(img), "plate-6-sat-inspection.png")

# ------------------------------------------------ PL. VII — SUN — THE PASS (negotiation)
def plate_pass():
    img = base_plate((11, 16, 27), (22, 28, 42))
    dr = ImageDraw.Draw(img, "RGBA")
    f = fonts()
    base = 828*S
    rnd = random.Random(23)
    ph = [rnd.uniform(0, math.tau) for _ in range(3)]
    pts = []
    for x in range(0, W+1, 4):
        g1 = 330*S * math.exp(-((x - 300*S)/(212*S))**2)
        g2 = 352*S * math.exp(-((x - 812*S)/(206*S))**2)
        n = 14*S * math.sin(x/(52*S) + ph[0]) + 8*S * math.sin(x/(23*S) + ph[1])
        pts.append((x, base - g1 - g2 + n*0.4))
    draw_ridge_strata(dr, pts, 850*S, CREAM, gap=8*S)
    dr.line(pts, fill=alpha(CREAM, 170), width=2*S)
    # the route through the pass — dashed, patient
    R0, C, R1 = (150*S, 826*S), (546*S, 596*S), (952*S, 826*S)
    route = []
    for t in [i/80 for i in range(81)]:
        x = (1-t)**2 * R0[0] + 2*(1-t)*t*C[0] + t*t*R1[0]
        y = (1-t)**2 * R0[1] + 2*(1-t)*t*C[1] + t*t*R1[1]
        route.append((x, y))
    dashed(dr, route, alpha(CREAM, 130), width=1*S, dash=10*S, gap=8*S)
    # saddle point — find lowest ridge y between the peaks
    saddle = min((p for p in pts if 420*S < p[0] < 680*S), key=lambda p: -p[1])
    sx, sy = saddle
    # gold cairn at the pass — spent once
    d = 16*S
    dr.polygon([(sx, sy-d), (sx+d, sy), (sx, sy+d), (sx-d, sy)], fill=GOLD_HI)
    dr.line([(sx, sy-d), (sx, sy-92*S)], fill=alpha(GOLD, 200), width=1*S)
    dr.text((sx, sy-120*S), "THE PASS · 5213 FT", font=f["mono"], fill=alpha(GOLD_HI, 225), anchor="ma")
    title_block(dr, f, "NEGOTIATION UNDER PRESSURE", "The Pass", "CALM IS A STRATEGY")
    registration(dr, f, "PL. VII", "48.32° N   113.35° W")
    footer(dr, f)
    finish(grain(img), "plate-7-sun-pass.png")

if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    plate_reading(); plate_twopaths(); plate_earnedground(); plate_longway()
    plate_lake(); plate_inspection(); plate_pass()
