# Where we left off (updated 2026-10-09, end of day)

**Everything is built.** Pipeline (8 steps), the full EDA notebook (sections 1, 2.1 to 2.6, 3, references) and the written
report `report/Team10_EDA.pdf` (35 pages: 27 body including references, 8 appendix; source `report/Team10_EDA.tex`).
The takeaway paragraphs in the notebook are labeled DRAFT; the report text is derived from them and from the data-quality reports.
**Committed through `aaa0b40`.** Not yet committed: the report-size figure rewrite (`src/viz.py`, `src/viz_eda.py`, new `src/make_figures.py`),
regenerated figures, the rebuilt PDF and this note.

## Final deliverable
(see the 2026-10-11 update at the bottom)
PDF report, built from LaTeX (same toolchain as the plan and lit review, same structure as the prior-team example: long data
sources/cleaning section, figures each explained in prose, data-sources-only references). The assignment text does not name a
format; **check the Canvas page for any required format or length** before submitting. Supporting files to attach or link:
`notebooks/01_eda.ipynb` (reproducible analysis), the repo (code, `docs/SOURCES.md`).

Rebuild: `.venv/bin/python report/make_tables.py`, then `cd report && xelatex Team10_EDA.tex` twice.
Figures in `report/figures/` are 1800 px JPEG copies of `outputs/figures/*.png`, written by `src/make_figures.py`.

## Known issues to decide
1. ~~Figure text small~~ FIXED: figures are now 8.5 in wide with 10-12.5 pt text (about 7.6 pt on the page at 6.5 in). Regenerate
   everything with `.venv/bin/python src/make_figures.py` (also refreshes `report/figures/*.jpg`); sizes live in `viz.FS` / `viz.FIG_W`.
2. The 2.3 takeaway is based on all eight growth maps (checked); the report quotes only what was seen.
3. The report body is 27 pages including references (35 with the appendix); the prior example was 14. Trim if the assignment gives a page limit (the appendix can go first).
4. Statistical caveats are stated wherever they apply: plain OLS intervals ignore spatial correlation, simple fits are not the
   event study, and the smooth curves rest on few ZIPs at the far end.

## Results in one paragraph
The hypothesis (gradient flattens 2020-22, then holds) holds clearly only in Atlanta (growth slope -0.44 -> +0.69 -> +1.03 pts/yr
per 10 mi), late in Austin, and in Tampa until it reverses (+0.57 -> -0.32); Phoenix goes the other way and its pattern disappears
when flagged outer ZIPs are dropped (level slope -4.3% -> +0.5%); Charlotte, Dallas and Las Vegas show nothing; Nashville's outer
advantage predates 2020. Expensive ZIPs form wedges, not rings; two city halls do not rescue a monocentric gradient (Fort Worth
ZIPs rise with distance from Fort Worth, Dallas ZIPs do not). SQ2: within metro, WFH share goes with slower growth pre-2020
(-1.48), slower in 2020-22 (-0.30), faster only in 2023-25 (+0.40), and WFH share tracks income (+0.66) and home value (+0.74), so
the post-2020 slopes cannot be read as an exposure effect. SQ3: four groups, silhouette about 0.36 (k=2 is 0.375), groups track
metro and housing type more than distance. Rents (inner and middle metro only, 478 ZIPs): rent growth kept rising with distance in
2023-25 (+0.33) while price growth did not (-0.07).

## Decisions already made (do not reopen)
- Metro = ZHVI `Metro` column; 12 column-only ZIPs flagged; 5 crosswalk-only ZIPs left out.
- Center = city hall of the first-named city; second centers Fort Worth and St. Petersburg; ZCTA-centroid distance kept as a robustness column.
- Keep every ZIP; flags in `zip_flags.csv`; show full vs flag-free samples.
- Growth = YoY, Dec 2019 reference, periods 2018-19 / 2020-22 / 2023-25, annualized for comparison; the panel keeps all months.
- WFH share flagged unreliable when MOE/estimate > 0.5. LODES and the Dingel-Neiman index are out of the EDA.
- Linear and smooth fits everywhere; report results plainly even where they contradict the plan.

## Practical notes
- Use `.venv/bin/python`. Notebook kernel: "Python 3 (capstone venv)". Run notebooks with `.venv/bin/python -m nbconvert --execute`.
- Plain `git` in Terminal may fail (broken Xcode shortcut); working copy: `/Library/Developer/CommandLineTools/usr/bin/git`.
- Census key: `CENSUS_API_KEY` in `~/.zshrc`; step 4 does not need it again (responses cached).
- Not done: GitHub remote; backup copy of `data/raw/` (352 MB, not in git).

## 2026-10-11 update: interpretation audit applied
- `docs/interpretation_audit.md` (and `.pdf`) lists every interpretive claim in 2.2-2.6 with the number behind it. All proposed
  corrections were applied to the report and the notebook (donut reduced to Atlanta only, wedge claim limited to the five metros
  where a direction test passes, Las Vegas direction fixed, education claim removed, Austin sentence made consistent, Phoenix
  classification fixed, rents paragraph reworded, two-center price levels limited to Dallas-Fort Worth).
- New results in the report: pre-2020 trend controlled (later exposure slopes +0.03 and +0.13, intervals include zero), direction
  test (Table 4), band comparison with bootstrap intervals (Table 7).
- `src/audit_checks.py` computes the extra checks; `src/check_report_numbers.py` verifies 267 numbers/phrases against the data and
  the .tex. Run both before submitting; the second must say FAILED 0.
- Report is now 26 pages (was 24).

## 2026-10-11 later: fonts, Section 2.2, final files
- Font audit found tables at 5.7 to 10 pt (each was scaled to fit) and figures in Arial against a Latin Modern page. Now every table is
  9 pt, unscaled, and figures use Latin Modern Roman. Slope table is two stacked panels so it fits at that size.
- Section 2.2's metro-by-metro prose is one paragraph grouped as flatten / do not flatten / reverse; Table 3 and Figure 4 carry the numbers.
- Final files: `report/Team10_EDA.pdf` and `report/Team10_EDA.tex` (27 pages). `report/Team10_EDA_source.zip` bundles the .tex with
  the figures and tables it needs.
- Both checks pass: `src/audit_checks.py` ran cleanly, `src/check_report_numbers.py` reports FAILED 0 (268 checks).

## 2026-10-11 later still: page layout
- Large blank bands on some pages were float placement (a lone tall figure forming its own mostly empty page), not a rendering failure.
  Fix in the preamble: `\floatpagefraction` raised from 0.7 to 0.95 and `[!tbp]` on figures and tables. Wasted vertical space fell from about
  1,600 pt to 326 pt and the report went from 27 to 25 pages. Relaxing the other float fractions or using `[!htbp]` made it worse (28 to 30 pages).
- Build log: 0 overfull boxes, 0 missing files, 0 undefined references; 12 harmless underfull notices (narrow table cells and bibliography URLs);
  one notice that page 11 holds only a float (the 8-inch two-center figure).

## 2026-10-21: methodology submission
- New assignment: methods document plus preliminary results. Files: `report/Team10_Methodology.pdf` (12 pages; source `report/Team10_Methodology.tex`)
  and `notebooks/02_methods.ipynb` (runs in about a minute; the full model grid is loaded from saved tables unless `RUN_FULL_ML = True`).
- Code: `src/methods.py` (event study with spatial block bootstrap, mixed-effects model, Moran's I, leave-one-metro-out models, clustering
  comparison), `src/viz_methods.py`, `src/make_method_results.py` (all results, about 10 minutes), `src/make_method_figures.py` (redraw only),
  `report/make_method_tables.py`, `src/check_method_numbers.py` (41 checks, must say FAILED 0).
- Rebuild: `make_method_results.py` (or `make_method_figures.py` if the tables already exist), `report/make_method_tables.py`, then `xelatex` twice in `report/`.
- Main results: pooled gradient +1.15 per 10 mi by 2025 (Atlanta +4.98 drives it); the work-from-home coefficient changes sign with controls;
  Moran's I 0.35 to 0.47; held-out R-squared 0.10 to 0.30, work-from-home share adds nothing detectable; clusters weakly separated, mixture disagrees.
- Bug found and fixed by the checker: the bootstrap order depended on Python's set ordering, so intervals changed between runs. Now sorted.
- Not committed.

## 2026-10-21 later: review of the methodology document
- Added a spatial block bootstrap to the exposure model (`methods.exposure_block_bootstrap`, about 5 seconds) as a fourth column of Table 2; the text now
  treats it as the main interval and says the other three are not spatially corrected. Cited Zillow and ACS in Section 1, explained 1,082 vs 1,072,
  replaced the example-project sentence with Gelman and Hill, reworded the notebook claim, added a 2017 column to Table 1 and all four models to Table 6.
- Font audit: all text is Latin Modern; tables 9 pt unscaled; the only inconsistency was a few figure labels printing under 8 pt (now raised).
- `src/check_method_numbers.py` now has 47 checks (PASSED 47, FAILED 0). Not committed.

## 2026-10-21 later still: bootstrap interval types
- Reviewer found the exposure-model percentile bootstrap intervals are lopsided (long side away from zero, about 2:1). Confirmed. Added basic, symmetric and BCa intervals
  (`methods.exposure_block_bootstrap`); Table 2 now shows the bootstrap SE and the BCa interval, new Table 3 compares the four interval types.
  Percentile and BCa exclude zero in all four specs; symmetric includes zero for 2020-22; basic includes zero in all four (2023-25 only just). 2020-22 is not treated as firm.
- Event study: mildly lopsided with no consistent direction; main claims hold under basic and symmetric intervals, except Nashville 2025 and Tampa 2025 (borderline).
- `check_method_numbers.py`: 52 checks, FAILED 0. Not committed.

## 2026-10-21 final check before submission
- Full recomputation (`make_method_results.py`) reproduced all 14 saved tables exactly. Number check: 52 passed, 0 failed. Notebook re-executed clean (14 code cells, 0 errors, 4 figures).
- PDF: 13 pages, 0 errors, 0 overfull boxes, 0 undefined references, all 13 references cited, no em dashes, all text Latin Modern (tables 9 pt, captions 10 pt, body 10.9 pt).
- Last wording fixes: "pre-2020" hyphen in Table 4; two untested leakage explanations softened; Table 3 caption clarified.
- Submit: report/Team10_Methodology.pdf and notebooks/02_methods.ipynb (the .tex is optional). Not committed.
