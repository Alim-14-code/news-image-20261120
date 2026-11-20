# The World in One Page

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/Alim-14-code/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/Alim-14-code/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)

Sum up the world's news of **Friday 20 November 2026** in one image.

A newspaper front page for the whole planet: 40 stories, 7 regions, on a single 1024×1024 page — 3 lead cards, 10 medium cards, a dotted world map with numbered pins, a day-in-numbers strip, and the rest of the day in briefs. Every story was verified against wire coverage of 20 November 2026; items first reported on Thursday 19 November are named in the DATE CHECK footer, not counted as stories.

## How it works

- `render_ni20.py` draws `entry.png` with Pillow: header, region bar, 13 cards with flat illustrations, dotted world map from a hand-written land mask, numbers strip, briefs 14–40, DATE CHECK and sources footer. No network, no clock, no randomness — re-runs are byte-identical.
- `main.py` (stdlib only) copies `entry.png` to `$MAKEFUN_OUTPUT_DIR`.

```bash
python3 render_ni20.py        # rebuild entry.png
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Story list

See `briefs.md` — all 40 stories with their region and source.

## make.fun

Competition: **news-image-20261120** — $250, top 50 entries share the prize. Entries close 22 November 2026, 07:00 WIB (00:00 UTC).

Bounty: https://make.fun/bounty/news-image-20261120
