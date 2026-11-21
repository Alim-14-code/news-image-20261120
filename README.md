# The World in One Page

[![make.fun](https://img.shields.io/badge/make.fun-news--image--20261120-8a2be2)](https://make.fun/bounty/news-image-20261120)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)

Sum up the world's news of **Friday 20 November 2026** in one image.

A newspaper front page for the whole planet: 35 stories, 7 regions,
on a single 1024×1024 page — 3 lead cards, 10 medium cards, a
"THE DAY IN UTC" timeline, a dotted world map with numbered pins,
a day-in-numbers strip, and the rest of the day in briefs. Every story
carries a verification tag — OFFICIAL (on the record), CONFIRMED (two
or more outlets), REPORTED (one outlet) — explained in the footer
legend. Every story was verified against wire coverage of
20 November 2026; items first reported on Thursday 19 November are
named in the DATE CHECK footer, not counted as stories.

## How it works

- `render_ni20_r4.py` draws `entry.png` with Pillow: header, region bar,
  UTC timeline, 13 cards with flat illustrations and verification pills,
  dotted world map from a hand-written land mask, numbers strip,
  briefs 14–35 with colour-coded numerals, DATE CHECK and sources
  footer. No network, no clock, no randomness — re-runs are
  byte-identical.
- `main.py` (stdlib only) copies `entry.png` to `$MAKEFUN_OUTPUT_DIR`.

```bash
python3 render_ni20_r4.py        # rebuild entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Story list

See `briefs.md` — all 35 stories with their region, source and
verification tag.

## make.fun

Competition: **news-image-20261120** — $250, top 50 entries share the
prize. Entries close 22 November 2026, 07:00 WIB (00:00 UTC).
