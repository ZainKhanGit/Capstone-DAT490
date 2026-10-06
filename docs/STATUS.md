# Where we left off (2026-10-06)

**Pipeline: done.** All eight steps run end to end (`python src/run_pipeline.py`, about 20 s). Each step writes
a report to `outputs/logs/` that Section 1 of the EDA quotes. **EDA figures: not started.**
`notebooks/01_eda.ipynb` is a skeleton: setup and data loading work (verified, no errors), Section 1 displays
the eight reports inline, Section 2 has the figure plan 2.1–2.6 with `# TODO` cells, Section 3 and the
references are empty.

## Next step: build the figures, starting with 2.2 (the gradient, SQ1)

1. Open `notebooks/01_eda.ipynb` with the kernel **"Python 3 (capstone venv)"** and run the first three code
   cells. That loads `panel`, `zg` (one row per ZIP), `dist`, `flags`, `acs`, `zori`, `zorig`, `zcta`.
2. In the plot-conventions cell, pick the palette first (8 colorblind-safe metro colors, one sequential and
   one diverging map) and use it everywhere. Consider loading the `dataviz` skill before the first chart.
3. Figure 2.2: cumulative growth against city-hall distance, one panel per metro, columns = pre-2020 /
   2020-2022 / 2023-2025. Columns in `zg`: `cum_2017_2019`, `cum_2019_2022`, `cum_2022_2025`, plus
   `rel_cum_*` (growth minus the metro median). Distance: `dist_cityhall_mi`; for Dallas and Tampa also draw
   `dist_nearest_mi` (two-center test). Same y-axis scale across metros.
4. Then 2.1 distributions, 2.3 maps (`zcta` polygons + `rel_cum_*`), 2.4 SQ2 plots (`acs.wfh_share_2019`),
   2.5 trajectories (`panel.index_dec2019`), 2.6 robustness. Write a one-line takeaway under every figure.

## Decisions already made (do not reopen)
- Metro = ZHVI `Metro` column; 12 column-only ZIPs flagged; 5 crosswalk-only ZIPs left out.
- Center = city hall of first-named city; second centers Fort Worth and St. Petersburg for the nearest-center
  distance; ZCTA-centroid distance kept as a robustness column.
- Keep every ZIP; flags are in `zip_flags.csv`; show full vs. flag-free samples.
- Growth = YoY, Dec 2019 reference, periods 2018-19 / 2020-22 / 2023-25; panel keeps all months.
- WFH share flagged unreliable when MOE/estimate > 0.5 (continuous `wfh_rel_moe` kept for sensitivity).
- LODES and the Dingel-Neiman index are out of the EDA.

## Things to say in the write-up (they are in the reports; do not lose them)
- Data problems sit at the periphery (incomplete ZHVI, column-only ZIPs, no ZORI, unreliable WFH share), but
  the 7 ZIPs with no 2015-2019 ACS row do **not** fit that pattern ("no evidence of"; small n).
- ZORI cannot check the 2022 rate shock in the outer ring: 36% of ZIPs 30+ mi out have ZORI, 13% have it at
  both Dec 2019 and Dec 2025. Rent check = inner/middle metro only; use the fixed sample in `zori_growth.csv`.
- Second centers change the distance variable a lot in Dallas (rank corr 0.68) and Tampa (0.80); the ZCTA-
  centroid alternative barely changes it (rank corr >= 0.99).
- Dallas City Hall's point falls in ZCTA 75202, recorded ZIP is 75201; left as is (under 1 mi effect).
- Metro-column vs county-crosswalk differences (17 of 1,104 ZIPs) are probably a delineation-vintage effect;
  not confirmed.

## Practical notes
- Use `.venv/bin/python`, not system python (system python has no geopandas).
- Plain `git` in Terminal may fail (broken Xcode shortcut). Working copy:
  `/Library/Developer/CommandLineTools/usr/bin/git`, or use GitHub Desktop.
- Census key: `CENSUS_API_KEY` in `~/.zshrc`. Step 4 does not need it again (responses cached in `data/raw/acs/`).
- Not yet done: GitHub remote (local repo only), a backup copy of `data/raw/` (352 MB, not in git).
- Open question to settle when making figures: how to show the 248 unreliable-WFH ZIPs in the SQ2 plots
  (different marker vs. excluded vs. shown in a second panel).
