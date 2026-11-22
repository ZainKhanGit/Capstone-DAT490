"""Run every preliminary analysis for the methodology submission and save tables and figures.

    .venv/bin/python src/make_method_results.py          # about 10 minutes (the cross-validation dominates)

Tables go to outputs/tables/m_*.csv, figures to outputs/figures/m_*.png, report copies to report/figures/m_*.jpg.
The notebook (notebooks/02_methods.ipynb) calls the same functions in methods.py.
"""
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from PIL import Image  # noqa: E402

import methods as M  # noqa: E402
import viz  # noqa: E402
import viz_eda  # noqa: E402
import viz_methods as VM  # noqa: E402

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
F, T, R = ROOT / "outputs" / "figures", ROOT / "outputs" / "tables", ROOT / "report" / "figures"
viz.set_style()


def save(fig, name):
    fig.savefig(F / f"{name}.png")
    plt.close(fig)
    im = Image.open(F / f"{name}.png").convert("RGB")
    if im.width > 1800:
        im = im.resize((1800, round(im.height * 1800 / im.width)), Image.LANCZOS)
    im.save(R / f"{name}.jpg", quality=90, optimize=True, subsampling=0)


gd, xd = M.load()

# 1. event study
tab, summ = M.event_study(gd, B=1000)
tab.to_csv(T / "m_event_study.csv", index=False)
summ.to_csv(T / "m_event_summary.csv", index=False)
save(VM.event_study_figure(tab), "m_1_event_study")

# 2. mixed model
M.mixed_model(xd).to_csv(T / "m_mixed_model.csv", index=False)

# 3. Moran's I
M.moran(xd, perms=999).to_csv(T / "m_moran.csv", index=False)

# 4. supervised, leave one metro out
x = M.ml_data(xd)
scores, imps, lasso = [], {}, {}
for target, lab in [("ann_cum_2019_2022_dm", "2020-22 growth"), ("ann_cum_2022_2025_dm", "2023-25 growth")]:
    s, imp, _ = M.ml_cv(x, target, perm_set="D. C + pre-2020 growth")
    scores.append(s)
    s.to_csv(T / f"m_cv_scores_{target}.csv", index=False)       # saved as soon as it is done
    imps[lab] = imp
    imp.assign(target=target).to_csv(T / f"m_perm_importance_{target}.csv", index=False)
    lasso[lab] = M.lasso_selection(x, target, "D. C + pre-2020 growth")
scores = pd.concat(scores)
scores.to_csv(T / "m_cv_scores.csv", index=False)
pd.DataFrame(lasso).to_csv(T / "m_lasso_selection.csv")
pd.DataFrame({"n_zips": [len(x)], "n_metros": [x["metro_short"].nunique()]}).to_csv(T / "m_ml_sample.csv", index=False)
save(VM.ml_figure(scores), "m_2_ml_scores")
save(VM.importance_figure(imps), "m_3_importance")

# 5. clustering methods
panel = pd.read_parquet(ROOT / "data" / "clean" / "zhvi_analysis_panel.parquet", columns=["zip", "date", "index_dec2019"])
P = viz_eda.path_matrix(panel, gd)
ct, ari, evr = M.cluster_methods(P)
ct.to_csv(T / "m_cluster_methods.csv", index=False)
ari.to_csv(T / "m_cluster_ari.csv", index=False)
pd.Series(evr, name="explained_variance_ratio").to_csv(T / "m_cluster_pca_variance.csv", index=False)
save(VM.cluster_methods_figure(ct), "m_4_cluster_methods")
print("done")
