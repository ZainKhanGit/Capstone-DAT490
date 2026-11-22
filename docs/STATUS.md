# Project Status

Updated November 21, 2026.

## Current deliverable

The capstone rough draft is complete and stored in:

- `report/Team10_Rough_Draft.pdf`
- `report/Team10_Rough_Draft.tex`

The paper is 40 pages. It contains the abstract, introduction, prior research, data preparation, exploratory analysis, methods, results, discussion, ethical and equity considerations, limitations and future research, conclusion, supplemental evidence, two-center robustness, code appendix, and references.

The earlier EDA and methodology submissions remain in `report/` as project history. The current submission is the rough draft.

## Analytical scope

The project studies 1,082 ZIP codes across Atlanta, Austin, Charlotte, Dallas, Las Vegas, Nashville, Phoenix, and Tampa. It combines Zillow home-value and rent indexes with Census geography and pre-pandemic American Community Survey characteristics.

The formal event-study, exposure, and prediction models use distance to the nearer named city hall in Dallas-Fort Worth and Tampa-St. Petersburg. Exploratory slopes begin with the first-named city hall and include separate two-center checks so center-dependent conclusions are visible.

The main conclusion is heterogeneous rather than universal: the pooled housing-price gradient moved outward after 2019, but Atlanta accounts for much of the late-period result and the metro-specific patterns differ substantially. Pre-pandemic work-from-home share does not provide a stable, portable explanation after controls and geographic validation. Price paths show meaningful continuous variation but weak evidence for sharply separated natural groups.

## Reproducibility

The numbered pipeline is in `src/01_zhvi_panel.py` through `src/08_growth.py`. Formal models are implemented in `src/methods.py` and orchestrated by `src/make_method_results.py`. The two notebooks are:

- `notebooks/01_eda.ipynb`
- `notebooks/02_methods.ipynb`

`CODE_APPENDIX.md` provides the full reproduction sequence and a file-level guide. `docs/SOURCES.md` records the provenance of every external input.

Raw Zillow downloads are not tracked. They can be restored from the documented sources. Census API access requires `CENSUS_API_KEY`; the key itself is never stored in the repository.

## Validation state

- The final PDF compiles to 40 pages with no overfull boxes, missing files, undefined references, or fatal errors.
- The paper source contains no en dashes or em dashes.
- Metro displays use alphabetical order, and time-period panels progress chronologically.
- Tables and figures are generated from saved analytical outputs rather than manually re-entered values.
- Numerical audit scripts are stored in `src/audit_checks.py`, `src/check_report_numbers.py`, and `src/check_method_numbers.py`.
- The team repository is connected at `https://github.com/ZainKhanGit/Capstone-DAT490`.

## Remaining administrative step

The repository owner needs to make the repository public, or explicitly grant the instructor access, so the Code Appendix link can be opened outside the team accounts.
