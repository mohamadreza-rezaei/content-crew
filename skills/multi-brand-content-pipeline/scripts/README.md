# Helper scripts

| Script | What it does |
|---|---|
| `render.py config.json outdir` | Renders 2–10 square 1080×1080 JPEG slides (layouts `hero`, `card`, `cta`; themes `violet`, `emerald`, `sunset`). Needs Python 3, Pillow and Chrome/Chromium (`CHROME=chromium` to override). |
| `check_lines.py *.txt` | RTL line-start check: no line may begin with a Latin word, URL, hashtag or mention. |

Fonts: put `.woff2` files named `Vazirmatn-{Regular,Bold,ExtraBold,Black}.woff2` in `scripts/fonts/` (or set `font_dir` in the config). Vazirmatn is free under the SIL OFL: https://github.com/rastikerdar/vazirmatn. Swap in any font you like by renaming.
