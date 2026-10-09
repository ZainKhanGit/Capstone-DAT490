# Where we left off (updated 2026-10-09, later)

**Pipeline: done** (`python src/run_pipeline.py`, about 20 s; reports in `outputs/logs/`).
**Section 2: 2.1, 2.2, 2.3 and 2.4 are built and have DRAFT takeaway paragraphs in the notebook** (2.2 committed in `b7a6cfd`;
2.1, 2.3, 2.4, the 2.2 takeaways and `src/viz_eda.py` are not committed yet). **Still to do: 2.5, 2.6, Section 3, references.**

## What exists for 2.2
- `src/viz.py`: shared style and builders. Palette = dataviz reference palette (blue/orange validated all-pairs;
  blue steps 250/400/600 validated as an ordinal ramp for dates and periods). Solid line = linear (OLS) fit,
  dashed = smooth (LOWESS, frac 0.45, drawn over the range holding 95% of ZIPs). Same ZIPs in every panel
  (`balanced`); growth is annualized (periods are 2, 3, 3 years long); ZIPs off the axis are drawn as ▲▼ at the edge
  and stay in every fit.
- `outputs/figures/`: `2_2_gradient_<metro>.png` (8), `2_2_two_center_{level,growth}_{dallas,tampa}.png` (4),
  `2_2_slope_summary.png`. `outputs/tables/`: `gradient_slopes.csv`, `two_center_fits.csv`.
- `notebooks/01_eda.ipynb` section 2.2 regenerates all of them (runs without errors). The "takeaways" cell is empty.

## What the figures show (OLS slopes; levels in % per 10 mi from the center, growth in points per year per 10 mi)
Our hypothesis: gradient flattens 2020-22, then holds; smaller flattening than in dense metros. The data is mixed and
mostly does not support a uniform monocentric flattening. Intervals are plain OLS (no clustering for spatial
correlation), so they are probably too narrow.
- **Atlanta** matches the prediction and keeps going: level slope -7.7 -> -6.0 -> -3.0; growth slope -0.44 -> +0.69 -> +1.03.
- **Austin** flattens late: growth slope -0.12 -> +0.21 -> +0.63 (2023-25); level slope -14.9 -> -12.7.
- **Tampa** flattens in 2020-22 (+0.57) and then reverses in 2023-25 (-0.32): contradicts "hold". Level slope ~-8 throughout.
- **Nashville** growth slope +1.02 pre-2020, -0.19, +0.72: not a clean break at 2020. Level slope -13.5 -> -12.1.
- **Phoenix** goes the other way: growth slope +0.46 -> -0.15 -> -0.30; level slope steepens (-4.3 -> -5.6). Prices peak
  at ~20 mi and fall beyond, so a straight line misdescribes it (ring/polycentric shape in the smooth fit).
- **Charlotte** shows no change (level slope ~-18 throughout; growth slope within about +-0.4 of zero).
- **Dallas and Las Vegas** have no linear distance gradient at all (Dallas level slope ~-2, R2 <= 0.006; Las Vegas ~0), in every period.
  Las Vegas has a clear hump in the smooth fit (values peak ~10-20 mi out).
- **Two-center test:** nearest-of-two distance barely changes the pooled fit (Dallas R2 0.005 -> 0.004 levels,
  0.002 -> 0.010 growth; Tampa 0.065 -> 0.080 levels, 0.049 -> 0.055 growth). It does not rescue a monocentric
  gradient. Row C shows why: fitted per center, Fort Worth ZIPs rise steeply with distance (+8 to +10% per 10 mi)
  while Dallas ZIPs are flat or slightly negative, i.e. the two cores sit at different price levels.
- Not shown: suburban job centers (Plano, Las Colinas, Scottsdale, ...). LODES would be the way to test them.

## What 2.1, 2.3 and 2.4 show (details in the notebook takeaways)
- 2.1: prices are right-skewed (skew 2.6 -> 0.4 in logs); metro medians diverge after 2022 (Austin -15% from its peak);
  spread across ZIPs inside a metro is as big as many between-metro differences; data-quality flags rise with distance.
- 2.3: expensive ZIPs form wedges on one side of the center, not rings or patches; pre-2020 growth maps have more spatial
  contrast than 2020-22 and 2023-25. Only the Phoenix and Dallas growth maps were inspected closely; check the other six.
- 2.4 (SQ2): within a metro, higher pre-2020 WFH share goes with SLOWER growth before 2020 (-1.48 pts/yr per +5 pp), slightly
  slower in 2020-22 (-0.30), faster only in 2023-25 (+0.40). Contradicts "positive, strongest in 2021-22". The measure tracks
  income (+0.66), professional jobs (+0.74) and home value (+0.74), and high-value ZIPs grew slowest pre-2020 (-0.72), so
  the strong pre-trend has to be handled in any model. Reliable-only slopes are about the same.

## Next steps
1. Read and edit the DRAFT takeaways under 2.1, 2.2, 2.3, 2.4 (the user asked for plain, non-overclaiming text).
2. Build 2.5 (indexed paths, Dec 2019 = 100, faceted by distance band; optional simple k-means with silhouette) and 2.6
   (full vs flag-free sample; ZORI inner/middle-metro check on the fixed sample).
3. Section 3 (implications) and references (data sources only; `docs/SOURCES.md`).
4. Commit the new work (`src/viz_eda.py`, new figures/tables, notebook, STATUS).

## Decisions already made (do not reopen)
- Metro = ZHVI `Metro` column; 12 column-only ZIPs flagged; 5 crosswalk-only ZIPs left out.
- Center = city hall of first-named city; second centers Fort Worth and St. Petersburg for the nearest-center
  distance; ZCTA-centroid distance kept as a robustness column.
- Keep every ZIP; flags in `zip_flags.csv`; show full vs flag-free samples.
- Growth = YoY, Dec 2019 reference, periods 2018-19 / 2020-22 / 2023-25; panel keeps all months.
- WFH share flagged unreliable when MOE/estimate > 0.5 (continuous `wfh_rel_moe` kept).
- LODES and the Dingel-Neiman index are out of the EDA.
- Show linear and smooth fits everywhere; report results plainly even where they contradict the hypotheses.

## Things to say in the write-up (they are in the reports)
- Data problems sit at the periphery (incomplete ZHVI, column-only ZIPs, no ZORI, unreliable WFH share), but the 7
  ZIPs with no 2015-2019 ACS row do not fit that pattern ("no evidence of"; small n).
- ZORI cannot check the 2022 rate shock in the outer ring: 36% of ZIPs 30+ mi out have ZORI, 13% have it at both
  Dec 2019 and Dec 2025. The rent check is an inner/middle-metro check; use `zori_growth.csv`.
- Dallas City Hall's point is in ZCTA 75202, recorded ZIP 75201; left as is (effect under 1 mi).
- Metro-column vs county-crosswalk differences (17 of 1,104 ZIPs) are probably a delineation-vintage effect; not confirmed.

## Practical notes
- Use `.venv/bin/python`. Notebook kernel: "Python 3 (capstone venv)" (registered inside `.venv`). Run notebooks with
  `.venv/bin/python -m nbconvert --execute`.
- Plain `git` in Terminal may fail (broken Xcode shortcut); working copy: `/Library/Developer/CommandLineTools/usr/bin/git`.
- Census key: `CENSUS_API_KEY` in `~/.zshrc`; step 4 does not need it again (responses cached).
- Not done: GitHub remote; backup copy of `data/raw/` (352 MB, not in git).
