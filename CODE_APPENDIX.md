# Code Appendix

This appendix identifies the code used to build the capstone analysis, figures, tables, and numerical checks. Raw Zillow downloads are not stored in the repository. Their source details are recorded in `docs/SOURCES.md`, and the raw files can be placed in `data/raw/` before running the pipeline.

## Reproduction sequence

1. Install the packages listed in `requirements.txt`.
2. Place the source files described in `docs/SOURCES.md` in `data/raw/`.
3. Set `CENSUS_API_KEY` for the Census API step.
4. Run `python src/run_pipeline.py` to rebuild the cleaned analysis files.
5. Run `python src/make_method_results.py` to estimate the event study, exposure models, prediction models, and clustering diagnostics.
6. Run `python src/make_figures.py` and `python src/make_method_figures.py` to rebuild the visualizations.
7. Run `python report/make_tables.py` and `python report/make_method_tables.py` to rebuild the LaTeX tables.
8. Run `python src/audit_checks.py`, `python src/check_report_numbers.py`, and `python src/check_method_numbers.py` to verify the numerical claims reported in the paper.

## File guide

| Project component | Main files | Purpose |
|---|---|---|
| Data preparation | `src/01_zhvi_panel.py` through `src/08_growth.py` | Clean Zillow and Census inputs, assign metros, calculate distances, add geographic boundaries, and construct growth outcomes. |
| Pipeline control | `src/run_pipeline.py`, `src/config.py` | Run the numbered preparation steps in a consistent order and store shared settings. |
| Exploratory analysis | `notebooks/01_eda.ipynb`, `src/viz_eda.py` | Produce descriptive statistics, coverage checks, maps, gradients, and exploratory comparisons. |
| Formal methods | `notebooks/02_methods.ipynb`, `src/methods.py`, `src/make_method_results.py` | Estimate the event study, work-from-home exposure models, spatial diagnostics, prediction models, and price-path clusters. |
| Figures | `src/make_figures.py`, `src/make_method_figures.py`, `src/viz.py`, `src/viz_methods.py` | Rebuild the figures from cleaned data and saved analytical outputs. |
| Tables | `report/make_tables.py`, `report/make_method_tables.py` | Convert saved results into the tables used by the LaTeX report. |
| Validation | `src/audit_checks.py`, `src/check_report_numbers.py`, `src/check_method_numbers.py` | Recompute reported values and flag inconsistencies between the analysis outputs and the report. |
| Data provenance | `docs/SOURCES.md` | Record the origin, vintage, and retrieval details for each input source. |

## Data and privacy notes

- `data/raw/` is excluded because it contains large third-party downloads that can be retrieved from the documented sources.
- `.env` files, API keys, and Python environment folders are excluded from version control.
- Clean analytical files are included so the reported results can be inspected without redistributing the complete raw downloads.
- All reported results are aggregated at the ZIP-code level. The project contains no individual-level or personally identifying data.

## Report connection

The paper's methods section describes the analytical design. This appendix provides the corresponding file-level map so that a reviewer can trace each reported result to the code that creates it.
