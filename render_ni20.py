#!/usr/bin/env python3
"""news-image-20261120 — ROUND 3 renderer (fresh build).

One-page broadsheet for Friday 20 November 2026, 40 stories.
Renders at 2048x2048 (2x supersample) and downscales to 1024x1024.
Fonts: Playfair Display (masthead/headlines) + Archivo (body), both
open-licensed variable fonts bundled in ./fonts/.

R3 changes vs R2 (coordinator spec):
  1. Map: solid navy panel, solid beige continents, red numbered pins 1-13.
  2. Richer lead art: layered cyclone spiral, Kyiv skyline + missile
     trails + blasts, COP31 globe + big red thermometer + $120BN badge.
  3. Every feature panel (4-13) gets a real mini-illustration.
  4. Briefs 14-40 in TWO numbered columns with red numerals.
  5. 2x supersample + downscale, stronger contrast, consistent red accent.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
S = 2                      # supersample factor
W, H = 1024 * S, 1024 * S
M = 28 * S                 # outer margin

PAPER = (247, 241, 226)
INK = (22, 32, 61)         # deep navy ink
INK2 = (44, 52, 78)
RED = (193, 39, 45)
RED_DK = (150, 24, 30)
NAVY = (16, 30, 51)        # map / night panels
NAVY2 = (24, 44, 74)
LAND = (232, 217, 176)     # solid beige continents
LAND2 = (214, 196, 150)
CREAM = (247, 241, 226)
GOLD = (217, 164, 65)
TEAL = (46, 125, 107)
GREEN = (46, 125, 70)
GREY = (90, 90, 82)
LINE = (22, 32, 61)

PF = os.path.join(BASE, "fonts", "PlayfairDisplay-Black.ttf")
PFI = os.path.join(BASE, "fonts", "PlayfairDisplay-Italic.ttf")
AR = os.path.join(BASE, "fonts", "Archivo.ttf")

_cache = {}


def font(path, size, weight=None):
    key = (path, size, weight)
    if key not in _cache:
        f = ImageFont.truetype(path, int(size))
        if weight is not None:
            try:
                f.set_variation_by_axes([weight])
            except Exception:
                pass
        _cache[key] = f
    return _cache[key]


def serif(size, weight=900):
    return font(PF, size, weight)


def serif_it(size, weight=700):
    return font(PFI, size, weight)


def sans(size, weight=600):
    return font(AR, size, weight)


def text_w(d, s, f):
    return d.textlength(s, font=f)


def wrap(d, s, f, maxw):
    """Greedy word wrap; returns list of lines."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(d, t, f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, s, f, x, y, maxw, fill, lh=None, max_lines=None):
    lines = wrap(d, s, f, maxw)
    if max_lines:
        lines = lines[:max_lines]
    if lh is None:
        lh = int(f.size * 1.28)
    for ln in lines:
        d.text((x, y), ln, font=f, fill=fill)
        y += lh
    return y


def trunc(d, s, f, maxw):
    if text_w(d, s, f) <= maxw:
        return s
    while s and text_w(d, s + "…", f) > maxw:
        s = s[:-1]
    return s + "…"


def starburst(d, cx, cy, r1, r2, n, fill):
    pts = []
    for i in range(n * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.pi * i / n - math.pi / 2
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


def arc_poly(cx, cy, r, a0, a1, steps=40):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / steps)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / steps)))
            for i in range(steps + 1)]


# ---------------------------------------------------------------- data
KICK_L = "THE WORLD IN ONE DAY"
KICK_R = "FRIDAY'S NEWS  ·  ONE PAGE  ·  40 STORIES  ·  7 REGIONS"
MASTHEAD = "Friday 20 November 2026"
SUBLINE = ("Cyclone Akvan strikes India  ·  Ballistic missiles hit Kyiv  ·  "
           "COP31 deadlocked  ·  Asian AI sell-off")

KPIS = [
    ("300,000+", "evacuated ahead of Cyclone Akvan"),
    ("~30", "ballistic missiles fired at Kyiv"),
    ("-7%", "Asia shares' worst week since 2020"),
    ("2.3%", "Japan Oct headline CPI; BoJ eyed"),
    ("118", "Phillips' historic century vs India"),
    ("8 yrs", "BepiColombo reaches Mercury"),
]
REGIONS = [("EUROPE", 6, (31, 58, 95)), ("ASIA", 8, (193, 39, 45)),
           ("MIDDLE EAST", 6, (196, 120, 40)), ("AFRICA", 9, (46, 125, 70)),
           ("AMERICAS", 5, (90, 60, 140)), ("OCEANIA", 3, (0, 130, 140)),
           ("WORLD", 3, (90, 90, 82))]

LEADS = [
    dict(n=1, loc="ODISHA, INDIA · CYCLONE", src="IMD / THE HINDU",
         head="Cyclone Akvan makes landfall in eastern India",
         body=("Severe storm crosses the Andhra–Odisha coast near Gopalpur; "
               "300,000+ evacuated, winds 90–100 kmph gusting to 110, "
               "423 rescue teams deployed, schools shut. (IMD, The Hindu)"),
         art="akvan"),
    dict(n=2, loc="KYIV, UKRAINE · WAR", src="KYIV POST / REUTERS",
         head="Russia fires wave of ~30 ballistic missiles at Kyiv",
         body=("Seven overnight waves batter energy and transport sites; "
               "fires burn in three districts, Dutch and Austrian "
               "embassies damaged. (Kyiv Post, Reuters)"),
         art="kyiv"),
    dict(n=3, loc="ANTALYA, TÜRKIYE · CLIMATE", src="UN NEWS / REUTERS",
         head="COP31 reaches its final day deadlocked",
         body=("Closing draft omits the fossil-fuel phase-out while $120bn "
               "adaptation finance stays unresolved; hosts push a "
               "'35 by 35' clean-power goal. (UN News, Reuters)"),
         art="cop31"),
]

FEATURES = [
    dict(n=4, loc="SEOUL / TOKYO", src="REUTERS",
         head="AI sell-off sinks Asia to worst week since 2020",
         body="Taiex -6.8%, KOSPI -5.4%, Nikkei -4.9% intraday. (Reuters)",
         art="markets"),
    dict(n=5, loc="MERCURY", src="ESA / BBC",
         head="BepiColombo reaches Mercury after 8 years",
         body="ESA/JAXA probe ends its 6bn-mile trip. (ESA, BBC)",
         art="mercury"),
    dict(n=6, loc="NEW YORK", src="REUTERS",
         head="Anthropic ends first day up 17%",
         body="Opens $111.50, closes $97.17 — 17% above its $83 offer. (Reuters)",
         art="anthropic"),
    dict(n=7, loc="TOKYO", src="REUTERS",
         head="Japan inflation hits 2.3%; BoJ hike eyed",
         body="Oct CPI up from 2.1%; core 2.2%, above 2% a second month. (Reuters)",
         art="inflation"),
    dict(n=8, loc="BEIJING", src="PBOC / REUTERS",
         head="China holds lending rates for 18th month",
         body="1-year LPR 3.0%, 5-year 3.5%, as expected. (PBOC)",
         art="rates"),
    dict(n=9, loc="BRUSSELS", src="EU COUNCIL",
         head="Burnham holds first EU-UK reset summit",
         body="Costa & von der Leyen host the UK PM; agrifood & carbon links eyed. (EU Council)",
         art="euuk"),
    dict(n=10, loc="WELLINGTON", src="ICC / AP",
         head="Phillips makes history with 118 vs India",
         body="First NZ batter with centuries in all 3 formats vs India. (ICC, AP)",
         art="cricket"),
    dict(n=11, loc="SAN SALVADOR", src="AP",
         head="Bukele registers for third-term bid",
         body="Files for the Feb 2027 vote; rights groups object. (AP)",
         art="bukele"),
    dict(n=12, loc="SENEGAL", src="AL JAZEERA",
         head="Migrant boat capsizes off Yenne; 4 dead",
         body="Dozens missing from ~50–100 aboard as Canary arrivals surge. (Al Jazeera)",
         art="boat"),
    dict(n=13, loc="ROME", src="CGIL / AFP",
         head="Italy's CGIL holds 24-hr general strike",
         body="Unions rally in ~100 squares against the 2027 budget; transit hit. (CGIL, AFP)",
         art="strike"),
]

# briefs 14-40: (place, text) — one line each, verified Friday 20 Nov 2026
BRIEFS = [
    ("FRANCE", "Fire in 18-storey flats: 1 dead, 15 hurt"),
    ("TAIWAN", "Council candidate freed on NT$500k bail"),
    ("TAIWAN", "Spouse inheritance share up to two-thirds"),
    ("VIETJET", "Vietjet adds routes to the Philippines"),
    ("WORLD", "GTA 6 sales pass The Odyssey's $1.80bn"),
    ("GENOA", "Airport shut 4 hours after drones seen"),
    ("EUROPE", "Ready for talks with Russia on war end"),
    ("JAPAN", "Hayabusa2 engine fault ends landing bid"),
    ("HORMUZ", "Two oil tankers hit mines, catch fire"),
    ("LEBANON", "Israel says it hit 40 Hezbollah sites"),
    ("AFRICA", "260m children live in conflict zones"),
    ("NEW ZEALAND", "Votes Saturday: Luxon vs Hipkins"),
    ("RIYADH", "MBS phoned Trump twice over Houthis"),
    ("WASHINGTON", "Vance: US in direct talks with Houthis"),
    ("YEMEN", "Houthis seize Hanish isles, Mocha — CLAIM"),
    ("SAUDI", "East-West pipeline shut after drone hit"),
    ("NIGERIA", "Mob kills Osun crash survivor; hunt on"),
    ("SOUTH AFRICA", "SACP pushes back on ANC entitlement"),
    ("AFRICA", "More climate cash? 'Use what's pledged'"),
    ("BURUNDI", "Banyamulenge arrests: 25+ refugees held"),
    ("CAR", "Sakaï 2 power plan to light 300,000 homes"),
    ("ESWATINI", "Youth 'loses kidney' in overseas job scam"),
    ("SENEGAL", "Armed Forces Day: Faye urges mobilisation"),
    ("WASHINGTON", "Trump back from China; presser today"),
    ("CINCINNATI", "Trump pardons baseball's Pete Rose"),
    ("CRYPTO", "Bitcoin $62,150, −1.85%, as crypto slides"),
    ("SYDNEY", "LG names Jeff Roh Australia, NZ boss"),
]

DATE_CHECK = ("ICJ Myanmar genocide verdict · Trump–Xi–Putin Shenzhen trilateral · "
              "Houthi strike on Riyadh's PIF tower · Anthropic's $83 IPO pricing · "
              "GTA VI midnight launch · Voyager 1 one light-day · Senate 48–51 Iran "
              "war-powers vote · $190.4m Van Gogh sale · Kerch Bridge attack · "
              "Han Duck-soo's acquittal · EU's €45bn Ukraine loan.")

# (lat, lon) pins 1-13 and dots 14-40, in story order
PINS = [(19.3, 84.9), (50.45, 30.5), (36.9, 30.7), (37.5, 127.0),
        (5.2, -52.8), (40.7, -74.0), (35.7, 139.7), (39.9, 116.4),
        (50.85, 4.35), (-41.3, 174.8), (13.7, -89.2), (14.6, -17.1),
        (41.9, 12.5)]
DOTS = [(46.0, 2.0), (23.7, 121.0), (23.7, 121.0), (14.6, 121.0),
        (51.5, -0.1), (44.4, 8.9), (55.7, 37.6), (35.7, 139.7),
        (26.5, 56.2), (33.9, 35.8), (0.0, 20.0), (-41.3, 174.8),
        (24.7, 46.7), (38.9, -77.0), (13.7, 42.7), (24.7, 47.0),
        (7.5, 4.5), (-29.0, 25.0), (0.0, 20.0), (-3.4, 29.9),
        (6.6, 20.9), (-26.5, 31.5), (14.7, -17.4), (38.9, -77.0),
        (39.1, -84.5), (40.7, -74.0), (-33.9, 151.2)]

# simplified solid-continent polygons (lon, lat)
CONTINENTS = [
    # North America
    [(-168, 66), (-158, 58), (-152, 60), (-140, 60), (-135, 58), (-130, 54),
     (-125, 49), (-124, 42), (-120, 34), (-114, 29), (-110, 24), (-105, 20),
     (-97, 16), (-92, 15), (-86, 12), (-83, 9), (-79, 9), (-81, 13),
     (-84, 16), (-87, 21), (-90, 21), (-97, 26), (-93, 30), (-89, 30),
     (-84, 30), (-81, 26), (-76, 35), (-74, 40), (-70, 42), (-66, 45),
     (-60, 47), (-55, 47), (-60, 52), (-65, 60), (-68, 58), (-75, 62),
     (-85, 66), (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
     (-155, 71), (-165, 68)],
    # Greenland
    [(-45, 60), (-40, 64), (-32, 68), (-25, 70), (-20, 74), (-25, 78),
     (-35, 80), (-50, 80), (-58, 76), (-55, 70), (-52, 64)],
    # South America
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
     (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
     (-66, -55), (-68, -50), (-62, -41), (-57, -38), (-52, -33), (-48, -28),
     (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
     (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12), (-77, 8)],
    # Africa
    [(-17, 15), (-16, 20), (-13, 27), (-10, 31), (-6, 34), (-2, 35), (5, 37),
     (10, 37), (11, 34), (15, 32), (20, 32), (25, 32), (30, 31), (33, 27),
     (35, 23), (37, 18), (40, 15), (43, 12), (48, 11), (51, 10), (46, 5),
     (42, 0), (40, -5), (40, -10), (37, -15), (35, -20), (32, -26),
     (28, -33), (20, -35), (16, -28), (14, -22), (12, -17), (13, -12),
     (12, -6), (9, 4), (4, 6), (-3, 5), (-8, 5), (-13, 8), (-17, 12)],
    # Eurasia (mainland, peninsulas cut at their bases)
    [(-10, 36), (-9, 43), (-2, 48), (-4, 49), (1, 51), (4, 53), (8, 55),
     (8, 57), (11, 58), (6, 60), (5, 62), (12, 65), (18, 69), (26, 71),
     (32, 70), (40, 68), (48, 69), (55, 69), (62, 70), (68, 72), (74, 73),
     (80, 73), (86, 75), (95, 76), (104, 77), (112, 74), (118, 73),
     (127, 72), (135, 71), (142, 72), (150, 70), (158, 70), (168, 67),
     (178, 66), (178, 62), (170, 60), (162, 59), (158, 52), (156, 50),
     (150, 59), (142, 59), (141, 53), (140, 46), (137, 38), (133, 34),
     (130, 32), (127, 35), (126, 38), (122, 40), (120, 35), (121, 31),
     (119, 26), (113, 22), (109, 18), (106, 10), (103, 8), (100, 7),
     (98, 11), (96, 15), (93, 18), (91, 22), (88, 22), (86, 20),
     (83, 18), (80, 14), (77, 8), (75, 11), (73, 16), (70, 20), (67, 24),
     (61, 25), (57, 26), (52, 27), (50, 29), (48, 30), (44, 29), (39, 31),
     (36, 36), (33, 36), (30, 36), (27, 36), (23, 36), (19, 40), (16, 38),
     (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37), (-6, 36), (-9, 37)],
    # India
    [(68, 23), (70, 20), (73, 16), (75, 11), (77, 8), (79, 10), (80, 13),
     (82, 17), (86, 20), (88, 22), (89, 22), (86, 21), (83, 19), (80, 16),
     (77, 13), (74, 15), (72, 19), (70, 22)],
    # Arabia
    [(43, 29), (46, 29), (49, 29), (51, 27), (54, 26), (56, 26), (58, 23),
     (59, 20), (57, 18), (55, 17), (52, 15), (48, 14), (45, 13), (43, 13),
     (41, 16), (39, 20), (38, 24), (39, 27), (41, 29)],
    # Malay peninsula + Sumatra
    [(100, 7), (102, 4), (104, 2), (101, 6), (99, 9), (98, 12), (100, 14),
     (99, 10), (97, 14), (95, 5), (98, 2), (101, -1), (104, -3), (106, -6),
     (104, -4), (101, 0), (97, 3)],
    # Borneo
    [(109, 1), (111, 3), (114, 4), (117, 6), (118, 2), (116, -1),
     (113, -3), (110, -3), (109, 0)],
    # Java
    [(105, -6), (108, -7), (111, -7), (114, -8), (114, -9), (110, -8),
     (106, -7)],
    # New Guinea
    [(131, -1), (134, -3), (137, -4), (141, -6), (145, -7), (147, -9),
     (144, -8), (141, -8), (138, -7), (135, -4), (132, -2)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 37),
     (141, 39), (141, 41), (142, 43), (144, 44), (142, 42), (140, 39),
     (139, 37), (137, 36), (135, 34), (132, 33)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-3, 50)],
    # New Zealand
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
     (174, -41), (171, -44), (168, -46)],
    # Australia
    [(114, -22), (114, -30), (115, -33), (118, -35), (124, -33), (129, -32),
     (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -23), (146, -19), (142, -11), (141, -13),
     (137, -12), (136, -15), (135, -12), (132, -11), (130, -13), (128, -14),
     (126, -14), (124, -16), (122, -17), (120, -20), (116, -21)],
    # Philippines
    [(120, 18), (122, 17), (123, 14), (122, 11), (121, 13), (120, 16)],
]

# ---------------------------------------------------------------- art
def art_akvan(d, x, y, w, h):
    """Layered cyclone spiral over the Odisha coast."""
    d.rectangle([x, y, x + w, y + h], fill=(23, 68, 96))
    # sea shading bands (right = Bay of Bengal)
    for i, c in enumerate([(28, 84, 116), (33, 100, 134), (38, 116, 150)]):
        d.rectangle([x + w * (0.45 + i * 0.18), y, x + w * (0.63 + i * 0.18),
                     y + h], fill=c)
    # land mass (left): pale sand with coastline curve
    coast = [(x, y), (x + w * 0.52, y), (x + w * 0.46, y + h * 0.30),
             (x + w * 0.55, y + h * 0.55), (x + w * 0.44, y + h * 0.80),
             (x + w * 0.50, y + h), (x, y + h)]
    d.polygon(coast, fill=(238, 226, 196))
    d.line([(x + w * 0.52, y), (x + w * 0.46, y + h * 0.30),
            (x + w * 0.55, y + h * 0.55), (x + w * 0.44, y + h * 0.80),
            (x + w * 0.50, y + h)], fill=(120, 100, 60), width=3 * S)
    # fields / towns on land
    for fx, fy in [(0.12, 0.22), (0.22, 0.45), (0.10, 0.68), (0.30, 0.15)]:
        d.rectangle([x + w * fx, y + h * fy, x + w * (fx + 0.05),
                     y + h * (fy + 0.04)], fill=(196, 164, 110))
    # layered spiral: concentric shaded rings + white arms
    cx, cy = x + w * 0.68, y + h * 0.50
    for rf, c in [(0.46, (10, 48, 72)), (0.38, (16, 62, 90)),
                  (0.30, (24, 78, 106)), (0.22, (36, 100, 128)),
                  (0.14, (52, 126, 152))]:
        r = rf * h
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)
    for rf, a0, a1 in [(0.42, 20, 300), (0.34, 140, 60), (0.26, 250, 160),
                       (0.18, 20, 300), (0.10, 90, 30)]:
        d.line(arc_poly(cx, cy, rf * h, a0, a1), fill=(255, 255, 255),
               width=max(3 * S, int(h * 0.016)))
    er = h * 0.03
    d.ellipse([cx - er, cy - er, cx + er, cy + er], fill=(255, 255, 255))
    # Gopalpur marker on the coast
    gx, gy = x + w * 0.50, y + h * 0.42
    gr = h * 0.035
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=RED,
              outline=(255, 255, 255), width=3 * S)
    d.ellipse([x + w * 0.05, y + h * 0.80, x + w * 0.05 + 8 * S,
               y + h * 0.80 + 8 * S], fill=RED)
    d.text((x + w * 0.05 + 12 * S, y + h * 0.80), "GOPALPUR",
           font=sans(12 * S, 800), fill=RED_DK)
    d.text((x + w * 0.70, y + h * 0.05), "BAY OF BENGAL",
           font=sans(10 * S, 700), fill=(200, 225, 235))
    # wind barbs along the spiral edge
    for a in (30, 110, 200, 290):
        px = cx + 0.50 * h * math.cos(math.radians(a))
        py = cy + 0.50 * h * math.sin(math.radians(a))
        d.line([(px, py), (px + 12 * S, py - 6 * S)], fill=(255, 255, 255),
               width=3 * S)


def art_kyiv(d, x, y, w, h):
    """Night skyline, missile trails, explosions."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.ellipse([x + w * 0.82, y + h * 0.08, x + w * 0.94, y + h * 0.30],
              fill=(240, 226, 180))
    # missile trails: glowing arcs
    for (sx, sy, ex, ey) in [(0.08, 0.95, 0.38, 0.18), (0.30, 0.98, 0.55, 0.10),
                             (0.62, 0.98, 0.82, 0.22), (0.45, 0.95, 0.68, 0.30)]:
        pts = []
        for i in range(25):
            t = i / 24
            pts.append((x + w * (sx + (ex - sx) * t),
                        y + h * (sy + (ey - sy) * t - 0.28 * math.sin(math.pi * t))))
        d.line(pts, fill=(250, 170, 60), width=4 * S)
        d.ellipse([x + w * ex - 5 * S, y + h * ey - 5 * S,
                   x + w * ex + 5 * S, y + h * ey + 5 * S], fill=(255, 220, 120))
    # skyline silhouette with lit windows
    base = y + h
    spans = [(0.00, 0.16, 0.52), (0.17, 0.11, 0.72), (0.29, 0.15, 0.60),
             (0.45, 0.10, 0.80), (0.56, 0.17, 0.55), (0.74, 0.12, 0.68),
             (0.87, 0.13, 0.58)]
    for fx, fw, fh in spans:
        d.rectangle([x + w * fx, base - h * fh, x + w * (fx + fw), base],
                    fill=(10, 18, 34))
        btop = base - h * fh
        for wy in range(3):
            for wx in range(3):
                if (int(fx * 100) + wy * 3 + wx) % 3:
                    wyy = btop + 6 * S + wy * (h * fh - 14 * S) / 3
                    d.rectangle([x + w * (fx + 0.015 + wx * 0.035), wyy,
                                 x + w * (fx + 0.03 + wx * 0.035),
                                 wyy + 5 * S], fill=(255, 200, 90))
    # explosions (in front of the skyline)
    for ex, ey, rf in [(0.30, 0.60, 0.15), (0.58, 0.68, 0.12),
                       (0.86, 0.56, 0.10)]:
        r = rf * h
        starburst(d, x + w * ex, y + h * ey, r, r * 0.45, 8, (255, 140, 30))
        starburst(d, x + w * ex, y + h * ey, r * 0.55, r * 0.25, 8,
                  (255, 210, 90))
    # smoke columns
    for sx in (0.32, 0.60):
        for i in range(3):
            sr = h * (0.03 + i * 0.02)
            scy = base - h * 0.62 - i * h * 0.10
            d.ellipse([x + w * sx - sr, scy - sr * 0.5,
                       x + w * sx + sr, scy + sr * 0.5],
                      fill=(120, 120, 130))


def art_cop31(d, x, y, w, h):
    """Globe with continents + big red thermometer + finance-gap badge."""
    d.rectangle([x, y, x + w, y + h], fill=(222, 232, 222))
    # globe
    cx, cy, r = x + w * 0.24, y + h * 0.52, h * 0.46
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(64, 130, 180))
    for (gx, gy, gr) in [(0.22, 0.40, 0.13), (0.36, 0.62, 0.11),
                         (0.26, 0.72, 0.08), (0.40, 0.38, 0.07)]:
        d.ellipse([x + w * gx - gr * h, y + h * gy - gr * h,
                   x + w * gx + gr * h, y + h * gy + gr * h],
                  fill=(96, 170, 96))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(30, 60, 90),
              width=3 * S)
    d.arc([cx - r * 0.55, cy - r, cx + r * 0.55, cy + r], 270, 90,
          fill=(255, 255, 255), width=2 * S)
    # thermometer, right side — labels on the LEFT of the tube, bulb kept
    # above the $120BN badge (badge covers art y +76..+116, drawn after).
    # (R3 fix: right-side "40°/30°/20°" crowded the art edge and the old
    # bulb ran under the badge. Only top/bottom labels: three 26px labels
    # cannot fit with clear gaps inside a ~62px tube.)
    tx, ty, tw, th = x + w * 0.62, y + h * 0.05, 26 * S, h * 0.50
    d.rounded_rectangle([tx, ty, tx + tw, ty + th], radius=13 * S,
                        fill=(255, 255, 255), outline=INK, width=3 * S)
    d.rounded_rectangle([tx + 5 * S, ty + th * 0.30, tx + tw - 5 * S,
                         ty + th - 5 * S], radius=6 * S, fill=RED)
    d.ellipse([tx - 7 * S, ty + th - 5 * S, tx + tw + 7 * S,
               ty + th + 7 * S], fill=RED, outline=INK, width=3 * S)
    for lab, frac in (("40°", 0.14), ("20°", 0.78)):
        ly = ty + th * frac
        d.line([(tx - 14 * S, ly), (tx - 4 * S, ly)], fill=INK,
               width=2 * S)
        lf = sans(12 * S, 700)
        d.text((tx - 17 * S - text_w(d, lab, lf), ly - 6 * S), lab,
               font=lf, fill=INK)


def art_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 24, 30))
    # descending candlesticks
    tops = [0.22, 0.30, 0.42, 0.50, 0.58]
    for i, t in enumerate(tops):
        cx = x + w * (0.12 + i * 0.19)
        d.rectangle([cx - 7 * S, y + h * t, cx + 7 * S, y + h * (t + 0.22)],
                    fill=RED)
        d.line([(cx, y + h * (t - 0.08)), (cx, y + h * (t + 0.30))],
               fill=(255, 120, 120), width=2 * S)
    d.line([(x + w * 0.08, y + h * 0.25), (x + w * 0.92, y + h * 0.72)],
           fill=(255, 200, 80), width=3 * S)
    for lab, lx in [("TAIEX -6.8%", 0.02), ("KOSPI -5.4%", 0.35),
                    ("NIKKEI -4.9%", 0.68)]:
        d.text((x + w * lx, y + h * 0.82), lab, font=sans(8.5 * S, 800),
               fill=(255, 255, 255))


def art_mercury(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 10, 20))
    for sx, sy, sr in [(0.12, 0.2, 2), (0.3, 0.12, 2), (0.55, 0.25, 2),
                       (0.8, 0.15, 3), (0.9, 0.45, 2), (0.2, 0.6, 2)]:
        d.ellipse([x + w * sx - sr * S, y + h * sy - sr * S,
                   x + w * sx + sr * S, y + h * sy + sr * S],
                  fill=(255, 255, 255))
    # dotted trajectory arc
    for i in range(24):
        t = i / 23
        px = x + w * (0.08 + 0.55 * t)
        py = y + h * (0.78 - 0.45 * math.sin(math.pi * t * 0.9))
        d.ellipse([px - 2 * S, py - 2 * S, px + 2 * S, py + 2 * S],
                  fill=(255, 220, 120))
    # Mercury with craters
    cx, cy, r = x + w * 0.72, y + h * 0.48, h * 0.34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(178, 152, 120))
    for gx, gy, gr in [(0.66, 0.40, 0.06), (0.76, 0.55, 0.08),
                       (0.68, 0.60, 0.05), (0.78, 0.38, 0.04)]:
        d.ellipse([x + w * gx - gr * h, y + h * gy - gr * h,
                   x + w * gx + gr * h, y + h * gy + gr * h],
                  fill=(140, 116, 88))
    # NOTE (R3 fix): no in-art text — "6BN MILES · 8 YEARS" used to sit on
    # the trajectory dots / Mercury edge and ran past the art bottom.
    # Headline + body below the card already carry 6bn miles / 8 years.


def art_anthropic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(14, 42, 28))
    tops = [0.58, 0.55, 0.52, 0.48, 0.44]
    for i, t in enumerate(tops):
        cx = x + w * (0.12 + i * 0.19)
        d.rectangle([cx - 7 * S, y + h * t, cx + 7 * S, y + h * (t + 0.14)],
                    fill=(60, 200, 110))
        d.line([(cx, y + h * (t - 0.06)), (cx, y + h * (t + 0.20))],
               fill=(140, 240, 170), width=2 * S)
    # NOTE (R3 fix): no in-art text — "$97.17" / "+17%" used to overlap the
    # candlesticks. Headline + body below the card already carry $97.17 / +17%.
    pass


def art_inflation(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 238, 228))
    d.text((x + w * 0.06, y + h * 0.08), "CORE 2.2%",
           font=sans(12 * S, 800), fill=INK)
    bx, bw = x + w * 0.55, w * 0.16
    for i, (lab, v, c) in enumerate([("2.1%", 0.55, GREY),
                                     ("2.3%", 0.72, RED)]):
        bh = h * v
        d.rectangle([bx + i * bw * 1.25, y + h - 8 * S - bh,
                     bx + i * bw * 1.25 + bw, y + h - 8 * S], fill=c)
        # NOTE (R3 fix): no in-bar labels — "2.1%" and "SEP" used to overlap
        # inside the shorter grey bar, and "2.3%"/"OCT" touched. Bars stay
        # pure graphics; headline + body below carry 2.3% / 2.1% / Oct.


def art_rates(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    for i, (lab, v) in enumerate([("1Y 3.00%", 0.62), ("5Y 3.50%", 0.78)]):
        bw = w * 0.34
        bx = x + w * (0.08 + i * 0.46)
        d.rectangle([bx, y + h * (0.90 - v), bx + bw, y + h * 0.90],
                    fill=TEAL if i == 0 else (30, 90, 80))
        d.text((bx + 4 * S, y + h * (0.90 - v) + 4 * S), lab,
               font=sans(10 * S, 800), fill=(255, 255, 255))


def art_euuk(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 238, 228))
    # EU flag
    ex, ey, ew, eh = x + w * 0.06, y + h * 0.14, w * 0.40, h * 0.62
    d.rectangle([ex, ey, ex + ew, ey + eh], fill=(0, 51, 153))
    for i in range(12):
        a = 2 * math.pi * i / 12 - math.pi / 2
        d.ellipse([ex + ew / 2 + ew * 0.30 * math.cos(a) - 3 * S,
                   ey + eh / 2 + eh * 0.30 * math.sin(a) - 3 * S,
                   ex + ew / 2 + ew * 0.30 * math.cos(a) + 3 * S,
                   ey + eh / 2 + eh * 0.30 * math.sin(a) + 3 * S],
                  fill=(255, 204, 0))
    # UK flag
    ux, uy, uw, uh = x + w * 0.54, y + h * 0.14, w * 0.40, h * 0.62
    d.rectangle([ux, uy, ux + uw, uy + uh], fill=(1, 33, 105))
    d.line([(ux, uy), (ux + uw, uy + uh)], fill=(255, 255, 255), width=8 * S)
    d.line([(ux + uw, uy), (ux, uy + uh)], fill=(255, 255, 255), width=8 * S)
    d.line([(ux + uw / 2, uy), (ux + uw / 2, uy + uh)], fill=(255, 255, 255),
           width=10 * S)
    d.line([(ux, uy + uh / 2), (ux + uw, uy + uh / 2)], fill=(255, 255, 255),
           width=10 * S)
    d.line([(ux + uw / 2, uy), (ux + uw / 2, uy + uh)], fill=(200, 16, 46),
           width=5 * S)
    d.line([(ux, uy + uh / 2), (ux + uw, uy + uh / 2)], fill=(200, 16, 46),
           width=5 * S)
    d.text((x + w * 0.30, y + h * 0.80), "RESET TALKS",
           font=sans(12 * S, 800), fill=INK)


def art_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(46, 125, 70))
    d.rectangle([x + w * 0.42, y, x + w * 0.58, y + h], fill=(232, 214, 170))
    # stumps
    for i in range(3):
        d.rectangle([x + w * (0.46 + i * 0.035), y + h * 0.14,
                     x + w * (0.475 + i * 0.035), y + h * 0.34],
                    fill=(255, 220, 120))
    # bat + ball trajectory
    d.line([(x + w * 0.20, y + h * 0.78), (x + w * 0.38, y + h * 0.45)],
           fill=(180, 120, 60), width=7 * S)
    d.line([(x + w * 0.38, y + h * 0.45), (x + w * 0.80, y + h * 0.18)],
           fill=(255, 255, 255), width=2 * S)
    d.ellipse([x + w * 0.78, y + h * 0.14, x + w * 0.84, y + h * 0.22],
              fill=RED, outline=(255, 255, 255), width=2 * S)
    # NOTE (R3 fix): no in-art text — "118" (60px in an 84px-tall art) ran
    # past the art bottom and across the bat line; "RECORD" clipped too.
    # Headline below the card already carries 118 / the record.


def art_bukele(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    # ballot box
    bx, by, bw, bh = x + w * 0.10, y + h * 0.30, w * 0.44, h * 0.52
    d.rectangle([bx, by, bx + bw, by + bh], fill=(31, 58, 95))
    d.rectangle([bx - 6 * S, by - 10 * S, bx + bw + 6 * S, by + 2 * S],
                fill=(22, 32, 61))
    d.rectangle([bx + bw * 0.35, by - h * 0.08, bx + bw * 0.65, by - h * 0.03],
                fill=(255, 255, 255))
    # ballot paper going in, with check
    d.polygon([(bx + bw * 0.55, by - h * 0.28), (bx + bw * 0.95, by - h * 0.24),
               (bx + bw * 0.88, by - h * 0.03), (bx + bw * 0.48, by - h * 0.07)],
              fill=(255, 255, 255), outline=INK)
    d.line([(bx + bw * 0.60, by - h * 0.18), (bx + bw * 0.68, by - h * 0.12),
            (bx + bw * 0.86, by - h * 0.21)], fill=GREEN, width=4 * S)
    # NOTE (R3 fix): no in-art text — "THIRD"/"TERM"/"2027" crowded the
    # ballot box and "2027" ran past the art bottom. Headline + body below
    # the card already carry third-term / Feb 2027.


def art_boat(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 52, 84))
    # waves
    for wy in (0.62, 0.74, 0.86):
        pts = []
        for i in range(25):
            t = i / 24
            pts.append((x + w * t,
                        y + h * wy + 6 * S * math.sin(t * 12)))
        d.line(pts, fill=(140, 190, 220), width=3 * S)
    # capsized hull
    d.pieslice([x + w * 0.30, y + h * 0.30, x + w * 0.72, y + h * 0.78],
               180, 360, fill=(150, 90, 50))
    d.rectangle([x + w * 0.30, y + h * 0.52, x + w * 0.72, y + h * 0.58],
                fill=(110, 64, 34))
    # NOTE (R3 fix): no in-art text — "4 DEAD" overlapped the hull, "YENNE
    # COAST · SENEGAL" sat on the waves. Headline + body below the card
    # already carry 4 dead / Yenne.


def art_strike(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(178, 34, 34))
    # protest placards on sticks
    for i, (px, ph) in enumerate([(0.12, 0.42), (0.38, 0.52), (0.64, 0.44)]):
        d.line([(x + w * (px + 0.10), y + h * (0.30 + ph)),
                (x + w * (px + 0.10), y + h * 0.88)], fill=(255, 255, 255),
               width=3 * S)
        d.rectangle([x + w * px, y + h * 0.28, x + w * (px + 0.24),
                     y + h * (0.28 + ph)], fill=(255, 255, 255),
                    outline=INK, width=2 * S)
        # "!" centred inside its placard (R3 fix: the old 20*S "!" was taller
        # than the shortest placard, so its dot fell below the placard edge)
        ef = sans(12 * S, 800)
        d.text((x + w * (px + 0.12) - text_w(d, "!", ef) / 2,
                y + h * (0.30 + ph * 0.22)), "!",
               font=ef, fill=RED)
    # NOTE (R3 fix): no in-art text — "100 SQUARES" overlapped the placards.
    # Headline + body below the card already carry ~100 squares.


ART = {"akvan": art_akvan, "kyiv": art_kyiv, "cop31": art_cop31,
       "markets": art_markets, "mercury": art_mercury,
       "anthropic": art_anthropic, "inflation": art_inflation,
       "rates": art_rates, "euuk": art_euuk, "cricket": art_cricket,
       "bukele": art_bukele, "boat": art_boat, "strike": art_strike}


# ---------------------------------------------------------------- map
def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.text((x + 14 * S, y + 8 * S), "WHERE IT HAPPENED",
           font=sans(15 * S, 800), fill=(255, 255, 255))
    d.text((x + w - 14 * S - text_w(d, "pins 1–13 · dots 14–40",
           sans(11 * S, 600)), y + 10 * S), "pins 1–13 · dots 14–40",
           font=sans(11 * S, 600), fill=(170, 190, 210))

    mx, my, mw, mh = x + 10 * S, y + 34 * S, w - 20 * S, h - 44 * S
    lat0, lat1 = 84.0, -58.0

    def proj(lon, lat):
        return (mx + (lon + 180.0) / 360.0 * mw,
                my + (lat0 - lat) / (lat0 - lat1) * mh)

    # faint graticule
    for lon in range(-150, 181, 30):
        px, _ = proj(lon, 0)
        d.line([(px, my), (px, my + mh)], fill=(30, 48, 72), width=1 * S)
    for lat in (-30, 0, 30, 60):
        _, py = proj(0, lat)
        d.line([(mx, py), (mx + mw, py)], fill=(30, 48, 72), width=1 * S)
    # solid beige continents
    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND)
    # equator label
    _, eqy = proj(0, 0)
    d.text((mx + 4 * S, eqy + 2 * S), "EQUATOR", font=sans(9 * S, 700),
           fill=(150, 170, 195))
    # dots 14-40 first (under pins)
    for lat, lon in DOTS:
        px, py = proj(lon, lat)
        d.ellipse([px - 4 * S, py - 4 * S, px + 4 * S, py + 4 * S],
                  fill=(247, 241, 226), outline=NAVY, width=1 * S)
    # numbered red pins 1-13
    for i, (lat, lon) in enumerate(PINS, 1):
        px, py = proj(lon, lat)
        r = 11 * S
        d.ellipse([px - r, py - r, px + r, py + r], fill=RED,
                  outline=(255, 255, 255), width=2 * S)
        t = str(i)
        f = sans(11 * S, 800)
        d.text((px - text_w(d, t, f) / 2, py - 8 * S), t, font=f,
               fill=(255, 255, 255))


# ---------------------------------------------------------------- layout
def badge(d, cx, cy, n, r=13 * S):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
              outline=(255, 255, 255), width=2 * S)
    t = str(n)
    f = sans(13 * S, 800)
    d.text((cx - text_w(d, t, f) / 2, cy - 9 * S), t, font=f,
           fill=(255, 255, 255))


def card_head(d, x, y, w, card):
    """Number badge + location + source line; returns y below header."""
    badge(d, x + 16 * S, y + 17 * S, card["n"])
    sf = sans(9 * S, 600)
    sw = text_w(d, card["src"], sf)
    lf = sans(10.5 * S, 800)
    loc = trunc(d, card["loc"], lf, w - 36 * S - sw - 10 * S)
    d.text((x + 36 * S, y + 8 * S), loc, font=lf, fill=RED)
    d.text((x + w - 8 * S - sw, y + 9 * S), card["src"], font=sf, fill=GREY)
    return y + 34 * S


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([6 * S, 6 * S, W - 6 * S, H - 6 * S], outline=INK, width=3 * S)

    # ---- header
    y = 18 * S
    d.text((M, y), KICK_L, font=sans(15 * S, 800), fill=RED)
    rf = sans(13 * S, 700)
    d.text((W - M - text_w(d, KICK_R, rf), y + 2 * S), KICK_R, font=rf,
           fill=GREY)
    y += 24 * S
    d.text((M, y), MASTHEAD, font=serif(56 * S, 900), fill=INK)
    y += 58 * S
    d.text((M, y), SUBLINE, font=serif_it(15 * S, 700), fill=RED_DK)
    y += 24 * S
    d.line([(M, y), (W - M, y)], fill=INK, width=5 * S)
    d.line([(M, y + 7 * S), (W - M, y + 7 * S)], fill=INK, width=2 * S)
    y += 12 * S

    # ---- KPI strip
    kpi_y = y
    cw = (W - 2 * M) / 6
    for i, (num, lab) in enumerate(KPIS):
        cx = M + i * cw
        d.text((cx + 8 * S, kpi_y), num, font=serif(26 * S, 900), fill=RED)
        draw_wrapped(d, lab, sans(11.5 * S, 600), cx + 8 * S,
                     kpi_y + 32 * S, cw - 16 * S, INK2, lh=12.5 * S,
                     max_lines=2)
        if i:
            d.line([(cx, kpi_y + 4 * S), (cx, kpi_y + 56 * S)], fill=GREY,
                   width=1 * S)
    y = kpi_y + 56 * S

    # ---- region bar
    total = sum(v for _, v, _ in REGIONS)
    rx = M
    for name, v, col in REGIONS:
        seg = (W - 2 * M) * v / total
        d.rectangle([rx, y, rx + seg - 2 * S, y + 12 * S], fill=col)
        rx += seg
    y += 12 * S
    rf2 = sans(12 * S, 800)
    labels = "  ·  ".join(f"{n} {v}" for n, v, _ in REGIONS)
    d.text((M, y), labels, font=rf2, fill=INK)
    y += 16 * S

    # ---- leads (3 cards)
    lead_y, lead_h = y, 194 * S
    lw = (W - 2 * M - 2 * 8 * S) / 3
    for i, card in enumerate(LEADS):
        x = M + i * (lw + 8 * S)
        d.rectangle([x, lead_y, x + lw, lead_y + lead_h], fill=(255, 255, 255),
                    outline=INK, width=2 * S)
        hy = card_head(d, x, lead_y, lw, card)
        ART[card["art"]](d, x + 6 * S, hy, lw - 12 * S, 62 * S)
        ty = hy + 70 * S
        ty = draw_wrapped(d, card["head"], serif(19 * S, 900), x + 8 * S,
                          ty, lw - 16 * S, INK, lh=21 * S, max_lines=2)
        draw_wrapped(d, card["body"], sans(12 * S, 500), x + 8 * S,
                     ty + 4 * S, lw - 16 * S, INK2, lh=13.5 * S, max_lines=3)
        if card["n"] == 3:
            # $120BN FINANCE GAP badge over the COP31 art
            bf = sans(12 * S, 800)
            label = "$120BN FINANCE GAP"
            bw = text_w(d, label, bf) + 18 * S
            bx = x + lw - 6 * S - bw
            by = hy + 62 * S - 24 * S
            d.rectangle([bx, by, bx + bw, by + 20 * S], fill=RED)
            d.text((bx + 9 * S, by + 3 * S), label, font=bf,
                   fill=(255, 255, 255))
    y = lead_y + lead_h + 6 * S

    # ---- features (2 rows x 5)
    feat_h = 146 * S
    fw = (W - 2 * M - 4 * 7 * S) / 5
    for row in range(2):
        for col in range(5):
            card = FEATURES[row * 5 + col]
            x = M + col * (fw + 7 * S)
            fy = y + row * (feat_h + 7 * S)
            d.rectangle([x, fy, x + fw, fy + feat_h], fill=(255, 255, 255),
                        outline=INK, width=2 * S)
            hy = card_head(d, x, fy, fw, card)
            ART[card["art"]](d, x + 6 * S, hy, fw - 12 * S, 42 * S)
            ty = hy + 48 * S
            ty = draw_wrapped(d, card["head"], serif(15 * S, 900),
                              x + 7 * S, ty, fw - 14 * S, INK, lh=17 * S,
                              max_lines=2)
            draw_wrapped(d, card["body"], sans(11 * S, 500), x + 7 * S,
                         ty + 3 * S, fw - 14 * S, INK2, lh=13 * S,
                         max_lines=2)
    y = y + 2 * feat_h + 6 * S + 4 * S

    # ---- bottom: map + briefs (2 numbered columns)
    bot_y, bot_h = y, 202 * S
    map_w = 340 * S
    draw_map(d, M, bot_y, map_w, bot_h)
    bx = M + map_w + 10 * S
    bw = W - M - bx
    d.text((bx, bot_y + 2 * S),
           "ALSO ON FRIDAY 20 NOVEMBER — 27 MORE STORIES",
           font=sans(14 * S, 800), fill=INK)
    d.line([(bx, bot_y + 26 * S), (W - M, bot_y + 26 * S)], fill=RED,
           width=3 * S)
    col_w = (bw - 12 * S) / 2
    by = bot_y + 30 * S
    lh = 12 * S
    bf = sans(11 * S, 500)
    pf = sans(11 * S, 800)
    for ci in range(2):
        cx = bx + ci * (col_w + 12 * S)
        for ri in range(14):
            idx = ci * 14 + ri
            if idx >= len(BRIEFS):
                break
            place, text = BRIEFS[idx]
            yy = by + ri * lh
            n = str(14 + idx)
            nf = sans(11 * S, 800)
            d.text((cx, yy), n, font=nf, fill=RED)
            nx = cx + text_w(d, n, nf) + 5 * S
            line = f"{place}  {text}"
            d.text((nx, yy), trunc(d, line, bf, col_w - (nx - cx)),
                   font=bf, fill=INK)
    y = bot_y + bot_h + 8 * S

    # ---- DATE CHECK footer
    d.rectangle([M, y, W - M, y + 52 * S], outline=RED, width=2 * S)
    d.text((M + 8 * S, y + 4 * S), "DATE CHECK —",
           font=sans(12 * S, 800), fill=RED)
    draw_wrapped(
        d,
        "First reported Thu 19 Nov — not Friday's news: "
        + DATE_CHECK,
        sans(11 * S, 500), M + 8 * S, y + 24 * S, W - 2 * M - 16 * S,
        INK2, lh=13 * S, max_lines=2)
    y = y + 52 * S + 4 * S
    d.text((M, y),
           "Every story here happened, or was first reported, on Friday 20 November 2026, "
           "in at least one wire or news roundup. Claims are attributed, not stated as fact.",
           font=sans(10.5 * S, 500), fill=GREY)
    y += 12 * S
    d.text((M, y),
           "Sources: Reuters · AP · AFP · BBC · The Hindu · IMD · UN News · Al Jazeera · ICC · "
           "EU Council · PBOC · PRNewswire. Original vector drawings.",
           font=sans(10.5 * S, 500), fill=GREY)

    out = img.resize((1024, 1024), Image.LANCZOS)
    out.save(os.path.join(BASE, "entry.png"), optimize=True)
    print("wrote entry.png 1024x1024")


if __name__ == "__main__":
    render()
