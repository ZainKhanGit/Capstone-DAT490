"""Redraw the methodology figures from the saved tables (no model refitting; seconds, not minutes).

    .venv/bin/python src/make_method_figures.py
"""
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from PIL import Image  # noqa: E402

import viz  # noqa: E402
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


save(VM.event_study_figure(pd.read_csv(T / "m_event_study.csv")), "m_1_event_study")
save(VM.ml_figure(pd.read_csv(T / "m_cv_scores.csv")), "m_2_ml_scores")
imps = {lab: pd.read_csv(T / f"m_perm_importance_{t}.csv")
        for t, lab in [("ann_cum_2019_2022_dm", "2020-22 growth"), ("ann_cum_2022_2025_dm", "2023-25 growth")]}
save(VM.importance_figure(imps), "m_3_importance")
save(VM.cluster_methods_figure(pd.read_csv(T / "m_cluster_methods.csv")), "m_4_cluster_methods")
print("figures redrawn")
