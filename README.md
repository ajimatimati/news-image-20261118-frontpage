# World News Front Page — Wednesday, 18 November 2026

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/ajimatimati/news-image-20261118-frontpage/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/ajimatimati/news-image-20261118-frontpage/reward.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

Editorial `1024x1024` world news front page summarizing the verified global events of **Wednesday, 18 November 2026**, built for the [make.fun `news-image-20261118`](https://make.fun/bounty/news-image-20261118) bounty.

## Coverage (Wednesday, 18 November 2026)

1. **Asia-Pacific · Diplomacy** — *Trump lands in Shenzhen for Xi talks*: Xi greets the US leader ahead of APEC and Putin summit.
2. **Middle East · Security** — *Gulf strikes hit Kuwait & Bahrain*: Iran widens strikes; UN panel faults ceasefire breaches.
3. **Tech · Markets** — *Nvidia reports; Huang ruled out*: Earnings amid export probes and permanent CEO exit.
4. **Climate · COP31** — *COP31 1.5°C alert; EU grid deal*: Antalya finance gap; EU speeds clean power permits.
5. **Europe · War** — *Ukraine hits fuel & Crimea bridge*: Strikes slash Russian refining ahead of winter.
6. **18 Nov Brief Ticker** — US envoys visit Caracas for security pact • Pew projects Islam largest faith by 2035 • US withdraws FDA nominee Overton.

## Architecture & Reproducibility

- `build_frontpage.py`: Composites five bespoke painterly editorial illustrations into a cohesive `1024x1024` broadsheet front page using high-contrast TrueType typography optimized for both full-resolution and `300x300` thumbnail legibility, outputting `entry.png`.
- `main.py`: Python 3.13 standard-library-only runtime entrypoint (zero network access, zero third-party dependencies). Verifies image header integrity, dimensions (`<= 1024x1024`), size cap (`<= 1,048,576` bytes), and SHA-256 digest before deterministically writing `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` (defaulting to `/output/entry.png`).

## Local Verification

```bash
mkdir -p out1 out2
MAKEFUN_OUTPUT_DIR=out1 python main.py
MAKEFUN_OUTPUT_DIR=out2 python main.py
sha256sum out1/entry.png out2/entry.png
```
