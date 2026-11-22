[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/kizuna99/news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/kizuna99/news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

# The World in One Day — Sunday 22 November 2026

Entry for make.fun's ["Sum up 22 November's world news in one image"](https://make.fun/bounty/news-image-20261122) bounty.

One front page summing up the world's news of **Sunday 22 November 2026**:
37 stories from 7 regions, every one of them dated, with sources, a numbered
world map, and a date-check note that says what was deliberately left out as
another day's news.

`entry.png` is the entry (1024×1024 PNG). `main.py` copies it to
`/output/entry.png`; the grader runs with no network, so the program does no
drawing of its own. `gen.py` is the code that drew the page — every panel,
icon, map dot and rule is drawn with Python and Pillow, no photographs and no
stock art.

## Run it

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py     # copies the committed image
python3 gen.py entry.png                   # redraws it from scratch
```

`gen.py` needs Pillow, the eight PT Serif / PT Sans Narrow files in `fonts/`,
and `countries.geojson` (Natural Earth 1:110m, public domain) for the dotted
map. It renders at 2× and downsamples, so the type stays clean.

## Sources

The day's wires and papers, read on 22 November 2026: Reuters, AP, AFP, BBC,
Al Jazeera, The Guardian, DW, France 24, ABC News (Australia) and The Japan
Times. Each item on the page names the outlets it came from; figures are as
those outlets reported them before 04:30 UTC that day.

## License

MIT — see `LICENSE`. The PT Serif and PT Sans Narrow fonts are under the SIL
Open Font License; the Natural Earth data is public domain.
