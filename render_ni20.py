#!/usr/bin/env python3
"""Render entry.png for make.fun news-image-20261120.

One page, Friday 20 November 2026: 40 stories, 7 regions.
Written from scratch in this session. Layout follows the winning
news-image-20261118 R5 / news-image-20261119 R2 formula (3 leads +
10 medium cards with flat Pillow illustrations, dotted world map
with numbered pins, brief list, day-in-numbers strip, DATE CHECK
footer, sources line) — with all text, decks and illustrations
written fresh for 20 November.

Every story was verified against wire coverage or the day's news
roundups of 20 Nov 2026 (WIB) before it went on the page; see
briefs.md for the story list and sources. Items first reported
Thu 19 Nov are named in the DATE CHECK footer, not as stories.

Deterministic: no network, no clock, no randomness. The dotted map
is drawn from a hand-written land mask (ellipses over lon/lat),
not from any downloaded file.

    python3 render_ni20.py      # writes entry.png next to this file
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 1024, 1024

# ---- palette: warm paper, muted newsroom inks ----
PAPER = (246, 241, 231)
CARD = (255, 255, 255)
INK = (26, 36, 48)
NAVY = (30, 41, 66)
NAVY2 = (44, 60, 96)
RUST = (178, 82, 42)
TEAL = (74, 120, 118)
TEAL_DK = (36, 72, 74)
SAND = (229, 218, 196)
SAND_DK = (203, 187, 148)
GOLD = (198, 152, 58)
GREY = (104, 112, 126)
LINE = (214, 205, 185)
DOT = (120, 138, 156)
MAP_BG = (239, 234, 221)
RED = (178, 44, 36)
GREEN = (62, 110, 72)

DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DJB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DSB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
DS = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def wrap(d, text, font, max_w):
    """Wrap text to lines that fit max_w pixels. Returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(d, text, font, max_w, max_lines=None):
    """Wrap, then truncate with an ellipsis if it runs past max_lines."""
    lines = wrap(d, text, font, max_w)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        # trim the last line so the ellipsis fits
        while lines and d.textlength(lines[-1] + "…", font=font) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + "…"
    return lines


# ---- region colours (used for tags, map dots, region bar) ----
REGION_COLOR = {
    "Europe": (44, 60, 96),
    "Asia": (178, 82, 42),
    "Middle East": (122, 74, 28),
    "Africa": (62, 110, 72),
    "Americas": (96, 62, 110),
    "Oceania": (36, 110, 122),
    "World": (90, 90, 90),
}

# ---- the 13 cards: (num, kicker, headline, deck, region, source, art, lon, lat) ----
CARDS = [
    (1, "AKVAN · ODISHA", "300,000 flee the storm",
     "Severe Cyclone Akvan crosses the Andhra–Odisha coast near "
     "Gopalpur by noon, 90–100 kmph winds; 300,000+ evacuated, "
     "423 rescue teams out.",
     "Asia", "India Today / Hindu", "cyclone", 85.2, 19.5),
    (2, "KYIV · UKRAINE", "Ballistic night over Kyiv",
     "Russia fires ballistic missiles at Kyiv overnight; fires "
     "burn in several districts, debris hits a building in "
     "Obolonskyi.",
     "Europe", "Reuters", "kyiv", 30.5, 50.45),
    (3, "RIYADH · GULF", "Missiles hit the PIF tower",
     "Houthis claim strikes on four Saudi targets; a missile "
     "damages Riyadh's tallest tower, home of the sovereign "
     "wealth fund. No casualties.",
     "Middle East", "SPA / Al Jazeera", "riyadh", 46.7, 24.7),
    (4, "GENOA · DRONES", "Airport shut by drones",
     "Genoa airport halts flights for four hours over drones.",
     "Europe", "Daily Baku", "genoa", 8.9, 44.4),
    (5, "EUROPE · TALKS", "Europe ready to talk",
     "Europe ready to talk; the E3 weigh a Moscow meeting.",
     "Europe", "BBC", "talks", 4.35, 50.85),
    (6, "SPACE · JAPAN", "Hayabusa2 gives up the landing",
     "Engine trouble ends Hayabusa2's asteroid landing plan.",
     "Asia", "Space.com", "hayabusa", 139.4, 35.5),
    (7, "HORMUZ · OIL", "Tankers hit mines, on fire",
     "Two tankers hit mines east of Hormuz; WTI holds $82.50.",
     "Middle East", "FXStreet", "hormuz", 56.3, 26.5),
    (8, "LEBANON · STRIKES", "40 sites hit in a day",
     "40 Hezbollah sites hit; a woman killed, children hurt.",
     "Middle East", "AJ", "lebanon", 35.5, 33.9),
    (9, "WALL ST · MARKETS", "Dow −1,101 as AI bust bites",
     "Dow −2.19%, S&P's sixth loss in a row; Anthropic +17%.",
     "Americas", "WSJ", "wallst", -74.0, 40.7),
    (10, "GTA 6 · SALES", "Bigger than a blockbuster",
     "GTA 6 sales pass The Odyssey's $1.80bn global box office.",
     "World", "Mezha", "gta6", -3.2, 55.95),
    (11, "TAIPEI · MARKETS", "Five moves to steady stocks",
     "Taiwan acts as stocks fall 5,248 points in three days.",
     "Asia", "FSC / CNA", "taiwan", 121.6, 25.0),
    (12, "AFRICA · CHILDREN", "260 million childhoods at war",
     "260 million children live in African conflict zones.",
     "Africa", "STC", "children", 22.0, 4.0),
    (13, "WELLINGTON · VOTE", "New Zealand votes tomorrow",
     "Kiwis vote Saturday; Australian ballots could decide it.",
     "Oceania", "AP", "nzvote", 174.8, -41.3),
]

# ---- briefs 14-40: (num, headline, region, lon, lat) ----
BRIEFS = [
    (14, "Fire in 18-storey French flats: 1 dead, 15 hurt", "Europe", 2.35, 48.85),
    (15, "Taiwan council hopeful out on NT$500k bail", "Asia", 121.6, 25.0),
    (16, "Taiwan widens spouse share in inheritance law", "Asia", 121.6, 25.0),
    (17, "Vietjet expands routes to the Philippines", "Asia", 106.7, 10.8),
    (18, "Nikkei −4.54% as Asian stocks slide Friday", "Asia", 139.7, 35.7),
    (19, "Lee hails Korea's $1tn export milestone", "Asia", 127.0, 37.5),
    (20, "WTI above $82.50 on Hormuz disruption", "Middle East", -95.4, 29.8),
    (21, "MBS phoned Trump twice over the Houthis", "Middle East", 46.7, 24.7),
    (22, "Vance: US in direct talks with the Houthis", "Middle East", -77.0, 38.9),
    (23, "Houthis seize Hanish islands and Mocha port", "Middle East", 43.3, 12.7),
    (24, "East-West pipeline shut after drone strike", "Middle East", 38.1, 24.1),
    (25, "Mob kills Osun accident survivor in Nigeria", "Africa", 4.6, 7.8),
    (26, "SACP pushes back on ANC entitlement", "Africa", 28.0, -26.2),
    (27, "More climate cash for Africa? Europe says no", "Africa", 30.7, 36.9),
    (28, "Burundi: Banyamulenge caught in arrest wave", "Africa", 29.4, -3.4),
    (29, "CAR: Sakaï 2 power plan sparks mockery", "Africa", 18.6, 4.4),
    (30, "Eswatini youth 'loses kidney in job scam'", "Africa", 31.4, -26.3),
    (31, "Senegal marks Armed Forces Day, Faye rallies region", "Africa", -17.4, 14.7),
    (32, "Trump flies home, White House briefing today", "Americas", -77.0, 38.9),
    (33, "Trump pardons baseball's Pete Rose, posthumously", "Americas", -84.5, 39.1),
    (34, "Bitcoin $62,150 as crypto slides with stocks", "Americas", -74.0, 40.7),
    (35, "LG names new boss for Australia and NZ", "Oceania", 151.2, -33.9),
    (36, "Passport-free travel promised for Kiwis in Australia", "Oceania", 174.8, -41.3),
    (37, "L7 take The Last Hurrah Tour to Australia, NZ", "Oceania", 151.2, -33.9),
    (38, "Gale warning for Suwarrow, storm alert Pukapuka", "Oceania", -159.8, -21.2),
    (39, "IEA: data-centre power use may double by 2030", "World", 2.35, 48.85),
    (40, "Islam to be world's largest faith by 2035: study", "World", 106.8, -6.2),
]

# ---- day in numbers: (big, label) ----
NUMBERS = [
    ("300k+", "evacuated ahead of Akvan"),
    ("4", "ballistic missiles hit Kyiv"),
    ("$82.50", "WTI crude, Friday"),
    ("−1,101", "Dow points, Thursday"),
    ("260M", "children in conflict zones"),
    ("90–100", "kmph, Akvan landfall winds"),
]

# ---- items deliberately left out: first reported Thursday 19 Nov ----
DATE_CHECK = (
    "DATE CHECK — left out on purpose, first reported Thu 19 Nov: ICJ rules Myanmar "
    "guilty of genocide · APEC trilateral in Shenzhen · Korea's $1tn export milestone · "
    "Voyager 1's light-day confirmed · COP31 draft drops fossil fuels · US Senate rejects "
    "Iran war-powers 51–48 · Trump: 'see what happens' on Iran after Jan 1 · Modi at FICCI centenary."
)

SOURCES = (
    "Sources: Reuters · BBC · Al Jazeera · AP · WSJ · UN News · India Today · The Hindu · "
    "AfricaFrontPage · FXStreet. Every story verified against wire coverage of 20 Nov 2026."
)

# ---- land mask: (lon centre, lat centre, rx, ry) ellipses, hand-drawn ----
LAND = [
    (-110, 62, 55, 12), (-85, 55, 25, 10), (-98, 39, 28, 9), (-102, 23, 12, 7),
    (-88, 13, 8, 4), (-42, 74, 12, 8),
    (-60, 0, 18, 10), (-45, -12, 14, 12), (-68, -25, 8, 18),
    (5, 48, 14, 9), (15, 63, 10, 8), (-2, 54, 3, 5), (28, 52, 14, 8),
    (-4, 40, 6, 4), (15, 40, 6, 4),
    (5, 22, 22, 8), (-8, 10, 10, 7), (20, 0, 12, 10), (35, -2, 10, 12),
    (25, -22, 12, 10), (47, -19, 3, 6),
    (45, 24, 10, 9), (45, 35, 14, 6),
    (70, 62, 35, 12), (135, 65, 40, 12), (65, 45, 12, 8), (78, 21, 10, 12),
    (101, 15, 7, 9), (105, 35, 18, 12), (115, -3, 18, 5), (138, 38, 4, 8),
    (128, 38, 2, 4), (142, -5, 8, 4),
    (122, -25, 12, 10), (145, -28, 10, 10), (172, -41, 3, 6),
]


def is_land(lon, lat):
    for cx, cy, rx, ry in LAND:
        dx = (lon - cx) / rx
        dy = (lat - cy) / ry
        if dx * dx + dy * dy <= 1.0:
            return True
    return False


# ---- flat illustrations, one per card (Pillow primitives only) ----
def art_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(38, 66, 82))
    # spiral bands
    for r, col in [(26, (120, 160, 180)), (18, (160, 190, 205)), (10, (220, 230, 235))]:
        d.arc([x + w // 2 - r, y + h // 2 - r - 4, x + w // 2 + r, y + h // 2 + r - 4],
              200, 120, fill=col, width=4)
    d.ellipse([x + w // 2 - 4, y + h // 2 - 8, x + w // 2 + 4, y + h // 2],
              fill=(240, 200, 90))
    # rain slashes
    for i in range(8):
        rx = x + 6 + i * ((w - 12) // 8)
        d.line([rx, y + h - 22, rx - 4, y + h - 10], fill=(160, 190, 205), width=2)
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(24, 44, 56))


def art_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 30, 52))
    # missile trails arcing down
    for tx, col in [(18, (240, 160, 40)), (44, (240, 200, 90)), (70, (240, 160, 40))]:
        d.arc([x + tx - 14, y + 2, x + tx + 14, y + 34], 180, 360, fill=col, width=2)
        d.ellipse([x + tx - 2, y + 30, x + tx + 2, y + 34], fill=col)
    # city silhouette + one fire
    for i, bh in enumerate([20, 30, 16, 26]):
        bx = x + 8 + i * ((w - 16) // 4)
        bw = (w - 16) // 4 - 3
        d.rectangle([bx, y + h - 12 - bh, bx + bw, y + h - 12], fill=(70, 82, 110))
    d.polygon([(x + 16, y + h - 30), (x + 12, y + h - 18), (x + 20, y + h - 18)],
              fill=(240, 140, 40))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(16, 20, 36))


def art_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 214, 170))
    # PIF tower: tall slab with a burst at the crown
    tx = x + w // 2 - 12
    d.rectangle([tx, y + 18, tx + 24, y + h - 12], fill=(44, 60, 96))
    for i in range(6):
        wy = y + 24 + i * 9
        d.rectangle([tx + 4, wy, tx + 20, wy + 4], fill=(120, 140, 170))
    bx, by = x + w // 2, y + 14
    for a in range(0, 360, 45):
        ex = bx + 12 * math.cos(math.radians(a))
        ey = by + 12 * math.sin(math.radians(a))
        d.line([bx, by, ex, ey], fill=(240, 160, 40), width=2)
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(240, 160, 40))
    # low city blocks
    d.rectangle([x + 6, y + h - 26, x + 30, y + h - 12], fill=(120, 110, 90))
    d.rectangle([x + w - 30, y + h - 22, x + w - 6, y + h - 12], fill=(120, 110, 90))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(203, 187, 148))


def art_genoa(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 232))
    # runway + tower
    d.rectangle([x, y + h - 20, x + w, y + h - 12], fill=(60, 60, 60))
    for i in range(5):
        dx = x + 10 + i * ((w - 20) // 5)
        d.rectangle([dx, y + h - 17, dx + 8, y + h - 15], fill=(255, 255, 255))
    d.rectangle([x + w - 22, y + 10, x + w - 14, y + h - 20], fill=(90, 90, 90))
    d.rectangle([x + w - 26, y + 6, x + w - 10, y + 14], fill=(44, 60, 96))
    # three drones with lights, one circled (detected)
    for dx, dy in [(20, 14), (40, 22), (60, 12)]:
        d.ellipse([x + dx - 3, y + dy - 3, x + dx + 3, y + dy + 3], fill=(40, 40, 40))
        d.ellipse([x + dx - 1, y + dy - 1, x + dx + 1, y + dy + 1], fill=(240, 60, 40))
    d.ellipse([x + 52, y + 4, x + 68, y + 20], outline=(178, 44, 36), width=2)


def art_talks(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    # three flags on poles above a round table
    for i, col in enumerate([(0, 56, 147), (206, 17, 38), (0, 60, 120)]):
        px = x + 14 + i * 26
        d.line([px, y + 8, px, y + 32], fill=(120, 120, 120), width=2)
        d.rectangle([px, y + 8, px + 20, y + 16], fill=col)
        if i == 1:
            d.rectangle([px, y + 8, px + 20, y + 12], fill=(255, 255, 255))
            d.rectangle([px, y + 12, px + 20, y + 16], fill=(206, 17, 38))
    d.ellipse([x + 10, y + h - 26, x + w - 10, y + h - 8], fill=(44, 60, 96))
    d.rectangle([x + w // 2 - 2, y + h - 8, x + w // 2 + 2, y + h], fill=(44, 60, 96))


def art_hayabusa(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 22, 40))
    # stars
    for sx, sy in [(10, 8), (30, 18), (52, 6), (70, 22), (84, 10)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=(255, 255, 255))
    # asteroid (grey potato)
    ax, ay = x + w - 34, y + h - 30
    d.ellipse([ax - 16, ay - 10, ax + 16, ay + 10], fill=(140, 130, 115))
    d.ellipse([ax - 8, ay - 5, ax - 2, ay + 1], fill=(110, 100, 88))
    d.ellipse([ax + 4, ay + 2, ax + 10, ay + 8], fill=(110, 100, 88))
    # probe body + panels, drifting away (dashed path)
    px, py = x + 22, y + 16
    d.line([px + 8, py + 6, ax - 14, ay - 8], fill=(120, 140, 170), width=1)
    d.rectangle([px, py, px + 16, py + 12], fill=(198, 152, 58))
    d.rectangle([px - 12, py + 3, px, py + 9], fill=(74, 120, 180))
    d.rectangle([px + 16, py + 3, px + 28, py + 9], fill=(74, 120, 180))


def art_hormuz(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 232))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(74, 120, 138))
    for i in range(4):
        yy = y + h - 18 + i * 4
        d.arc([x + 4, yy - 3, x + w - 4, yy + 5], 200, 340, fill=(150, 180, 188))
    # tanker hull + fire burst amidships
    d.rectangle([x + 10, y + h - 38, x + w - 10, y + h - 22], fill=(52, 62, 78))
    d.rectangle([x + w - 26, y + h - 52, x + w - 14, y + h - 38], fill=(240, 240, 240))
    bx, by = x + w // 2, y + h - 44
    for a in range(0, 360, 40):
        ex = bx + 13 * math.cos(math.radians(a))
        ey = by + 13 * math.sin(math.radians(a))
        d.line([bx, by, ex, ey], fill=(240, 140, 40), width=2)
    d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(240, 160, 40))
    # naval mine, spiked, bottom right
    mx, my = x + w - 16, y + h - 12
    d.ellipse([mx - 5, my - 5, mx + 5, my + 5], fill=(40, 40, 40))
    for a in range(0, 360, 45):
        ex = mx + 8 * math.cos(math.radians(a))
        ey = my + 8 * math.sin(math.radians(a))
        d.line([mx, my, ex, ey], fill=(40, 40, 40), width=1)


def art_lebanon(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 214, 186))
    # mountains + cedar + strike burst
    d.polygon([(x, y + h), (x + w * 0.3, y + 14), (x + w * 0.6, y + h)],
              fill=(120, 140, 120))
    d.polygon([(x + w * 0.4, y + h), (x + w * 0.7, y + 22), (x + w, y + h)],
              fill=(96, 118, 100))
    cx, cy = x + w // 2, y + h - 30
    d.rectangle([cx - 2, cy, cx + 2, cy + 12], fill=(90, 60, 40))
    d.polygon([(cx, cy - 16), (cx - 10, cy - 2), (cx + 10, cy - 2)], fill=(62, 110, 72))
    d.polygon([(cx, cy - 24), (cx - 7, cy - 12), (cx + 7, cy - 12)], fill=(62, 110, 72))
    bx, by = x + w - 18, y + 16
    for a in range(0, 360, 45):
        ex = bx + 9 * math.cos(math.radians(a))
        ey = by + 9 * math.sin(math.radians(a))
        d.line([bx, by, ex, ey], fill=(178, 44, 36), width=2)
    d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(178, 44, 36))


def art_wallst(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 41, 66))
    # grid
    for i in range(1, 4):
        gy = y + i * (h // 4)
        d.line([x + 6, gy, x + w - 6, gy], fill=(58, 76, 116), width=1)
    # falling chart, red, with a small green bounce at the open
    pts = [(x + 6, y + 12), (x + w * 0.25, y + 16), (x + w * 0.45, y + 30),
           (x + w * 0.65, y + 26), (x + w * 0.85, y + h - 16), (x + w - 6, y + h - 12)]
    for i in range(len(pts) - 1):
        col = (62, 180, 120) if i == 0 else (220, 70, 50)
        d.line([pts[i], pts[i + 1]], fill=col, width=3)
    d.text((x + w - 8, y + 6), "−2.19%", font=F(DJB, 11), fill=(220, 70, 50),
           anchor="ra")


def art_gta6(d, x, y, w, h):
    # dusk skyline + palm + sun
    d.rectangle([x, y, x + w, y + h], fill=(238, 170, 110))
    d.ellipse([x + w - 30, y + 8, x + w - 10, y + 28], fill=(250, 220, 140))
    for i, bh in enumerate([26, 40, 22, 34, 30]):
        bx = x + 6 + i * ((w - 12) // 5)
        bw = (w - 12) // 5 - 3
        d.rectangle([bx, y + h - 12 - bh, bx + bw, y + h - 12], fill=(60, 40, 70))
        for wy in range(0, bh - 6, 8):
            d.rectangle([bx + 2, y + h - 12 - bh + 3 + wy, bx + 5,
                         y + h - 9 - bh + wy], fill=(250, 220, 140))
    # palm silhouette, right
    px, py = x + w - 14, y + h - 12
    d.line([px, py, px + 2, py - 26], fill=(40, 30, 50), width=3)
    for a in [-60, -30, 0, 30, 60]:
        ex = px + 12 * math.cos(math.radians(a - 90))
        ey = py - 26 + 7 * math.sin(math.radians(a - 90))
        d.line([px + 2, py - 26, ex, ey], fill=(40, 30, 50), width=2)
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(40, 30, 50))


def art_taiwan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 226))
    # falling bars, then a shield with a check (the five measures)
    for i, bh in enumerate([34, 28, 22, 16]):
        bx = x + 10 + i * 16
        d.rectangle([bx, y + h - 14 - bh, bx + 11, y + h - 14], fill=(178, 82, 42))
    # shield
    sx, sy = x + w - 34, y + 12
    d.polygon([(sx, sy), (sx + 22, sy), (sx + 22, sy + 14), (sx + 11, sy + 26),
               (sx, sy + 14)], fill=(44, 60, 96))
    d.line([sx + 5, sy + 13, sx + 9, sy + 17], fill=(255, 255, 255), width=2)
    d.line([sx + 9, sy + 17, sx + 18, sy + 7], fill=(255, 255, 255), width=2)
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(74, 120, 118))


def art_children(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 222, 188))
    d.ellipse([x + 8, y + 6, x + 26, y + 24], fill=(240, 200, 90))
    # three small figures holding hands
    for i, col in enumerate([(178, 82, 42), (62, 110, 72), (44, 60, 96)]):
        fx = x + 22 + i * 22
        fy = y + h - 34
        d.ellipse([fx - 5, fy - 12, fx + 5, fy - 2], fill=col)
        d.rectangle([fx - 4, fy - 2, fx + 4, fy + 12], fill=col)
        d.line([fx - 9, fy + 2, fx + 9, fy + 2], fill=col, width=2)
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(203, 187, 148))


def art_nzvote(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 226))
    # ballot box + big tick + two small flags
    bx, by = x + w // 2 - 22, y + h - 40
    d.rectangle([bx, by, bx + 44, by + 28], fill=(44, 60, 96))
    d.rectangle([bx - 4, by - 6, bx + 48, by], fill=(30, 41, 66))
    d.rectangle([bx + 18, by - 6, bx + 26, by], fill=(232, 226, 210))
    d.line([bx + 6, by + 14, bx + 16, by + 24], fill=(255, 255, 255), width=3)
    d.line([bx + 16, by + 24, bx + 38, by + 2], fill=(255, 255, 255), width=3)
    for i, col in enumerate([(0, 56, 147), (206, 17, 38)]):
        px = x + 12 + i * 16
        d.line([px, y + 8, px, y + 26], fill=(120, 120, 120), width=2)
        d.rectangle([px, y + 8, px + 13, y + 15], fill=col)


ART = {
    "cyclone": art_cyclone, "kyiv": art_kyiv, "riyadh": art_riyadh,
    "genoa": art_genoa, "talks": art_talks, "hayabusa": art_hayabusa,
    "hormuz": art_hormuz, "lebanon": art_lebanon, "wallst": art_wallst,
    "gta6": art_gta6, "taiwan": art_taiwan, "children": art_children,
    "nzvote": art_nzvote,
}


# ---- layout ----
MX = 24                      # side margin
CW = W - 2 * MX              # content width = 976


def region_counts():
    counts = {}
    for c in CARDS:
        counts[c[4]] = counts.get(c[4], 0) + 1
    for b in BRIEFS:
        counts[b[2]] = counts.get(b[2], 0) + 1
    return counts


def draw_header(d):
    d.text((MX, 14), "THE WORLD IN ONE PAGE", font=F(DSB, 34), fill=INK)
    d.text((W - MX, 26), "FRIDAY 20 NOVEMBER 2026", font=F(DJB, 15),
           fill=RUST, anchor="ra")
    d.text((MX, 54), "40 STORIES · 7 REGIONS · ONE PAGE", font=F(DJB, 13), fill=NAVY)
    d.text((W - MX, 54), "A careful picture editor's summary of the day",
           font=F(DJ, 11), fill=GREY, anchor="ra")
    d.line([MX, 74, W - MX, 74], fill=INK, width=2)


def draw_region_bar(d, y):
    counts = region_counts()
    order = ["Europe", "Asia", "Middle East", "Africa", "Americas", "Oceania", "World"]
    total = sum(counts.values())
    x = MX
    for r in order:
        n = counts.get(r, 0)
        w = CW * n / total
        d.rectangle([x, y, x + w - 2, y + 12], fill=REGION_COLOR[r])
        x += w
    # one centred label line under the bar — no overlap on narrow segments
    parts = ["%s %d" % (r.upper(), counts.get(r, 0)) for r in order]
    label = "   ·   ".join(parts)
    d.text((MX + CW // 2, y + 22), label, font=F(DJB, 10), fill=INK, anchor="ma")
    return y + 34


def draw_card(d, card, x, y, w, h, lead=False):
    num, kicker, headline, deck, region, source, art, lon, lat = card
    col = REGION_COLOR[region]
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    d.rectangle([x, y, x + w, y + 4], fill=col)
    # number badge
    d.ellipse([x + 8, y + 10, x + 28, y + 30], fill=RED)
    d.text((x + 18, y + 20), str(num), font=F(DJB, 12), fill=(255, 255, 255),
           anchor="mm")
    d.text((x + 34, y + 12), kicker, font=F(DJB, 9), fill=col)
    d.text((x + w - 8, y + 12), source.upper(), font=F(DJB, 8), fill=GREY,
           anchor="ra")
    if lead:
        art_h = 72
        ART[art](d, x + 8, y + 32, w - 16, art_h)
        ty = y + 32 + art_h + 6
        hl = F(DJB, 16)
        dk = F(DJ, 11)
        max_lines_h, max_lines_d = 2, 3
        step_h, step_d = 18, 14
    else:
        art_h = 46
        ART[art](d, x + 8, y + 30, w - 16, art_h)
        ty = y + 30 + art_h + 4
        hl = F(DJB, 12)
        dk = F(DJ, 10)
        max_lines_h, max_lines_d = 2, 2
        step_h, step_d = 13, 12
    for i, line in enumerate(fit_text(d, headline, hl, w - 16, max_lines_h)):
        d.text((x + 8, ty + i * step_h), line, font=hl, fill=INK)
    dy = ty + len(fit_text(d, headline, hl, w - 16, max_lines_h)) * step_h + 2
    for i, line in enumerate(fit_text(d, deck, dk, w - 16, max_lines_d)):
        d.text((x + 8, dy + i * step_d), line, font=dk, fill=(60, 68, 80))


def lonlat_to_xy(lon, lat, mx, my, mw, mh):
    # crop the poles: lat 85..-60 uses the height far better than -90..90
    px = mx + (lon + 180.0) / 360.0 * mw
    py = my + (85.0 - lat) / 145.0 * mh
    return px, py


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=MAP_BG, outline=LINE, width=1)
    d.text((x + 10, y + 8), "WHERE IT HAPPENED", font=F(DJB, 11), fill=NAVY)
    d.text((x + w - 10, y + 8), "pins 1–13 · dots 14–40", font=F(DJ, 9),
           fill=GREY, anchor="ra")
    mx, my, mw, mh = x + 8, y + 26, w - 16, h - 34
    step = 4
    px = mx
    while px < mx + mw:
        py = my
        while py < my + mh:
            lon = (px - mx) / mw * 360.0 - 180.0
            lat = 85.0 - (py - my) / mh * 145.0
            if is_land(lon, lat):
                d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=DOT)
            py += step
        px += step
    # brief dots first (under the pins)
    for num, headline, region, lon, lat in BRIEFS:
        bx, by = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        d.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=REGION_COLOR[region])
    # numbered pins for the 13 cards
    for num, kicker, headline, deck, region, source, art, lon, lat in CARDS:
        bx, by = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        if num == 9:  # nudge the Wall Street pin clear of the Bitcoin dot
            bx += 14
            by -= 10
        d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=RED,
                  outline=(255, 255, 255), width=2)
        d.text((bx, by), str(num), font=F(DJB, 9), fill=(255, 255, 255),
               anchor="mm")


def draw_numbers(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY, outline=LINE, width=1)
    d.text((x + 10, y + 8), "THE DAY IN NUMBERS", font=F(DJB, 11), fill=(240, 200, 90))
    cw = (w - 20) // 3
    ch = (h - 30) // 2
    for i, (big, label) in enumerate(NUMBERS):
        cx = x + 10 + (i % 3) * cw
        cy = y + 30 + (i // 3) * ch
        d.text((cx, cy), big, font=F(DJB, 17), fill=(255, 255, 255))
        for j, line in enumerate(fit_text(d, label, F(DJ, 9), cw - 6, 2)):
            d.text((cx, cy + 22 + j * 11), line, font=F(DJ, 9), fill=(200, 210, 230))


def draw_briefs(d, y):
    d.text((MX, y), "THE REST OF THE DAY — 14–40", font=F(DJB, 11), fill=NAVY)
    d.line([MX, y + 16, W - MX, y + 16], fill=LINE, width=1)
    col_w = (CW - 2 * 16) // 3
    for i, (num, headline, region, lon, lat) in enumerate(BRIEFS):
        col = i // 9
        row = i % 9
        bx = MX + col * (col_w + 16)
        by = y + 22 + row * 17
        d.text((bx, by), "%d." % num, font=F(DJB, 10), fill=REGION_COLOR[region])
        d.text((bx + 22, by), headline, font=F(DJ, 10), fill=INK)


def draw_footer(d, y):
    d.line([MX, y, W - MX, y], fill=INK, width=2)
    for i, line in enumerate(fit_text(d, DATE_CHECK, F(DJB, 10), CW, 3)):
        d.text((MX, y + 8 + i * 13), line, font=F(DJB, 10), fill=RUST)
    sy = y + 8 + len(fit_text(d, DATE_CHECK, F(DJB, 10), CW, 3)) * 13 + 4
    for i, line in enumerate(fit_text(d, SOURCES, F(DJ, 9), CW, 2)):
        d.text((MX, sy + i * 12), line, font=F(DJ, 9), fill=GREY)
    return sy + len(fit_text(d, SOURCES, F(DJ, 9), CW, 2)) * 12


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_header(d)
    y = draw_region_bar(d, 84)
    # 3 lead cards
    lead_w = (CW - 2 * 10) // 3
    for i, card in enumerate(CARDS[:3]):
        draw_card(d, card, MX + i * (lead_w + 10), y, lead_w, 182, lead=True)
    y += 182 + 10
    # 10 medium cards in 2 rows of 5
    med_w = (CW - 4 * 8) // 5
    for r in range(2):
        for c in range(5):
            card = CARDS[3 + r * 5 + c]
            draw_card(d, card, MX + c * (med_w + 8), y + r * (132 + 8),
                      med_w, 132, lead=False)
    y += 2 * 132 + 8 + 10
    # map + numbers side by side
    map_w = 640
    draw_map(d, MX, y, map_w, 172)
    draw_numbers(d, MX + map_w + 10, y, CW - map_w - 10, 172)
    y += 172 + 10
    draw_briefs(d, y)
    y += 22 + 9 * 17 + 8
    end = draw_footer(d, y)
    assert end <= H - 6, "footer overflow: %d" % end
    return img


def main():
    img = render()
    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
