#!/usr/bin/env python3
"""Render entry.png for make.fun news-image-20261120 — ROUND 2.

One page, Friday 20 November 2026: 40 stories, 7 regions.
Rebuilt from the R1 render after the R1 evaluation: giant serif
masthead + KPI strip (the rank 1-50 pattern), 3 rich lead cards
(Akvan map-based, Kyiv missile trails, COP31 globe+thermometer),
10 feature cards with REPORTED/CLAIM/FORECAST tags, solid navy
map with beige continents + numbered red pins, 2-column brief
list, explicit DATE CHECK footer.

Content changes vs R1: PIF-tower strike REMOVED from the leads
(it was first reported Thu 19 Nov) and named only in DATE CHECK;
Korea's $1tn export milestone removed from the briefs (also Thu);
Anthropic first close, BepiColombo, GTA VI day-one sales, Japan
CPI 2.3% (core 2.2%), China rates hold, UK-EU reset, Senegal
boat, CGIL strike, Phillips 118, Bukele third-term bid promoted.

Every story was verified against wire coverage or the day's news
roundups of 20 Nov 2026 (WIB); see briefs.md. Items first
reported Thu 19 Nov are named in the DATE CHECK footer, not as
stories.

Deterministic: no network, no clock, no randomness.

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
SAND = (229, 218, 196)
GOLD = (198, 152, 58)
GREY = (104, 112, 126)
LINE = (214, 205, 185)
DOT = (120, 138, 156)
RED = (178, 44, 36)
GREEN = (62, 110, 72)
MAP_NAVY = (16, 30, 54)
MAP_LAND = (233, 221, 191)
MAP_LAND2 = (214, 200, 165)

DJ = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
DJB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DSB = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
DS = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"


def _pick(*paths):
    for p in paths:
        if os.path.exists(p):
            return p
    return paths[-1]


LSB = _pick("/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf", DSB)
LSI = _pick("/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf", DS)

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
        while lines and d.textlength(lines[-1] + "…", font=font) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + "…"
    return lines


def fit_one_line(d, text, font, max_w):
    """Single line, truncated with an ellipsis if too wide."""
    if d.textlength(text, font=font) <= max_w:
        return text
    while text and d.textlength(text + "…", font=font) > max_w:
        text = text[:-1]
    return text + "…"


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

# ---- the 13 cards: (num, kicker, headline, deck, region, source, art, tag, lon, lat) ----
CARDS = [
    (1, "ODISHA, INDIA · CYCLONE", "Cyclone Akvan makes landfall in eastern India",
     "Severe storm crosses near Gopalpur; 300,000+ evacuated, winds "
     "90-100 gusting 110 km/h, 423 rescue teams deployed, schools shut. "
     "(IMD, The Hindu)",
     "Asia", "IMD / The Hindu", "cyclone", "REPORTED", 85.2, 19.5),
    (2, "KYIV, UKRAINE · WAR", "Russia fires wave of ~30 ballistic missiles at Kyiv",
     "Seven overnight waves hit energy and transport sites; fires burn "
     "in three districts; Dutch and Austrian embassies damaged. "
     "(Kyiv Post, Reuters)",
     "Europe", "Kyiv Post / Reuters", "kyiv", "REPORTED", 30.5, 50.45),
    (3, "ANTALYA, TÜRKIYE · CLIMATE", "COP31 reaches its final day deadlocked",
     "Closing draft omits fossil-fuel phase-out while $120bn adaptation "
     "finance stays unresolved; hosts push '35 by 35' clean-power goal. "
     "(UN News, Reuters)",
     "World", "UN News / Reuters", "cop31", "REPORTED", 30.7, 36.9),
    (4, "SEOUL/TOKYO", "AI sell-off sinks Asia to worst week since 2020",
     "Taiex -6.8%, KOSPI -5.4%, Nikkei -4.9% intraday. (Reuters)",
     "Asia", "Reuters", "aiselloff", "REPORTED", 127.0, 37.5),
    (5, "MERCURY · SPACE", "BepiColombo reaches Mercury after 8 years",
     "ESA/JAXA probe ends 6bn-mile trip. (ESA, BBC)",
     "World", "ESA / BBC", "bepi", "REPORTED", -52.8, 5.2),
    (6, "NEW YORK · MARKETS", "Anthropic ends first day up 17%",
     "Opens $111.50, closes $97.17 - 17% above its $83 offer. (Reuters)",
     "Americas", "Reuters", "anthropic", "REPORTED", -74.0, 40.7),
    (7, "TOKYO · ECONOMY", "Japan inflation hits 2.3%; BoJ hike eyed",
     "Oct CPI up from 2.1%; core above 2% a second month. (Reuters)",
     "Asia", "Reuters", "cpi", "REPORTED", 139.7, 35.7),
    (8, "BEIJING · RATES", "China holds lending rates for 18th month",
     "1-year stays 3.0%, 5-year 3.5%, as expected. (PBOC)",
     "Asia", "PBOC / Reuters", "rates", "REPORTED", 116.4, 39.9),
    (9, "BRUSSELS · EUROPE", "Burnham holds first EU-UK reset summit",
     "Costa & von der Leyen host UK PM. (EU Council)",
     "Europe", "EU Council", "summit", "REPORTED", 4.35, 50.85),
    (10, "WELLINGTON · CRICKET", "Phillips makes history with 118 vs India",
     "First NZ batter with centuries in all 3 formats vs India. (ICC, AP)",
     "Oceania", "ICC / AP", "phillips", "REPORTED", 174.8, -41.3),
    (11, "SAN SALVADOR · POLITICS", "Bukele registers for third-term bid",
     "Files for Feb 2027 vote; rights groups object. (AP)",
     "Americas", "AP", "bukele", "REPORTED", -89.2, 13.7),
    (12, "SENEGAL", "Migrant boat capsizes off Yenne; 4 dead",
     "Dozens missing from ~50-100 aboard. (Al Jazeera)",
     "Africa", "Al Jazeera", "senegal", "REPORTED", -17.4, 14.7),
    (13, "ROME · LABOUR", "Italy's CGIL holds 24-hr general strike",
     "Unions rally in ~100 squares against 2027 budget. (CGIL, AFP)",
     "Europe", "CGIL / AFP", "cgil", "REPORTED", 12.5, 41.9),
]

# ---- briefs 14-40: (num, place, headline, region, source, tag, lon, lat) ----
BRIEFS = [
    (14, "FRANCE", "Fire in 18-storey French flats: 1 dead, 15 hurt", "Europe", "", "", 2.35, 48.85),
    (15, "TAIWAN", "Taiwan council hopeful out on NT$500k bail", "Asia", "", "", 121.6, 25.0),
    (16, "TAIWAN", "Taiwan widens spouse share in inheritance law", "Asia", "", "", 121.6, 25.0),
    (17, "VIETNAM", "Vietjet expands routes to the Philippines", "Asia", "TTR Weekly", "", 106.7, 10.8),
    (18, "WORLD", "GTA 6 sales pass The Odyssey's $1.80bn", "World", "Mezha", "", -3.2, 55.95),
    (19, "GENOA", "Genoa airport shut by drones for 4 hours", "Europe", "Daily Baku", "", 8.9, 44.4),
    (20, "EUROPE", "Europe ready to talk; E3 weigh Moscow trip", "Europe", "BBC", "", 37.6, 55.75),
    (21, "JAPAN", "Hayabusa2 gives up the asteroid landing", "Asia", "Space.com", "", 139.4, 35.5),
    (22, "HORMUZ", "Tankers hit mines east of Hormuz, on fire", "Middle East", "UKMTO", "", 56.3, 26.5),
    (23, "LEBANON", "40 Hezbollah sites hit; woman killed", "Middle East", "AJ", "", 35.5, 33.9),
    (24, "AFRICA", "260M children live in African conflict zones", "Africa", "STC", "", 22.0, 4.0),
    (25, "WELLINGTON", "NZ votes tomorrow; Australia may decide it", "Oceania", "AP", "", 174.8, -41.3),
    (26, "RIYADH", "MBS phoned Trump twice over the Houthis", "Middle East", "Axios", "", 46.7, 24.7),
    (27, "WASHINGTON", "Vance: US in direct talks with the Houthis", "Middle East", "AJ", "", -77.0, 38.9),
    (28, "YEMEN", "Houthis seize Hanish islands, Mocha port", "Middle East", "AJ", "CLAIM", 43.3, 12.7),
    (29, "SAUDI ARABIA", "East-West pipeline shut after drone strike", "Middle East", "AJ", "", 38.1, 24.1),
    (30, "NIGERIA", "Mob kills Osun accident survivor in Nigeria", "Africa", "Punch", "", 4.6, 7.8),
    (31, "S. AFRICA", "SACP pushes back on ANC entitlement", "Africa", "News24", "", 28.0, -26.2),
    (32, "AFRICA", "More climate cash for Africa? Europe says no", "Africa", "BBC", "", 2.35, 48.85),
    (33, "BURUNDI", "Burundi: Banyamulenge caught in arrest wave", "Africa", "", "", 29.4, -3.4),
    (34, "C. AFRICA", "CAR: Sakaï 2 power plan sparks mockery", "Africa", "", "", 18.6, 4.4),
    (35, "ESWATINI", "Eswatini youth 'loses kidney in job scam'", "Africa", "", "", 31.4, -26.3),
    (36, "SENEGAL", "Senegal marks Armed Forces Day", "Africa", "", "", -17.4, 14.7),
    (37, "WASHINGTON", "Trump flies home, briefing today", "Americas", "", "", -77.0, 38.9),
    (38, "CINCINNATI", "Trump pardons baseball's Pete Rose", "Americas", "", "", -84.5, 39.1),
    (39, "CRYPTO", "Bitcoin $62,150 as crypto slides with stocks", "Americas", "", "", -74.0, 40.7),
    (40, "SYDNEY", "LG names new Australia, NZ boss", "Oceania", "PRNewswire", "", 151.2, -33.9),
]

# ---- KPI strip under the masthead: (big, label) ----
NUMBERS = [
    ("300,000+", "evacuated ahead of Cyclone Akvan"),
    ("~30", "ballistic missiles fired at Kyiv"),
    ("-7%", "Asia shares' worst week since 2020"),
    ("2.3%", "Japan Oct headline CPI; BoJ eyed"),
    ("118", "Phillips' historic century vs India"),
    ("8 yrs", "BepiColombo reaches Mercury"),
]

# ---- items deliberately left out: first reported Thursday 19 Nov ----
DATE_CHECK = (
    "DATE CHECK — First reported Thursday 19 Nov, so NOT shown here as Friday's news: "
    "ICJ Myanmar genocide verdict · Trump-Xi-Putin Shenzhen trilateral · Houthi strike on "
    "Riyadh's PIF tower · Anthropic's $83 IPO pricing · GTA VI midnight launch · Voyager 1 "
    "one light-day · Senate 48-51 Iran war-powers vote · $190.4m Van Gogh sale · Kerch Bridge "
    "attack · Han Duck-soo's acquittal · EU's €45bn Ukraine loan."
)

EVERY = (
    "Every story here happened, or was first reported, on Friday 20 November 2026, "
    "in at least one time zone. Claims are attributed, not stated as fact."
)

SOURCES = (
    "Sources: Reuters · AP · AFP · BBC · The Hindu · IMD · UN News · Al Jazeera · ICC · "
    "EU Council · PBOC. Original vector drawings."
)

# ---- land mask: 56 cols (lon -180..180) x 28 rows (lat 85..-60).
# Hand-drawn spans per row: [(col_start, col_end), ...] inclusive.
# Cell (c, r) covers lon -180+c*360/56 .., lat 85-r*145/28 .. ----
MAP_GRID = [
    [(2, 4), (10, 15), (18, 23)],
    [(2, 6), (9, 13), (19, 24)],
    [(2, 17), (19, 24)],
    [(2, 19), (24, 24), (30, 32), (34, 55)],
    [(6, 19), (21, 22), (24, 25), (28, 55)],
    [(7, 19), (26, 55)],
    [(8, 19), (28, 55)],
    [(8, 17), (28, 32), (34, 49)],
    [(8, 17), (28, 37), (39, 47), (48, 49)],
    [(9, 16), (26, 37), (38, 50)],
    [(10, 15), (27, 36), (38, 41), (43, 46)],
    [(10, 14), (26, 33), (34, 36), (39, 41), (42, 44)],
    [(11, 15), (25, 35), (39, 41), (42, 44)],
    [(13, 15), (25, 35), (39, 40), (42, 44)],
    [(15, 19), (25, 35), (42, 46)],
    [(15, 20), (26, 34), (42, 48)],
    [(15, 21), (27, 34), (43, 49)],
    [(15, 22), (29, 34), (45, 48)],
    [(16, 21), (29, 33), (48, 50)],
    [(17, 21), (29, 33), (45, 51)],
    [(17, 21), (30, 33), (45, 51)],
    [(17, 20), (30, 32), (45, 51)],
    [(16, 19), (30, 32), (45, 50)],
    [(16, 18), (30, 31), (49, 51), (53, 55)],
    [(16, 18), (53, 55)],
    [(16, 18)],
    [(16, 17)],
    [(17, 17)],
]


def lonlat_to_xy(lon, lat, mx, my, mw, mh):
    # crop the poles: lat 85..-60 uses the height far better than -90..90
    px = mx + (lon + 180.0) / 360.0 * mw
    py = my + (85.0 - lat) / 145.0 * mh
    return px, py


# ---- illustrations (Pillow primitives only) ----
def _strip(d, x, y, w, h, fill, text, tfill, size=9, right=None):
    d.rectangle([x, y, x + w, y + h], fill=fill)
    d.text((x + 6, y + h // 2), text, font=F(DJB, size), fill=tfill, anchor="lm")
    if right:
        d.text((x + w - 6, y + h // 2), right, font=F(DJB, size), fill=tfill, anchor="rm")


def art_cyclone(d, x, y, w, h):
    SEA = (26, 64, 80)
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    # land: left portion, diagonal coast
    d.polygon([(x, y), (x + int(w * 0.46), y), (x + int(w * 0.34), y + h - 16),
               (x, y + h - 16)], fill=(233, 216, 172))
    # tiny houses on the coast
    for hx, hy in [(10, 16), (26, 32), (14, 50)]:
        d.rectangle([x + hx, y + hy, x + hx + 7, y + hy + 5], fill=(255, 255, 255))
        d.polygon([(x + hx - 1, y + hy), (x + hx + 3.5, y + hy - 4), (x + hx + 8, y + hy)],
                  fill=(178, 82, 42))
    # spiral over the Bay of Bengal
    cx, cy = x + int(w * 0.70), y + (h - 16) // 2
    for i, r in enumerate([30, 23, 16, 9]):
        a0 = 40 + i * 70
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 260,
              fill=(235, 242, 245), width=4 if r > 12 else 3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(178, 44, 36))
    # landfall pin on the coast
    px, py = x + int(w * 0.38), y + (h - 16) // 2 + 6
    d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(178, 44, 36),
              outline=(255, 255, 255), width=1)
    d.text((px + 7, py - 2), "GOPALPUR", font=F(DJB, 8), fill=(255, 255, 255))
    d.text((x + w - 6, y + h - 24), "BAY OF BENGAL", font=F(DJB, 8),
           fill=(150, 185, 200), anchor="ra")
    _strip(d, x, y + h - 16, w, 16, (16, 40, 54), "LANDFALL · GUSTS 110 KM/H",
           (240, 200, 90), right="CYCLONE AKVAN")


def art_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(20, 26, 46))
    for sx, sy in [(12, 8), (60, 14), (120, 6), (200, 12), (260, 8), (170, 20)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=(220, 220, 235))
    # missile trails arcing down
    for tx, col in [(52, (240, 160, 40)), (130, (240, 200, 90)), (208, (240, 160, 40)),
                    (262, (240, 200, 90))]:
        d.arc([x + tx - 18, y - 8, x + tx + 18, y + 42], 200, 340, fill=col, width=3)
        d.ellipse([x + tx - 3, y + 30, x + tx + 3, y + 36], fill=col)
    # skyline with lit windows
    for i, bh in enumerate([22, 34, 18, 30, 26, 20]):
        bx = x + 8 + i * ((w - 16) // 6)
        bw = (w - 16) // 6 - 4
        d.rectangle([bx, y + h - 16 - bh, bx + bw, y + h - 16], fill=(62, 72, 100))
        for wy in range(4, bh - 4, 9):
            d.rectangle([bx + 3, y + h - 16 - bh + wy, bx + 6,
                         y + h - 13 - bh + wy], fill=(240, 200, 90))
    # fire burst on one rooftop
    fx, fy = x + 62, y + h - 16 - 34
    for a in range(0, 360, 45):
        ex = fx + 10 * math.cos(math.radians(a))
        ey = fy + 10 * math.sin(math.radians(a))
        d.line([fx, fy, ex, ey], fill=(240, 140, 40), width=2)
    d.ellipse([fx - 4, fy - 4, fx + 4, fy + 4], fill=(240, 160, 40))
    _strip(d, x, y + h - 16, w, 16, (12, 16, 32), "01:25 LOCAL · 7 WAVES",
           (255, 255, 255), right="~30 MISSILES")


def art_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 230, 210))
    # globe
    gx, gy, gr = x + 44, y + (h - 16) // 2, 26
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 170))
    d.ellipse([gx - gr + 6, gy - gr + 8, gx - gr + 20, gy - gr + 18], fill=(96, 160, 90))
    d.ellipse([gx + 2, gy + 2, gx + 18, gy + 16], fill=(96, 160, 90))
    d.ellipse([gx - 12, gy + 8, gx + 2, gy + 20], fill=(120, 175, 105))
    d.arc([gx - gr, gy - gr, gx + gr, gy + gr], 200, 320, fill=(255, 255, 255), width=2)
    # thermometer
    tx = x + 84
    d.rectangle([tx - 3, gy - 24, tx + 3, gy + 12], fill=(255, 255, 255),
                outline=(120, 120, 120), width=1)
    d.rectangle([tx - 2, gy - 16, tx + 2, gy + 12], fill=(178, 44, 36))
    d.ellipse([tx - 7, gy + 8, tx + 7, gy + 22], fill=(178, 44, 36))
    # badge box
    bx0, by0, bx1, by1 = x + 104, y + 6, x + w - 8, y + h - 22
    d.rectangle([bx0, by0, bx1, by1], fill=(255, 255, 255), outline=(178, 44, 36), width=1)
    d.rectangle([bx0, by0, bx1, by0 + 13], fill=(178, 44, 36))
    d.text((bx0 + 8, by0 + 7), "ANTALYA · NOV 20", font=F(DJB, 8),
           fill=(255, 255, 255), anchor="lm")
    d.text(((bx0 + bx1) // 2, by0 + 32), "COP31", font=F(DJB, 20), fill=NAVY, anchor="mm")
    d.text(((bx0 + bx1) // 2, by1 - 7), "FINAL DAY · DEADLOCK", font=F(DJB, 8),
           fill=RED, anchor="mm")
    _strip(d, x, y + h - 16, w, 16, (178, 44, 36), "$120BN FINANCE GAP",
           (255, 255, 255), right="NO PHASE-OUT IN DRAFT")


def art_aiselloff(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 34, 58))
    rows = [("TAIEX", "-6.8%"), ("KOSPI", "-5.4%"), ("NIKKEI", "-4.9%")]
    for i, (name, val) in enumerate(rows):
        ry = y + 5 + i * 15
        d.text((x + 6, ry), name, font=F(DJB, 10), fill=(255, 255, 255))
        d.text((x + 54, ry), val, font=F(DJB, 10), fill=(230, 80, 60))
    # falling chart on the right
    pts = [(x + 112, y + 6), (x + 128, y + 12), (x + 142, y + 26), (x + w - 8, y + h - 8)]
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=(230, 80, 60), width=2)
    d.polygon([(x + w - 8, y + h - 8), (x + w - 14, y + h - 10), (x + w - 10, y + h - 14)],
              fill=(230, 80, 60))


def art_bepi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(14, 20, 38))
    for sx, sy in [(10, 8), (34, 16), (60, 6), (96, 14), (130, 8)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1], fill=(255, 255, 255))
    # dashed trajectory
    for i in range(6):
        sx = x + 34 + i * 14
        sy = y + 16 + i * 3
        d.line([sx, sy, sx + 8, sy + 2], fill=(120, 140, 170), width=1)
    # probe body + panels
    d.rectangle([x + 14, y + 12, x + 28, y + 22], fill=(198, 152, 58))
    d.rectangle([x + 4, y + 15, x + 14, y + 19], fill=(74, 120, 180))
    d.rectangle([x + 28, y + 15, x + 38, y + 19], fill=(74, 120, 180))
    # Mercury
    mx, my, mr = x + w - 26, y + h // 2 + 2, 14
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(150, 140, 125))
    d.ellipse([mx - 7, my - 5, mx - 2, my], fill=(115, 105, 92))
    d.ellipse([mx + 2, my + 3, mx + 7, my + 8], fill=(115, 105, 92))
    d.text((x + 8, y + h - 12), "6BN MILES · 8 YEARS", font=F(DJB, 8), fill=(240, 200, 90))


def art_anthropic(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(14, 52, 40))
    # candlesticks, rising trend (kept left of the REPORTED pill)
    candles = [(8, 26, 18, 1), (26, 22, 16, 0), (44, 24, 14, 1), (62, 18, 12, 0),
               (80, 14, 10, 0)]
    for cx0, top, bot, red in candles:
        col = (220, 70, 50) if red else (62, 180, 120)
        d.line([x + cx0 + 4, y + top - 4, x + cx0 + 4, y + bot + 14], fill=col, width=1)
        d.rectangle([x + cx0, y + top, x + cx0 + 8, y + bot + 10], fill=col)
    d.text((x + 8, y + 4), "$97.17", font=F(DJB, 14), fill=(240, 200, 90))
    d.text((x + 8, y + h - 12), "NASDAQ · FIRST CLOSE · +17%", font=F(DJB, 8),
           fill=(255, 255, 255))


def art_cpi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 232, 214))
    # basket
    d.polygon([(x + 12, y + 20), (x + 44, y + 20), (x + 40, y + 38), (x + 16, y + 38)],
              fill=(44, 60, 96))
    d.line([x + 16, y + 20, x + 22, y + 10], fill=(44, 60, 96), width=2)
    d.line([x + 40, y + 20, x + 34, y + 10], fill=(44, 60, 96), width=2)
    d.text((x + 58, y + 8), "2.3%", font=F(DJB, 20), fill=NAVY)
    d.polygon([(x + 126, y + 22), (x + 118, y + 30), (x + 134, y + 30)], fill=RED)
    d.text((x + 58, y + h - 13), "CORE 2.2% · OCT CPI", font=F(DJB, 8), fill=GREY)


def art_rates(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(30, 41, 66))
    d.text((x + 8, y + 4), "1Y · 3.00%", font=F(DJB, 10), fill=(255, 255, 255))
    d.rectangle([x + 8, y + 16, x + 88, y + 22], fill=(198, 152, 58))
    d.text((x + 8, y + 24), "5Y · 3.50%", font=F(DJB, 10), fill=(255, 255, 255))
    d.rectangle([x + 8, y + 36, x + 104, y + 42], fill=(198, 152, 58))


def art_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    # EU flag
    d.rectangle([x + 8, y + 6, x + 78, y + 28], fill=(0, 56, 147))
    for i in range(8):
        a = math.radians(i * 45)
        sx = x + 43 + 11 * math.cos(a)
        sy = y + 17 + 7 * math.sin(a)
        d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=(240, 200, 60))
    # UK flag (simplified)
    d.rectangle([x + 88, y + 6, x + w - 8, y + 28], fill=(0, 40, 90))
    d.rectangle([x + 88, y + 14, x + w - 8, y + 20], fill=(255, 255, 255))
    d.rectangle([x + 118, y + 6, x + 124, y + 28], fill=(255, 255, 255))
    d.rectangle([x + 88, y + 16, x + w - 8, y + 18], fill=(206, 17, 38))
    d.rectangle([x + 120, y + 6, x + 122, y + 28], fill=(206, 17, 38))
    d.text((x + w // 2, y + h - 12), "RESET TALKS", font=F(DJB, 9), fill=NAVY, anchor="mm")


def art_phillips(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 110, 70))
    d.rectangle([x + 30, y + 6, x + w - 30, y + h - 6], fill=(96, 150, 105))
    # stumps
    for sx in [x + w - 44, x + w - 40, x + w - 36]:
        d.line([sx, y + 12, sx, y + 22], fill=(255, 255, 255), width=2)
    # bat + ball
    d.polygon([(x + 52, y + 12), (x + 58, y + 10), (x + 44, y + 34), (x + 38, y + 36)],
              fill=(214, 178, 120))
    d.ellipse([x + 66, y + 30, x + 74, y + 38], fill=(178, 44, 36))
    d.text((x + 8, y + 6), "118", font=F(DJB, 16), fill=(255, 255, 255))
    d.text((x + 8, y + h - 12), "· RECORD", font=F(DJB, 8), fill=(240, 200, 90))


def art_bukele(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    d.text((x + 8, y + 4), "THIRD TERM", font=F(DJB, 10), fill=NAVY)
    d.text((x + w - 8, y + h - 12), "2027", font=F(DJB, 10), fill=RUST, anchor="ra")
    # ballot box + tick
    bx, by = x + w // 2 - 24, y + h - 30
    d.rectangle([bx, by, bx + 48, by + 22], fill=(44, 60, 96))
    d.rectangle([bx - 4, by - 5, bx + 52, by], fill=(30, 41, 66))
    d.rectangle([bx + 20, by - 5, bx + 28, by], fill=(232, 226, 210))
    d.line([bx + 8, by + 11, bx + 18, by + 19], fill=(255, 255, 255), width=3)
    d.line([bx + 18, by + 19, bx + 40, by + 3], fill=(255, 255, 255), width=3)


def art_senegal(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(40, 90, 110))
    for i in range(3):
        yy = y + h - 14 + i * 5
        d.arc([x + 6, yy - 3, x + w - 6, yy + 5], 200, 340, fill=(140, 180, 195))
    # capsized hull
    d.polygon([(x + 52, y + 22), (x + 118, y + 22), (x + 108, y + 32), (x + 62, y + 32)],
              fill=(52, 62, 78))
    d.line([x + 85, y + 22, x + 85, y + 8], fill=(52, 62, 78), width=2)
    # heads in the water
    for hx, hy in [(46, 34), (128, 36), (140, 30)]:
        d.ellipse([x + hx - 3, y + hy - 3, x + hx + 3, y + hy + 3], fill=(232, 200, 160))
    d.rectangle([x + 6, y + 4, x + 62, y + 18], fill=(178, 44, 36))
    d.text((x + 34, y + 11), "4 DEAD", font=F(DJB, 9), fill=(255, 255, 255), anchor="mm")
    d.text((x + 8, y + h - 12), "YENNE COAST", font=F(DJB, 8), fill=(200, 220, 230))


def art_cgil(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(160, 40, 32))
    # Italian tricolour strip
    tw = w // 3
    d.rectangle([x, y, x + tw, y + 10], fill=(0, 140, 70))
    d.rectangle([x + tw, y, x + 2 * tw, y + 10], fill=(255, 255, 255))
    d.rectangle([x + 2 * tw, y, x + w, y + 10], fill=(206, 17, 38))
    # crowd: heads + raised arms
    for i, hx in enumerate([16, 40, 64, 88, 112, 136, 156]):
        hy = y + 26 + (i % 2) * 6
        d.ellipse([x + hx - 4, hy - 4, x + hx + 4, hy + 4], fill=(240, 210, 180))
        d.line([x + hx + 5, hy + 2, x + hx + 9, hy - 8], fill=(240, 210, 180), width=2)
    d.text((x + w // 2, y + h - 10), "100 SQUARES", font=F(DJB, 9),
           fill=(255, 255, 255), anchor="mm")


ART = {
    "cyclone": art_cyclone, "kyiv": art_kyiv, "cop31": art_cop31,
    "aiselloff": art_aiselloff, "bepi": art_bepi, "anthropic": art_anthropic,
    "cpi": art_cpi, "rates": art_rates, "summit": art_summit,
    "phillips": art_phillips, "bukele": art_bukele, "senegal": art_senegal,
    "cgil": art_cgil,
}

# pin nudges (px) so the East-Asia / Europe clusters stay readable
PIN_NUDGE = {3: (8, 6), 4: (-2, 6), 7: (8, -2), 8: (-8, -8), 9: (-8, -8), 13: (8, 8)}


# ---- layout ----
MX = 24                      # side margin
CW = W - 2 * MX              # content width = 976


def region_counts():
    counts = {}
    for c in CARDS:
        counts[c[4]] = counts.get(c[4], 0) + 1
    for b in BRIEFS:
        counts[b[3]] = counts.get(b[3], 0) + 1
    return counts


def draw_tag(d, x, y, tag):
    w = d.textlength(tag, font=F(DJB, 8)) + 12
    d.rounded_rectangle([x - w, y, x, y + 14], radius=3, fill=(20, 20, 20))
    d.text((x - w // 2, y + 7), tag, font=F(DJB, 8), fill=(255, 255, 255), anchor="mm")


def draw_header(d):
    d.text((MX, 10), "THE WORLD IN ONE DAY", font=F(DJB, 12), fill=RED)
    d.text((W - MX, 11), "FRIDAY'S NEWS · ONE PAGE · 40 STORIES · 7 REGIONS",
           font=F(DJB, 10), fill=GREY, anchor="ra")
    # giant serif masthead, auto-fit
    text = "Friday 20 November 2026"
    size = 84
    while size > 40:
        f = F(LSB, size)
        if d.textlength(text, font=f) <= CW:
            break
        size -= 2
    d.text((MX + CW // 2, 28), text, font=F(LSB, size), fill=INK, anchor="ma")
    mh = size + 8
    d.text((MX + CW // 2, 28 + mh), "Cyclone Akvan strikes India · Ballistic missiles "
           "hit Kyiv · COP31 deadlocked on final day · Asian AI sell-off",
           font=F(LSI, 17), fill=RED, anchor="ma")
    y = 28 + mh + 24
    d.line([MX, y, W - MX, y], fill=INK, width=3)
    d.line([MX, y + 5, W - MX, y + 5], fill=INK, width=1)
    return y + 10


def draw_kpi(d, y):
    cw = CW // 6
    for i, (big, label) in enumerate(NUMBERS):
        cx = MX + i * cw
        if i:
            d.line([cx, y + 4, cx, y + 50], fill=LINE, width=1)
        d.text((cx + 12, y + 2), big, font=F(DSB, 24), fill=(150, 40, 32))
        for j, line in enumerate(fit_text(d, label, F(DJ, 9), cw - 24, 2)):
            d.text((cx + 12, y + 28 + j * 11), line, font=F(DJ, 9), fill=GREY)
    return y + 50


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
    parts = ["%s %d" % (r.upper(), counts.get(r, 0)) for r in order]
    label = "   ·   ".join(parts)
    d.text((MX + CW // 2, y + 18), label, font=F(DJB, 10), fill=INK, anchor="ma")
    return y + 28


def draw_card(d, card, x, y, w, h, lead=False):
    num, kicker, headline, deck, region, source, art, tag, lon, lat = card
    col = REGION_COLOR[region]
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    d.rectangle([x, y, x + w, y + 4], fill=col)
    # header: number badge + kicker + source
    if lead:
        bs, bf, kf, sf = 11, 12, 10, 8
        hy = y + 16
    else:
        bs, bf, kf, sf = 9, 10, 8, 7
        hy = y + 14
    d.ellipse([x + 8, hy - bs, x + 8 + 2 * bs, hy + bs], fill=RED)
    d.text((x + 8 + bs, hy), str(num), font=F(DJB, bf), fill=(255, 255, 255), anchor="mm")
    # kicker truncated so it can never collide with the source at right
    src_w = d.textlength(source.upper(), font=F(DJB, sf))
    max_kw = w - 14 - 2 * bs - 8 - int(src_w) - 8
    kicker = fit_one_line(d, kicker, F(DJB, kf), max_kw)
    d.text((x + 14 + 2 * bs, hy), kicker, font=F(DJB, kf), fill=col, anchor="lm")
    d.text((x + w - 8, hy), source.upper(), font=F(DJB, sf), fill=GREY, anchor="rm")
    if lead:
        art_y, art_h = y + 30, 80
        hl, dk = F(DJB, 16), F(DJ, 10)
        mh_l, md_l, sh, sd = 2, 3, 18, 12
    else:
        art_y, art_h = y + 26, 46
        hl, dk = F(DJB, 12), F(DJ, 9)
        mh_l, md_l, sh, sd = 2, 2, 13, 11
    ART[art](d, x + 8, art_y, w - 16, art_h)
    draw_tag(d, x + w - 12, art_y + 4, tag)
    ty = art_y + art_h + 6
    hlines = fit_text(d, headline, hl, w - 16, mh_l)
    for i, line in enumerate(hlines):
        d.text((x + 8, ty + i * sh), line, font=hl, fill=INK)
    dy = ty + len(hlines) * sh + 2
    for i, line in enumerate(fit_text(d, deck, dk, w - 16, md_l)):
        d.text((x + 8, dy + i * sd), line, font=dk, fill=(60, 68, 80))


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=MAP_NAVY, outline=LINE, width=1)
    d.text((x + 10, y + 8), "WHERE IT HAPPENED", font=F(DJB, 11), fill=(255, 255, 255))
    d.text((x + w - 10, y + 8), "pins 1-13 · dots 14-40", font=F(DJ, 9),
           fill=(170, 185, 205), anchor="ra")
    mx, my, mw, mh = x + 8, y + 28, w - 16, h - 46
    # solid continents from the grid
    cw, ch = mw / 56.0, mh / 28.0
    for r, spans in enumerate(MAP_GRID):
        for c0, c1 in spans:
            d.rectangle([mx + c0 * cw, my + r * ch,
                         mx + (c1 + 1) * cw + 0.5, my + (r + 1) * ch + 0.5],
                        fill=MAP_LAND)
    # brief dots first (under the pins)
    for num, place, headline, region, source, tag, lon, lat in BRIEFS:
        bx, by = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        d.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=REGION_COLOR[region])
    # numbered pins for the 13 cards
    for num, kicker, headline, deck, region, source, art, tag, lon, lat in CARDS:
        bx, by = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        dx, dy = PIN_NUDGE.get(num, (0, 0))
        bx, by = bx + dx, by + dy
        d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=RED,
                  outline=(255, 255, 255), width=2)
        d.text((bx, by), str(num), font=F(DJB, 9), fill=(255, 255, 255), anchor="mm")
    d.text((x + 10, y + h - 16), "1-3 Lead · 4-13 Feature · 5 BepiColombo via Kourou",
           font=F(DJ, 8), fill=(170, 185, 205))


def draw_briefs(d, x, y, w, h):
    d.text((x, y), "ALSO ON FRIDAY 20 NOVEMBER — 27 MORE STORIES",
           font=F(DJB, 11), fill=NAVY)
    d.line([x, y + 16, x + w, y + 16], fill=LINE, width=1)
    col_w = (w - 16) // 2
    f_num, f_pl, f_tx, f_src = F(DJB, 9), F(DJB, 9), F(DJ, 9), F(DJ, 9)
    for i, (num, place, headline, region, source, tag, lon, lat) in enumerate(BRIEFS):
        col = i // 14
        row = i % 14
        bx = x + col * (col_w + 16)
        by = y + 20 + row * 14
        num_s = "%d " % num
        pl_s = place + " "
        src_s = (" (" + source + ")") if source else ""
        tag_s = (" · " + tag) if tag else ""
        num_w = d.textlength(num_s, font=f_num)
        pl_w = d.textlength(pl_s, font=f_pl)
        src_w = d.textlength(src_s, font=f_src)
        tag_w = d.textlength(tag_s, font=f_pl)
        head_w = col_w - num_w - pl_w - src_w - tag_w - 4
        head = fit_one_line(d, headline, f_tx, head_w)
        d.text((bx, by), num_s, font=f_num, fill=RED)
        d.text((bx + num_w, by), pl_s, font=f_pl, fill=INK)
        hx = bx + num_w + pl_w
        d.text((hx, by), head, font=f_tx, fill=INK)
        tx = hx + d.textlength(head, font=f_tx)
        if tag:
            d.text((tx, by), tag_s, font=f_pl, fill=RED)
            tx += tag_w
        if source:
            d.text((tx, by), src_s, font=f_src, fill=GREY)
    return y + 20 + 14 * 14


def draw_footer(d, y):
    d.rectangle([MX, y, W - MX, y + 48], outline=RED, width=1)
    lines = fit_text(d, DATE_CHECK, F(DJ, 10), CW - 16, 3)
    prefix = "DATE CHECK — "
    pw = d.textlength(prefix, font=F(DJB, 10))
    for i, line in enumerate(lines):
        ly = y + 6 + i * 13
        if i == 0:
            d.text((MX + 8, ly), prefix, font=F(DJB, 10), fill=RED)
            d.text((MX + 8 + pw, ly), line[len(prefix):], font=F(DJ, 10), fill=INK)
        else:
            d.text((MX + 8, ly), line, font=F(DJ, 10), fill=INK)
    sy = y + 52
    for i, line in enumerate(fit_text(d, EVERY, F(DJ, 9), CW, 1)):
        d.text((MX, sy + i * 12), line, font=F(DJ, 9), fill=(60, 68, 80))
    sy += 12
    for i, line in enumerate(fit_text(d, SOURCES, F(DJ, 9), CW, 1)):
        d.text((MX, sy + i * 12), line, font=F(DJ, 9), fill=GREY)
    return sy + 12


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = draw_header(d)
    y = draw_kpi(d, y)
    y = draw_region_bar(d, y + 4)
    # 3 lead cards
    lead_w = (CW - 2 * 10) // 3
    for i, card in enumerate(CARDS[:3]):
        draw_card(d, card, MX + i * (lead_w + 10), y, lead_w, 194, lead=True)
    y += 194 + 8
    # 10 medium cards in 2 rows of 5
    med_w = (CW - 4 * 8) // 5
    for r in range(2):
        for c in range(5):
            card = CARDS[3 + r * 5 + c]
            draw_card(d, card, MX + c * (med_w + 8), y + r * (132 + 8),
                      med_w, 132, lead=False)
    y += 2 * 132 + 8 + 8
    # map + briefs side by side
    map_w = 340
    draw_map(d, MX, y, map_w, 216)
    draw_briefs(d, MX + map_w + 10, y, CW - map_w - 10, 216)
    y += 216 + 8
    end = draw_footer(d, y)
    assert end <= H - 4, "footer overflow: %d" % end
    return img


def main():
    img = render()
    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
