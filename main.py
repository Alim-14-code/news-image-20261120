#!/usr/bin/env python3
"""news-image-20261120 — ROUND 4 (R4c).

One-page newspaper for Friday 20 November 2026: 35 stories, 7 regions.
Rendered fresh with Pillow. Stdlib + Pillow only, deterministic
(no network, no clock, no randomness). Output: entry.png 1024x1024.

Layout: header + KPI strip + region bar + UTC strip + 3 lead cards +
10 feature cards (2x5) + "ALSO ON FRIDAY" (dotted world map + 22 briefs)
+ DATE CHECK + footer legend.
"""

import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
W, H = 1024, 1024
MARGIN = 28
CREAM = (250, 244, 231)
PAPER = (253, 249, 240)
NAVY = (18, 38, 66)
NAVY_SOFT = (38, 62, 96)
RED = (178, 34, 34)
RED_SOFT = (198, 64, 48)
INK = (28, 28, 28)
GREY = (110, 108, 100)
LINE = (196, 186, 168)
GOLD = (176, 138, 60)

BASE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE, "fonts")


def _font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def fonts():
    return {
        "archivo": lambda s: _font("Archivo.ttf", s),
        "playfair": lambda s: _font("PlayfairDisplay-Black.ttf", s),
        "italic": lambda s: _font("PlayfairDisplay-Italic.ttf", s),
    }


F = fonts()

# ---------------------------------------------------------------- data
# (num, region, headline, body, source, tag)
LEADS = [
    (1, "ASIA", "Cyclone Akvan slams Odisha coast",
     "Severe Cyclone Akvan crosses the Andhra-Odisha coast near "
     "Gopalpur by noon, 90-100 kmph winds gusting to 110; 300,000+ "
     "evacuated, 423 rescue teams deployed, schools shut.",
     "IMD / The Hindu", "CONFIRMED"),
    (2, "EUROPE", "Kyiv hit by ~30 ballistic missiles",
     "Russia fires ~30 ballistic missiles at Kyiv in seven overnight "
     "waves; fires in three districts, Dutch and Austrian embassies "
     "damaged.",
     "Kyiv Post / Reuters", "CONFIRMED"),
    (3, "WORLD", "COP31 final day deadlocked in Antalya",
     "Closing draft omits the fossil-fuel phase-out while $120bn "
     "adaptation finance stays unresolved; hosts push a "
     "'35 by 35' clean-power goal.",
     "UN News / Reuters", "CONFIRMED"),
]

# (num, region, headline, body, source, tag)
FEATURES = [
    (4, "ASIA", "AI sell-off sinks Asia to worst week since 2020",
     "Taiex -6.8%, KOSPI -5.4%, Nikkei -4.9% intraday.", "Reuters", "REPORTED"),
    (5, "WORLD", "BepiColombo reaches Mercury after 8 years",
     "ESA/JAXA probe ends its 6bn-mile trip.", "ESA / BBC", "CONFIRMED"),
    (6, "AMERICAS", "Anthropic ends first day up 17%",
     "Opens $111.50, closes $97.17, 17% above its $83 offer.", "Reuters", "REPORTED"),
    (7, "ASIA", "Japan inflation hits 2.3%; BoJ hike eyed",
     "Oct headline CPI up from 2.1%; core 2.2%, above 2% a second month.", "Reuters", "REPORTED"),
    (8, "ASIA", "China holds lending rates for 18th month",
     "1-year LPR 3.0%, 5-year 3.5%, as expected.", "PBOC / Reuters", "OFFICIAL"),
    (9, "EUROPE", "Burnham holds first EU-UK reset summit",
     "Costa & von der Leyen host the UK PM in Brussels.", "EU Council", "OFFICIAL"),
    (10, "OCEANIA", "Phillips makes history with 118 vs India",
     "First NZ batter with centuries in all 3 formats vs India.", "ICC / AP", "CONFIRMED"),
    (11, "AMERICAS", "Bukele registers for third-term bid",
     "Files with the electoral tribunal for the Feb 2027 vote; rights groups object.", "AP", "REPORTED"),
    (12, "AFRICA", "Migrant boat capsizes off Yenne, Senegal; 4 dead",
     "Dozens missing from ~50-100 aboard as Canary arrivals surge.", "Al Jazeera", "REPORTED"),
    (13, "EUROPE", "Italy's CGIL holds 24-hr general strike",
     "Unions rally in ~100 squares against the 2027 budget; transit hit.", "CGIL / AFP", "CONFIRMED"),
]

# (num, region, text, tag)
BRIEFS = [
    (14, "EUROPE", "Fire in an 18-storey French apartment block: 1 dead, 15 injured.", "REPORTED"),
    (15, "ASIA", "Taiwan council candidate released on NT$500,000 bail over alleged foreign funding.", "REPORTED"),
    (16, "ASIA", "Taiwan Executive Yuan approves Civil Code inheritance amendments; spouse share rises to two-thirds.", "REPORTED"),
    (17, "WORLD", "GTA 6 sales pass The Odyssey's $1.80bn box-office run.", "REPORTED"),
    (18, "EUROPE", "Genoa airport suspends all flights for 4 hours overnight after unidentified drones are detected.", "REPORTED"),
    (19, "EUROPE", "Europe says it is ready for talks with Russia on ending the war in Ukraine.", "REPORTED"),
    (20, "ASIA", "Hayabusa2 engine trouble — Japan's probe abandons its asteroid landing.", "REPORTED"),
    (21, "MIDDLE EAST", "Two oil tankers hit naval mines east of the Strait of Hormuz and catch fire.", "OFFICIAL"),
    (22, "MIDDLE EAST", "Israel says it hit 40 Hezbollah sites in the past day.", "REPORTED"),
    (23, "AFRICA", "Save the Children: 260 million children now live in conflict zones across Africa.", "OFFICIAL"),
    (24, "OCEANIA", "New Zealand votes Saturday — Luxon vs Hipkins tied.", "REPORTED"),
    (25, "MIDDLE EAST", "MBS phoned Trump twice calling for US military action against the Houthis.", "REPORTED"),
    (26, "MIDDLE EAST", "JD Vance: US in direct talks with the Houthis.", "REPORTED"),
    (27, "MIDDLE EAST", "Houthis seize Greater/Lesser Hanish islands and Mocha port (CLAIM).", "REPORTED"),
    (28, "MIDDLE EAST", "East-West pipeline shut after a drone strike; it carries ~4% of global oil.", "REPORTED"),
    (29, "AFRICA", "Mob kills an Osun accident survivor in Nigeria; police hunt suspects.", "REPORTED"),
    (30, "AFRICA", "SACP pushes back against ANC entitlement.", "REPORTED"),
    (31, "AFRICA", "BBC: more climate money for Africa? Europe says use what's already pledged.", "REPORTED"),
    (32, "AFRICA", "Burundi: Banyamulenge caught in an arrest wave, 25+ refugees detained since October.", "REPORTED"),
    (33, "AMERICAS", "Trump returns from China; White House press conference on the 20th.", "REPORTED"),
    (34, "AMERICAS", "Trump announces a posthumous pardon for baseball's Pete Rose.", "REPORTED"),
    (35, "AMERICAS", "Bitcoin $62,150, -1.85%, as crypto slides with stocks.", "REPORTED"),
]

KPI = [
    ("300,000+", "evacuated ahead of Akvan"),
    ("~30", "ballistic missiles at Kyiv"),
    ("-7%", "Asia shares worst since 2020"),
    ("2.3%", "Japan Oct CPI; BoJ hike eyed"),
    ("118", "Phillips' 118 vs India"),
    ("8 yrs", "BepiColombo reaches Mercury"),
]

UTC_STRIP = [
    ("~00:00", "Kyiv missile waves"),
    ("~02:00", "Genoa airport shut"),
    ("~06:30", "Akvan landfall"),
    ("~07:00", "Asia shares, worst week"),
    ("~12:00", "EU-UK reset summit"),
    ("~15:00", "COP31 deadlocked"),
    ("~21:00", "Anthropic +17% debut"),
]

REGIONS = [("EUROPE", 6), ("ASIA", 7), ("MIDDLE EAST", 6), ("AFRICA", 6),
           ("AMERICAS", 5), ("OCEANIA", 2), ("WORLD", 3)]

DATE_CHECK = ("ICJ Myanmar genocide verdict · Trump-Xi-Putin Shenzhen trilateral · "
              "Houthi strike on Riyadh's PIF tower · Anthropic's $83 IPO pricing · "
              "GTA VI midnight launch · Voyager 1 one light-day · Senate 48-51 Iran "
              "war-powers vote · $190.4m Van Gogh sale · Kerch Bridge attack · "
              "Han Duck-soo's acquittal · EU's €45bn Ukraine loan.")

# (lon, lat) for map pins 1-13
PINS = {
    1: (85.0, 19.0), 2: (30.5, 50.4), 3: (30.7, 36.9), 4: (121.0, 25.0),
    5: (8.6, 49.9), 6: (-122.4, 37.8), 7: (139.7, 35.7), 8: (116.4, 39.9),
    9: (4.35, 50.85), 10: (174.8, -41.3), 11: (-89.2, 13.7),
    12: (-17.2, 14.7), 13: (12.5, 41.9),
}

# (lon, lat) for map dots 14-35
DOTS = {
    14: (2.35, 48.85), 15: (121.5, 25.0), 16: (121.0, 24.0),
    17: (-118.2, 34.0), 18: (8.9, 44.4), 19: (37.6, 55.75),
    20: (139.7, 35.7), 21: (56.5, 26.5), 22: (35.5, 33.3),
    23: (36.8, -1.3), 24: (174.8, -41.3), 25: (46.7, 24.7),
    26: (44.2, 15.35), 27: (42.7, 13.7), 28: (45.0, 25.0),
    29: (4.5, 7.8), 30: (28.0, -26.2), 31: (38.7, 9.0),
    32: (29.36, -3.38), 33: (116.4, 39.9), 34: (-84.5, 39.1),
    35: (-74.0, 40.7),
}

# coarse land mask: (lon_min, lon_max, lat_min, lat_max)
LAND = [
    (-168, -55, 15, 72), (-105, -80, 7, 18), (-80, -35, -56, 12),
    (-58, -20, 60, 84), (-11, 40, 36, 71), (-18, 51, -35, 32),
    (35, 60, 12, 42), (60, 180, 5, 77), (95, 141, -11, 28),
    (113, 154, -39, -11), (166, 178, -47, -34), (129, 146, 31, 46),
    (-6, 2, 50, 59),
]
# thin sea carve-out (Mediterranean)
SEA = [(-6, 36, 33, 36)]


def is_land(lon, lat):
    for lo, hi, la, lb in LAND:
        if lo <= lon <= hi and la <= lat <= lb:
            for slo, shi, sla, slb in SEA:
                if slo <= lon <= shi and sla <= lat <= slb:
                    return False
            return True
    return False

# ---------------------------------------------------------------- helpers
def wrap_to_width(text, font, max_w):
    """Wrap text to fit max_w pixels; returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_tracked(d, xy, text, font, fill, tracking=2):
    """Draw text with extra letter spacing; returns total width."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x - xy[0] - tracking


def text_w(text, font):
    return font.getlength(text)


def pill(d, box, fill, outline=None):
    d.rounded_rectangle(box, radius=(box[3] - box[1]) // 2, fill=fill,
                        outline=outline, width=1)


def tag_pill(d, x, y, tag):
    """Verification pill; returns width used."""
    f = F["archivo"](10)
    tw = text_w(tag, f) + 12
    h = 15
    fill = NAVY if tag == "OFFICIAL" else (RED if tag == "CONFIRMED" else GREY)
    pill(d, [x, y, x + tw, y + h], fill=fill)
    d.text((x + 6, y + 2), tag, font=f, fill=(255, 255, 255))
    return tw


def rule(d, x0, x1, y, fill=NAVY, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)


# ---------------------------------------------------------------- map
def draw_map(d, box):
    """Dotted world map with numbered pins (1-13) and dots (14-35)."""
    x0, y0, x1, y1 = box
    mw, mh = x1 - x0, y1 - y0

    def project(lon, lat):
        px = x0 + (lon + 180.0) / 360.0 * mw
        py = y0 + (90.0 - lat) / 180.0 * mh
        return px, py

    step = 7
    r = 1.5
    gx = x0 + 3
    while gx < x1 - 2:
        gy = y0 + 3
        while gy < y1 - 2:
            lon = (gx - x0) / mw * 360.0 - 180.0
            lat = 90.0 - (gy - y0) / mh * 180.0
            if is_land(lon, lat):
                d.ellipse([gx - r, gy - r, gx + r, gy + r], fill=NAVY_SOFT)
            gy += step
        gx += step

    # dots 14-35 (small red)
    for num, (lon, lat) in DOTS.items():
        px, py = project(lon, lat)
        d.ellipse([px - 2.2, py - 2.2, px + 2.2, py + 2.2], fill=RED)

    # pins 1-13 (numbered red circles)
    f = F["archivo"](9)
    for num, (lon, lat) in PINS.items():
        px, py = project(lon, lat)
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=RED,
                  outline=(255, 255, 255), width=1)
        t = str(num)
        tw = text_w(t, f)
        d.text((px - tw / 2, py - 5), t, font=f, fill=(255, 255, 255))

# ---------------------------------------------------------------- sections
def draw_header(d):
    x0, x1 = MARGIN, W - MARGIN
    y = 22
    # top small line
    f_small = F["archivo"](12)
    left = "THE WORLD IN ONE DAY"
    right = "FRIDAY'S NEWS · ONE PAGE · 35 STORIES · 7 REGIONS"
    draw_tracked(d, (x0, y), left, f_small, NAVY, tracking=2)
    rw = text_w(right, f_small)
    d.text((x1 - rw, y), right, font=f_small, fill=NAVY)
    y += 20
    rule(d, x0, x1, y, fill=NAVY, width=2)
    y += 8
    # title
    f_title = F["playfair"](46)
    d.text((x0, y), "Friday 20 November 2026", font=f_title, fill=NAVY)
    y += 56
    f_sub = F["italic"](20)
    d.text((x0, y), "Thirty-five stories, seven regions — one day, one page.",
           font=f_sub, fill=RED)
    # right: issue tag
    f_tag = F["archivo"](11)
    tag = "NO. 324 · FRIDAY EDITION"
    tw = text_w(tag, f_tag)
    d.text((x1 - tw, y + 4), tag, font=f_tag, fill=GREY)
    return y + 28


def draw_kpi(d, y):
    x0, x1 = MARGIN, W - MARGIN
    h = 44
    d.rectangle([x0, y, x1, y + h], outline=LINE, width=1)
    cw = (x1 - x0) / 6.0
    f_num = F["archivo"](20)
    f_lab = F["archivo"](9)
    for i, (num, lab) in enumerate(KPI):
        cx = x0 + cw * i
        if i:
            d.line([(cx, y + 6), (cx, y + h - 6)], fill=LINE, width=1)
        d.text((cx + 10, y + 5), num, font=f_num, fill=NAVY)
        for j, ln in enumerate(wrap_to_width(lab, f_lab, cw - 20)):
            d.text((cx + 10, y + 26 + j * 10), ln, font=f_lab, fill=GREY)
    return y + h + 8


def draw_regions(d, y):
    x0 = MARGIN
    f = F["archivo"](11)
    x = x0
    for name, n in REGIONS:
        label = "%s %d" % (name, n)
        tw = text_w(label, f) + 16
        pill(d, [x, y, x + tw, y + 18], fill=NAVY)
        d.text((x + 8, y + 3), label, font=f, fill=(255, 255, 255))
        x += tw + 8
    return y + 26


def draw_utc(d, y):
    x0, x1 = MARGIN, W - MARGIN
    h = 30
    d.rectangle([x0, y, x1, y + h], fill=NAVY)
    f_lab = F["archivo"](11)
    lab = "THE DAY IN UTC"
    d.text((x0 + 10, y + 8), lab, font=f_lab, fill=(255, 255, 255))
    lx = x0 + 10 + text_w(lab, f_lab) + 18
    f_t = F["archivo"](11)
    f_e = F["archivo"](10)
    cw = (x1 - lx) / 7.0
    for i, (t, ev) in enumerate(UTC_STRIP):
        cx = lx + cw * i
        d.text((cx, y + 4), t, font=f_t, fill=(255, 210, 120))
        for j, ln in enumerate(wrap_to_width(ev, f_e, cw - 8)):
            d.text((cx, y + 17 + j * 9), ln, font=f_e, fill=(220, 225, 235))
            if j >= 0:
                break
    return y + h + 8


def draw_leads(d, y):
    x0, x1 = MARGIN, W - MARGIN
    h = 168
    cw = (x1 - x0 - 16) / 3.0
    f_kick = F["archivo"](10)
    f_head = F["playfair"](17)
    f_body = F["archivo"](11)
    f_src = F["archivo"](9)
    for i, (num, region, head, body, src, tag) in enumerate(LEADS):
        bx = x0 + (cw + 8) * i
        d.rectangle([bx, y, bx + cw, y + h], outline=LINE, width=1)
        # number badge + kicker
        d.ellipse([bx + 10, y + 10, bx + 30, y + 30], fill=RED)
        f_n = F["archivo"](12)
        d.text((bx + 15, y + 13), str(num), font=f_n, fill=(255, 255, 255))
        d.text((bx + 36, y + 14), region, font=f_kick, fill=RED)
        # headline
        yy = y + 38
        for ln in wrap_to_width(head, f_head, cw - 20):
            d.text((bx + 10, yy), ln, font=f_head, fill=NAVY)
            yy += 20
        # body
        yy += 2
        for ln in wrap_to_width(body, f_body, cw - 20):
            d.text((bx + 10, yy), ln, font=f_body, fill=INK)
            yy += 14
        # source + tag pill at bottom
        d.text((bx + 10, y + h - 24), src, font=f_src, fill=GREY)
        tw = tag_pill(d, bx + cw - 92, y + h - 26, tag)
    return y + h + 8


def draw_features(d, y):
    x0, x1 = MARGIN, W - MARGIN
    rows, cols = 2, 5
    gap = 8
    cw = (x1 - x0 - gap * (cols - 1)) / cols
    ch = 94
    f_head = F["playfair"](13)
    f_body = F["archivo"](10)
    f_src = F["archivo"](9)
    for idx, (num, region, head, body, src, tag) in enumerate(FEATURES):
        r, c = divmod(idx, cols)
        bx = x0 + c * (cw + gap)
        by = y + r * (ch + gap)
        d.rectangle([bx, by, bx + cw, by + ch], outline=LINE, width=1)
        d.text((bx + 8, by + 7), "%d · %s" % (num, region), font=f_src, fill=RED)
        yy = by + 20
        for ln in wrap_to_width(head, f_head, cw - 16):
            d.text((bx + 8, yy), ln, font=f_head, fill=NAVY)
            yy += 15
        body_lines = wrap_to_width(body, f_body, cw - 16)
        max_body = max(0, (by + ch - 18 - yy - 2) // 12)
        for ln in body_lines[:max_body]:
            d.text((bx + 8, yy), ln, font=f_body, fill=INK)
            yy += 12
        d.text((bx + 8, by + ch - 15), src, font=f_src, fill=GREY)
        tag_pill(d, bx + cw - 78, by + ch - 17, tag)
    return y + rows * ch + (rows - 1) * gap + 8

def draw_also(d, y):
    x0, x1 = MARGIN, W - MARGIN
    f_head = F["archivo"](13)
    head = "ALSO ON FRIDAY 20 NOVEMBER — 22 MORE STORIES"
    d.text((x0, y), head, font=f_head, fill=NAVY)
    rule(d, x0 + text_w(head, f_head) + 10, x1, y + 8, fill=NAVY, width=1)
    y += 22
    h = 250
    # left: map
    map_w = 320
    d.rectangle([x0, y, x0 + map_w, y + h], outline=LINE, width=1)
    f_map = F["archivo"](10)
    d.text((x0 + 8, y + 6), "WHERE IT HAPPENED", font=f_map, fill=NAVY)
    draw_map(d, [x0 + 6, y + 24, x0 + map_w - 6, y + h - 6])
    # right: briefs in 2 columns
    bx = x0 + map_w + 12
    bw = x1 - bx
    col_w = (bw - 12) / 2.0
    f_b = F["archivo"](10)
    f_n = F["archivo"](10)
    half = 11
    for col in range(2):
        cx = bx + col * (col_w + 12)
        yy = y
        for item in BRIEFS[col * half:(col + 1) * half]:
            num, region, text, tag = item
            # number
            d.text((cx, yy), "%d." % num, font=f_n, fill=RED)
            lines = wrap_to_width(text, f_b, col_w - 26)
            ly = yy
            for ln in lines:
                d.text((cx + 24, ly), ln, font=f_b, fill=INK)
                ly += 11
            yy = ly + 2
    return y + h + 8


def draw_datecheck(d, y):
    x0, x1 = MARGIN, W - MARGIN
    f_lab = F["archivo"](11)
    f_txt = F["archivo"](10.5)
    lab = "DATE CHECK — FIRST REPORTED THU 19 NOV, LEFT OUT ON PURPOSE: "
    lines = wrap_to_width(DATE_CHECK, f_txt, x1 - x0 - 16)
    h = 18 + len(lines) * 12 + 8
    d.rectangle([x0, y, x1, y + h], outline=RED, width=2)
    d.text((x0 + 8, y + 5), lab, font=f_lab, fill=RED)
    yy = y + 22
    for ln in lines:
        d.text((x0 + 8, yy), ln, font=f_txt, fill=INK)
        yy += 12
    return y + h + 8


def draw_footer(d, y):
    x0, x1 = MARGIN, W - MARGIN
    rule(d, x0, x1, y, fill=NAVY, width=2)
    y += 6
    f = F["archivo"](10)
    # legend pills
    x = x0
    d.text((x, y), "VERIFICATION:", font=f, fill=NAVY)
    x += text_w("VERIFICATION: ", f)
    for tag, desc in [("OFFICIAL", "on the record"),
                      ("CONFIRMED", "two or more outlets"),
                      ("REPORTED", "one outlet")]:
        w = tag_pill(d, x, y - 1, tag)
        x += w + 4
        d.text((x, y), desc, font=f, fill=GREY)
        x += text_w(desc + "   ", f)
    # sources line
    f2 = F["archivo"](9)
    src = ("Sources: IMD · The Hindu · Kyiv Post · Reuters · UN News · ESA · BBC · "
           "PBOC · EU Council · ICC · AP · Al Jazeera · UKMTO · Save the Children · "
           "CGIL · AFP · Axios · Punch · News24 · Mezha · Daily Baku · Space.com")
    for j, ln in enumerate(wrap_to_width(src, f2, x1 - x0)):
        d.text((x0, y + 18 + j * 11), ln, font=f2, fill=GREY)
    return y + 18 + 11 + 4


# ---------------------------------------------------------------- main
def main():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    # paper inset
    d.rectangle([MARGIN - 10, 10, W - MARGIN + 10, H - 10], fill=PAPER,
                outline=LINE, width=1)
    y = draw_header(d)
    y = draw_kpi(d, y)
    y = draw_regions(d, y)
    y = draw_utc(d, y)
    y = draw_leads(d, y)
    y = draw_features(d, y)
    y = draw_also(d, y)
    y = draw_datecheck(d, y)
    y = draw_footer(d, y)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    img.save(path, "PNG")
    print("wrote", path, img.size)


if __name__ == "__main__":
    main()
