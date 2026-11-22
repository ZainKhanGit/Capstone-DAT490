"""Figures for the methodology submission. Same style, fonts and palette as the EDA figures (viz.py)."""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import viz
from viz import BLUE_700, C1, C2, FIG_W, INK, METRO_ORDER, fs

GREY = "#898781"


def event_study_figure(tab: pd.DataFrame):
    """3 x 3 grid: all eight metros pooled (within-metro), then each metro. Line = gradient coefficient by year, relative to
    Dec 2019 (so 2019 is zero by construction). Shaded = spatial block-bootstrap 95% interval. Dashed = the ordinary interval."""
    fig, axes = plt.subplots(3, 3, figsize=(FIG_W, 8.2), sharex=True)
    scopes = ["All eight (within-metro)"] + METRO_ORDER
    for ax, s in zip(axes.ravel(), scopes):
        t = tab[tab["scope"] == s].sort_values("year")
        ax.axhline(0, color=INK["axis"], lw=1.0)
        ax.axvline(2019, color=INK["axis"], lw=1.0, ls=(0, (3, 3)))
        ax.axvspan(2020 - 0.5, 2022 + 0.5, color="#f1efe6", zorder=0)
        ax.fill_between(t["year"], t["boot_lo"], t["boot_hi"], color=C1, alpha=0.18, linewidth=0, zorder=2)
        ax.plot(t["year"], t["naive_lo"], color=C2, lw=1.0, ls=(0, (4, 2)), zorder=3)
        ax.plot(t["year"], t["naive_hi"], color=C2, lw=1.0, ls=(0, (4, 2)), zorder=3)
        ax.plot(t["year"], t["beta"], color=BLUE_700, lw=2.0, marker="o", markersize=5, markerfacecolor=BLUE_700,
                markeredgecolor=INK["surface"], markeredgewidth=1.0, zorder=5)
        viz._heading(ax, "All eight (within-metro)" if s.startswith("All") else s, f"{int(t['n'].iloc[0])} ZIPs")
        ax.set_xticks([2017, 2019, 2021, 2023, 2025])
        ax.tick_params(labelsize=fs(9.5))
    for ax in axes[:, 0]:
        ax.set_ylabel("% per 10 mi out")
    fig.subplots_adjust(hspace=0.62, wspace=0.28, top=0.815, bottom=0.07, left=0.075, right=0.985)
    fig.text(0.075, 0.992, "Gradient coefficient by year, relative to December 2019", ha="left", va="top", fontsize=viz.FS["sup"], fontweight="bold")
    fig.text(0.075, 0.9, "Blue band: spatial block-bootstrap 95% interval. Orange dashes: ordinary interval that treats ZIPs as independent.\n"
             "Shaded years: 2020-22. Above zero = farther ZIPs gained more than closer ZIPs since 2019.",
             fontsize=fs(9.5), color=INK["secondary"], va="bottom", linespacing=1.3)
    return fig


def ml_figure(scores: pd.DataFrame):
    """Top row: each model on feature set D, out-of-sample R2 for leave-one-metro-out (filled) and random 5-fold (hollow).
    Bottom row: leave-one-metro-out R2 as feature sets grow (A to D), random forest and ridge."""
    targets = [("ann_cum_2019_2022_dm", "2020-22 growth"), ("ann_cum_2022_2025_dm", "2023-25 growth")]
    fig, axes = plt.subplots(2, 2, figsize=(FIG_W, 6.6))
    models = ["Ridge", "Lasso", "Random forest", "Gradient boosting"]
    for j, (tg, lab) in enumerate(targets):
        s = scores[(scores["target"] == tg)]
        ax = axes[0, j]
        d = s[s["features"].str.startswith("D")].set_index("model").loc[models]
        y = np.arange(len(models))[::-1]
        ax.hlines(y, d["R2_leave_one_metro_out"], d["R2_random_5fold"], color=INK["axis"], lw=1.5, zorder=1)
        ax.scatter(d["R2_random_5fold"], y, s=70, facecolors="none", edgecolors=C2, linewidths=1.8, zorder=3, label="random 5-fold")
        ax.scatter(d["R2_leave_one_metro_out"], y, s=70, color=C1, edgecolors=INK["surface"], linewidths=1.2, zorder=4,
                   label="leave one metro out")
        ax.axvline(0, color=INK["axis"], lw=1.0)
        ax.set_yticks(y)
        ax.set_yticklabels(models)
        ax.set_xlim(-0.05, 0.55)
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", visible=True)
        ax.set_xlabel("Out-of-sample R²")
        viz._heading(ax, lab, "All features (set D)")
        if j == 0:
            ax.legend(loc="upper left", bbox_to_anchor=(0.0, -0.28), ncol=2, frameon=False, fontsize=fs(9.5))
        ax = axes[1, j]
        for m, col, mk in [("Random forest", C1, "o"), ("Ridge", C2, "s")]:
            q = s[s["model"] == m].sort_values("features")
            ax.plot(range(4), q["R2_leave_one_metro_out"], color=col, lw=2.0, marker=mk, markersize=7, markerfacecolor=col,
                    markeredgecolor=INK["surface"], markeredgewidth=1.2, label=m)
        ax.axhline(0, color=INK["axis"], lw=1.0)
        ax.set_xticks(range(4))
        ax.set_xticklabels(["A\nplace,\nhousing", "B\n+ income,\njobs", "C\n+ WFH\nshare", "D\n+ pre-\n2020 growth"], fontsize=fs(9.5))
        ax.set_ylabel("R², leave one metro out")
        ax.set_ylim(-0.02, 0.34)
        ax.set_xlim(-0.35, 3.35)
        viz._heading(ax, lab, "Adding features, in order")
        if j == 1:
            ax.legend(loc="upper right", frameon=False, fontsize=fs(9.5))
    fig.subplots_adjust(hspace=0.95, wspace=0.6, top=0.925, bottom=0.12, left=0.19, right=0.975)
    return fig


def importance_figure(imp: dict):
    """Permutation importance of the random forest on held-out metros. Bar = mean across the eight held-out metros; whiskers = range."""
    fig, axes = plt.subplots(2, 1, figsize=(FIG_W, 6.6))
    for ax, (lab, d) in zip(axes, imp.items()):
        g = d.groupby("feature")["importance"].agg(["mean", "min", "max"]).sort_values("mean")
        y = np.arange(len(g))
        ax.barh(y, g["mean"], color=C1, height=0.62, zorder=3)
        ax.hlines(y, g["min"], g["max"], color=INK["primary"], lw=1.1, zorder=4)
        ax.set_yticks(y)
        ax.set_yticklabels([viz_names(f) for f in g.index], fontsize=fs(9.8))
        ax.axvline(0, color=INK["axis"], lw=1.0)
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", visible=True)
        ax.set_xlabel("Increase in squared error when the feature is shuffled")
        viz._heading(ax, lab, "Random forest, scored on held-out metros")
    fig.subplots_adjust(hspace=0.75, top=0.91, bottom=0.08, left=0.36, right=0.975)
    return fig


def viz_names(f):
    import methods
    return methods.NICE.get(f, f)


def cluster_methods_figure(t: pd.DataFrame):
    """Left: silhouette by number of groups for three methods. Right: Gaussian-mixture BIC (lower is better)."""
    fig, axes = plt.subplots(1, 2, figsize=(FIG_W, 3.6))
    ax = axes[0]
    style = {"k-means": (C1, "o", "-"), "Ward hierarchical": (C2, "s", "-"), "Gaussian mixture": (GREY, "^", (0, (4, 2)))}
    for m, (col, mk, ls) in style.items():
        q = t[t["method"] == m]
        ax.plot(q["k"], q["silhouette"], color=col, lw=2.0, ls=ls, marker=mk, markersize=6.5, markerfacecolor=col,
                markeredgecolor=INK["surface"], markeredgewidth=1.0, label=m)
    ax.axhline(0.25, color=INK["axis"], lw=1.0)
    ax.text(2.02, 0.255, "0.25: weak below", fontsize=fs(9.5), color=INK["secondary"], va="bottom")
    ax.set_xlabel("Number of groups (k)")
    ax.set_ylabel("Silhouette width")
    ax.set_ylim(-0.05, 0.6)
    ax.legend(loc="upper right", frameon=False, fontsize=fs(9.5))
    viz._heading(ax, "How distinct are the groups?", "Same price paths, three methods")
    ax = axes[1]
    q = t[t["method"] == "Gaussian mixture"]
    ax.plot(q["k"], q["BIC"], color=BLUE_700, lw=2.0, marker="o", markersize=6.5, markerfacecolor=BLUE_700,
            markeredgecolor=INK["surface"], markeredgewidth=1.0)
    ax.set_xlabel("Number of groups (k)")
    ax.set_ylabel("BIC (lower is better)")
    viz._heading(ax, "Gaussian mixture fit", "On the first five principal components")
    fig.subplots_adjust(wspace=0.32, top=0.82, bottom=0.17, left=0.09, right=0.985)
    return fig
