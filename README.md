# Remote Work and Urban Housing Prices - Team 10

Reproducible data pipeline, exploratory analysis, formal modeling, and written reports for the ASU DAT 490 capstone project. We ask whether the
flattening of the within-metro house-price gradient seen in 2020-22 persisted through 2025 in eight
Sun Belt metros (Atlanta, Austin, Charlotte, Dallas, Las Vegas, Nashville, Phoenix, and Tampa), using
ZIP-level Zillow prices and rents joined to Census data. The plan and literature review are in `docs/`.

See [`CODE_APPENDIX.md`](CODE_APPENDIX.md) for the reproduction sequence and a file-by-file map from the paper to the analysis code.

## Current deliverables

- [`report/Team10_Rough_Draft.pdf`](report/Team10_Rough_Draft.pdf): complete capstone rough draft
- [`report/Team10_Rough_Draft.tex`](report/Team10_Rough_Draft.tex): editable LaTeX source
- [`report/Team10_Methodology.pdf`](report/Team10_Methodology.pdf): earlier methodology submission
- [`notebooks/01_eda.ipynb`](notebooks/01_eda.ipynb): exploratory analysis notebook
- [`notebooks/02_methods.ipynb`](notebooks/02_methods.ipynb): formal analysis notebook

The root `main.tex` file is the original team template retained from the repository setup. The current paper is the rough-draft file in `report/`.

## Folder map

| Folder | What is in it |
|---|---|
| `src/` | The pipeline: eight numbered steps, `config.py`, and `run_pipeline.py` |
| `notebooks/` | Exploratory and formal methods notebooks |
| `data/raw/` | Downloaded inputs (not in git; see `docs/SOURCES.md`) |
| `data/reference/` | Hand-compiled city-hall coordinates, with a source for each |
| `data/clean/` | Pipeline outputs (rebuilt by the pipeline) |
| `outputs/` | Data-quality logs, saved model results, tables, and full-resolution figures |
| `report/` | Current and prior reports, LaTeX tables, and report-ready figures |
| `docs/` | Project plan, literature review, `SOURCES.md` (provenance of every file), `STATUS.md` (where we left off, next steps) |

## Set up

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m ipykernel install --prefix .venv --name capstone --display-name "Python 3 (capstone venv)"
```

The pipeline downloads nothing except the ACS tables. Put the other raw files in `data/raw/` yourself,
using the URLs in `docs/SOURCES.md` (the ZHVI csv comes from Zillow Research's data page: ZHVI, ZIP code,
all homes, mid-tier, smoothed, seasonally adjusted). The ACS step calls the Census API and needs a free key
in an environment variable:

```bash
export CENSUS_API_KEY="your key"   # never commit it; request one at https://api.census.gov/data/key_signup.html
```

## Run

```bash
.venv/bin/python src/run_pipeline.py            # all steps, about 20 seconds once raw data is in place
.venv/bin/python src/run_pipeline.py --list     # what each step does
.venv/bin/python src/run_pipeline.py --from 4   # from step 4 onward
```

Then open `notebooks/01_eda.ipynb` and pick the "Python 3 (capstone venv)" kernel.

## Build the reports

The current capstone paper is `report/Team10_Rough_Draft.pdf`, with source in `report/Team10_Rough_Draft.tex`. Figures in
`report/figures/` are report-ready copies of the full-resolution graphics in `outputs/figures/`. To rebuild the analytical outputs:

```bash
python src/audit_checks.py
python src/make_method_results.py
python src/make_figures.py
python src/make_method_figures.py
python report/make_tables.py
python report/make_method_tables.py
cd report && xelatex Team10_Rough_Draft.tex && xelatex Team10_Rough_Draft.tex
```

Before submitting, `src/check_report_numbers.py` and `src/check_method_numbers.py` recompute the report's audited numerical claims.
`docs/interpretation_audit.md` preserves the earlier EDA interpretation audit; the current rough draft supersedes its proposed wording.

## Fonts

The report is set in Latin Modern (body 10.9 pt, captions 10 pt, tables 9 pt, headings 12 to 17 pt). Figures are drawn in Latin Modern
Roman too (read from the TinyTeX fonts, with a DejaVu Serif fallback; sizes are scaled in `src/viz.py` by `TEXT_SCALE`), so figure
text matches the page. All tables use one size and are not scaled to fit.

## Methodology submission (second assignment)

`report/Team10_Methodology.pdf` describes the planned methods with first results; `notebooks/02_methods.ipynb` reproduces them
(code in `src/methods.py`). Regenerate with `.venv/bin/python src/make_method_results.py` (about 10 minutes), then
`.venv/bin/python report/make_method_tables.py` and `xelatex` twice in `report/`. `src/check_method_numbers.py` must report FAILED 0.
