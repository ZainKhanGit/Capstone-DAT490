"""Figure builders for EDA sections 2.1 (distributions), 2.3 (maps) and 2.4 (exposure).

Builds on the style, palette and helpers in viz.py (import viz first and call viz.set_style()).
"""
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, Normalize, TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
from scipy import stats

import viz
from viz import (BLUE_700, C1, C2, GROWTH, INK, LEVEL_DATES, METRO_ORDER, MINUS, ORDINAL, TWO_CENTER,
                 _heading, _level_axis, _money, _pct_axis, _robust_limits, _sample, signed)

SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]  # steps 100..700
DIVERGING = ["#2a78d6", "#f0efec", "#e34948"]   # blue pole, neutral gray midpoint, red pole (warm = above)


# ============================================================================== 2.1 distributions
def _grouped_box(ax, groups, colors, labels, width=0.2, gap=0.24):
    """groups[metro_index][series_index] -> array. One dodged box per (metro, series)."""
    for si, color in enumerate(colors):
        pos, data = [], []
        for mi, series in enumerate(groups):
            x = np.asarray(series[si], float)
            x = x[np.isfinite(x)]
            if len(x):
                pos.append(mi + (si - (len(colors) - 1) / 2) * gap)
                data.append(x)
        bp = ax.boxplot(data, positions=pos, widths=width, patch_artist=True, showfliers=True, whis=1.5,
                        medianprops={"color": INK["surface"], "linewidth": 1.6},
                        whiskerprops={"color": color, "linewidth": 1.2}, capprops={"linewidth": 0},
                        boxprops={"linewidth": 0},
                        flierprops={"marker": "o", "markersize": 3, "markerfacecolor": color,
                                    "markeredgewidth": 0, "alpha": 0.55})
        for box in bp["boxes"]:
            box.set_facecolor(color)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(labels)
    ax.grid(axis="x", visible=False)


def distributions(d: pd.DataFrame):
    """Figure 2.1a: home value (log scale) at three dates and annualized growth in three periods, by metro.
    Box = middle 50% of ZIPs, white line = median, whiskers = 1.5 x IQR, dots = ZIPs beyond the whiskers."""
    samples = {m: _sample(d, m)[0] for m in METRO_ORDER}
    fig, axes = plt.subplots(2, 1, figsize=(12.2, 8.6))
    lv_cols = [f"level_{lab}" for _, lab in LEVEL_DATES]
    allv = pd.concat([s[lv_cols] for s in samples.values()])
    _grouped_box(axes[0], [[s[c] for c in lv_cols] for s in samples.values()], ORDINAL, METRO_ORDER)
    _level_axis(axes[0], allv.min().min() * 0.9, allv.max().max() * 1.1)
    axes[0].set_ylabel("Home value (ZHVI, log scale)")
    _heading(axes[0], "Home values", "Each box summarizes the ZIPs of one metro at one date; the same ZIPs appear at all three dates.")
    gr_cols = [f"ann_{c}" for c in GROWTH]
    allg = pd.concat([s[gr_cols] for s in samples.values()])
    _grouped_box(axes[1], [[s[c] for c in gr_cols] for s in samples.values()], ORDINAL, METRO_ORDER)
    # axis spans every whisker (not the extreme dots), so no box is clipped
    from matplotlib.cbook import boxplot_stats
    whis = [boxplot_stats(s_[c].dropna().to_numpy(), whis=1.5)[0] for s_ in samples.values() for c in gr_cols]
    lo, hi = min(w["whislo"] for w in whis) - 1.0, max(w["whishi"] for w in whis) + 1.0
    axes[1].set_ylim(lo, hi)
    _pct_axis(axes[1])
    axes[1].axhline(0, color=INK["axis"], lw=1.0, zorder=1)
    axes[1].set_ylabel("Annualized growth in home value")
    off = int(((allg < lo) | (allg > hi)).to_numpy().sum())
    _heading(axes[1], "Growth", "Annualized so the 2-year and 3-year periods compare."
             + (f" {off} extreme ZIP-period values beyond the whiskers' range are not drawn." if off else ""))
    for ax, labs in ((axes[0], [l for _, l in LEVEL_DATES]), (axes[1], [v[3] for v in GROWTH.values()])):
        h = [Line2D([0], [0], marker="s", ls="", color=c, markersize=9, label=l) for c, l in zip(ORDINAL, labs)]
        ax.legend(handles=h, loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=3, frameon=False,
                  handletextpad=0.3, columnspacing=1.4)
    fig.suptitle("Distributions of home values and growth by metro", x=0.012, y=0.995, ha="left",
                 fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.96), h_pad=2.8)
    return fig


def log_check(d: pd.DataFrame):
    """Figure 2.1b: is a log transform warranted? Dec 2019 home values on a linear and a log axis."""
    v = d["level_Dec 2019"].dropna()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.4))
    s1, s2 = stats.skew(v), stats.skew(np.log(v))
    axes[0].hist(v / 1e3, bins=45, color=C1, alpha=0.85, edgecolor=INK["surface"], linewidth=0.8)
    axes[0].set_xlabel("Home value, Dec 2019 ($ thousands)")
    _heading(axes[0], "Dollars", f"Skewness {s1:.2f}: a long right tail of expensive ZIPs")
    axes[1].hist(np.log10(v), bins=45, color=C1, alpha=0.85, edgecolor=INK["surface"], linewidth=0.8)
    ticks = [5.0, 5.3, 5.6, 5.9, 6.2]
    axes[1].set_xticks(ticks)
    axes[1].set_xticklabels([_money(10 ** t, None) for t in ticks])
    axes[1].set_xlabel("Home value, Dec 2019 (log scale)")
    _heading(axes[1], "Logs", f"Skewness {s2:.2f}: close to symmetric")
    for ax in axes:
        ax.set_ylabel("Number of ZIP codes")
        ax.grid(axis="x", visible=False)
    fig.suptitle(f"Why we use a log scale for prices ({len(v):,} ZIP codes, all eight metros)", x=0.012, y=0.995,
                 ha="left", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    return fig


FLAG_LABELS = {
    "zhvi_incomplete": "ZHVI series incomplete, 2018–2025",
    "metro_col_only": "Metro column only (not in county crosswalk)",
    "acs_baseline_missing": "No 2015–2019 ACS row",
    "wfh_unreliable": "Work-from-home share unreliable",
    "zori_missing": "No ZORI (rents) at all",
    "zori_incomplete": "ZORI present but patchy",
}


def flags_by_distance(flags: pd.DataFrame):
    """Figure 2.1c: share of ZIPs carrying each data-quality flag, by distance band (the figure behind Section 1)."""
    bands = ["0-10 mi", "10-20 mi", "20-30 mi", "30+ mi"]
    f = flags.copy()
    f["dist_band"] = pd.Categorical(f["dist_band"], categories=bands, ordered=True)
    m = (f.groupby("dist_band", observed=False)[list(FLAG_LABELS)].mean() * 100).T
    m["All ZIPs"] = f[list(FLAG_LABELS)].mean() * 100
    n = f.groupby("dist_band", observed=False).size().tolist() + [len(f)]
    cmap = LinearSegmentedColormap.from_list("seq", SEQ_BLUE)
    fig, ax = plt.subplots(figsize=(11.2, 4.9))
    norm = Normalize(0, 70)
    ax.imshow(m.to_numpy(), cmap=cmap, norm=norm, aspect="auto")
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            val = m.iat[i, j]
            ax.text(j, i, f"{val:.0f}%" if val >= 0.5 else "0%", ha="center", va="center", fontsize=11,
                    color="white" if norm(val) > 0.45 else INK["primary"])
    ax.set_xticks(range(m.shape[1]))
    ax.set_xticklabels([f"{c}\n(n = {k:,})" for c, k in zip(m.columns, n)])
    ax.set_yticks(range(m.shape[0]))
    ax.set_yticklabels([FLAG_LABELS[i] for i in m.index])
    ax.xaxis.tick_top()
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.axvline(3.5, color=INK["surface"], lw=5)
    ax.tick_params(length=0)
    fig.suptitle("Most data-quality problems are more common far from the center", x=0.012, y=0.985, ha="left",
                 fontsize=14, fontweight="bold")
    fig.text(0.012, 0.915, "Share of ZIP codes in each distance band (city-hall distance) with each flag. Darker = more ZIPs. "
             "The one exception, missing 2015–2019 ACS rows, is small and not tied to distance.",
             fontsize=9.2, color=INK["secondary"], ha="left", va="top", wrap=True)
    fig.tight_layout(rect=(0, 0, 1, 0.87))
    return fig


# ============================================================================== 2.3 maps
def _albers(gdf):
    return gdf.to_crs(5070)


def _centers_albers(ref: pd.DataFrame, metro: str):
    r = ref[ref["metro"] == metro]
    pts = gpd.GeoSeries(gpd.points_from_xy(r["lon"], r["lat"]), crs=4326).to_crs(5070)
    return pts


def _scalebar(ax, miles=20):
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    L = miles * 1609.344
    x, y = x0 + 0.03 * (x1 - x0), y0 + 0.035 * (y1 - y0)
    ax.plot([x, x + L], [y, y], color=INK["primary"], lw=2.2, solid_capstyle="butt", zorder=9)
    ax.text(x + L / 2, y + 0.012 * (y1 - y0), f"{miles} mi", ha="center", va="bottom", fontsize=8.5, color=INK["secondary"])


def relative_growth(d: pd.DataFrame) -> pd.DataFrame:
    """Annualized growth minus the metro's median, per period (points per year)."""
    out = d[["zip", "metro_short"]].copy()
    for col in GROWTH:
        a = d[f"ann_{col}"]
        out[f"rel_{col}"] = a - a.groupby(d["metro_short"]).transform("median")
    return out


def growth_limit(rel: pd.DataFrame) -> float:
    v = rel[[f"rel_{c}" for c in GROWTH]].abs().to_numpy().ravel()
    return float(np.ceil(np.nanpercentile(v, 90) * 2) / 2)


def growth_maps(zc: gpd.GeoDataFrame, rel: pd.DataFrame, ref: pd.DataFrame, metro: str, lim: float):
    """One metro, three periods: ZIP-level annualized growth relative to the metro median. One diverging
    scale shared by every metro and period (grey midpoint = at the metro median; warm = faster)."""
    g = _albers(zc.merge(rel, on="zip"))
    g = g[g["metro_short"] == metro]
    cmap = LinearSegmentedColormap.from_list("div", DIVERGING)
    norm = TwoSlopeNorm(vcenter=0, vmin=-lim, vmax=lim)
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 5.3))
    xmin, ymin, xmax, ymax = g.total_bounds
    pad = 0.03 * max(xmax - xmin, ymax - ymin)
    cen = _centers_albers(ref, metro)
    for ax, (col, (a, b, _, name)) in zip(axes, GROWTH.items()):
        c = f"rel_{col}"
        g[g[c].isna()].plot(ax=ax, color=INK["grid"], edgecolor=INK["surface"], linewidth=0.3)
        g[g[c].notna()].plot(ax=ax, column=c, cmap=cmap, norm=norm, edgecolor=INK["surface"], linewidth=0.3)
        ax.scatter(cen.x, cen.y, marker="*", s=170, color=INK["primary"], edgecolors=INK["surface"],
                   linewidths=1.2, zorder=10)
        ax.set_xlim(xmin - pad, xmax + pad)
        ax.set_ylim(ymin - 0.09 * max(xmax - xmin, ymax - ymin), ymax + pad)   # free band for the scale bar
        ax.set_aspect("equal")
        ax.set_anchor("NW")
        ax.set_axis_off()
        _scalebar(ax)
        ax.set_title(f"{name}  (Dec {a} \u2192 Dec {b})", loc="left", fontsize=11.5, fontweight="bold")
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    cb = fig.colorbar(sm, ax=axes, orientation="horizontal", fraction=0.05, pad=0.04, extend="both", aspect=45)
    cb.set_label("Annualized growth relative to the metro median (points per year); warm = faster, cool = slower", fontsize=9.5)
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=0, labelsize=9.5)
    cb.ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: signed(v, 0) if v else "0"))
    n_missing = int(g[[f"rel_{c}" for c in GROWTH]].isna().any(axis=1).sum())
    stars = "Black star = city hall" if metro not in TWO_CENTER else "Black stars = the two city halls"
    fig.suptitle(f"{metro}: where growth ran ahead of or behind the metro as a whole", x=0.012, y=0.985, ha="left",
                 fontsize=14, fontweight="bold")
    fig.text(0.012, 0.915, f"{stars}. Grey = a ZIP in our set with no data ({n_missing}); white = not in our ZIP set. The same color scale "
             f"is used for all eight metros and all three periods (clipped at \u00b1{lim:g} points per year).", fontsize=9.2,
             color=INK["secondary"], ha="left", va="top")
    fig.subplots_adjust(top=0.84, bottom=0.2, left=0.01, right=0.99, wspace=0.04)
    return fig


def level_quintile_maps(zc: gpd.GeoDataFrame, d: pd.DataFrame, ref: pd.DataFrame):
    """Figure 2.3b: Dec 2019 home value as within-metro fifths, all eight metros. A monocentric metro should show
    rings around the star; a polycentric one, separate patches."""
    classes = ["#cde2fb", "#6da7ec", "#2a78d6", "#184f95", "#0d366b"]   # steps 100, 300, 450, 600, 700
    fig, axes = plt.subplots(2, 4, figsize=(12.2, 7.4))
    for ax, metro in zip(axes.ravel(), METRO_ORDER):
        g = _albers(zc.merge(d[["zip", "metro_short", "level_Dec 2019"]], on="zip"))
        g = g[g["metro_short"] == metro].copy()
        g["q"] = pd.qcut(g["level_Dec 2019"], 5, labels=False)
        g[g["q"].isna()].plot(ax=ax, color=INK["grid"], edgecolor=INK["surface"], linewidth=0.3)
        for k, col in enumerate(classes):
            g[g["q"] == k].plot(ax=ax, color=col, edgecolor=INK["surface"], linewidth=0.3)
        cen = _centers_albers(ref, metro)
        ax.scatter(cen.x, cen.y, marker="*", s=110, color="#e34948", edgecolors=INK["surface"], linewidths=1.0, zorder=10)
        xmin, ymin, xmax, ymax = g.total_bounds
        pad = 0.03 * max(xmax - xmin, ymax - ymin)
        ax.set_xlim(xmin - pad, xmax + pad)
        ax.set_ylim(ymin - 0.09 * max(xmax - xmin, ymax - ymin), ymax + pad)
        ax.set_aspect("equal")
        ax.set_anchor("NW")
        ax.set_axis_off()
        _scalebar(ax, 20 if max(xmax - xmin, ymax - ymin) < 150 * 1609 else 40)
        ax.set_title(metro, loc="left", fontsize=11.5, fontweight="bold")
    h = [plt.Rectangle((0, 0), 1, 1, color=c) for c in classes]
    fig.legend(h, ["Lowest fifth", "2nd", "3rd", "4th", "Highest fifth"], loc="lower center", ncol=5, frameon=False,
               title="Dec 2019 home value, ranked within each metro's ZIPs", title_fontsize=10, handlelength=1.4)
    fig.suptitle("Where the expensive ZIPs are: a ring around the center, or separate patches?", x=0.012, y=0.992,
                 ha="left", fontsize=14, fontweight="bold")
    fig.text(0.012, 0.945, "Red star = city hall (two stars in Dallas\u2013Fort Worth and Tampa\u2013St. Petersburg). Fifths are within "
             "each metro, so colors compare places inside a metro, not prices across metros. Grey = no data; white = not "
             "in our ZIP set. Scale bars: 20 mi (40 mi in the largest metro).", fontsize=9.2, color=INK["secondary"], ha="left", va="top", wrap=True)
    fig.tight_layout(rect=(0, 0.08, 1, 0.92))
    return fig


# ============================================================================== 2.4 exposure (SQ2)
ACS_COLS = ["wfh_share_2019", "wfh_unreliable_2019", "median_hh_income_2019", "occ_mgmt_biz_sci_arts_share_2019",
            "sf_detached_share_2019", "units_20plus_share_2019", "pop_2019"]


def exposure_data(d: pd.DataFrame, acs: pd.DataFrame) -> pd.DataFrame:
    """ZIPs with data at every date (same sample as 2.2) and a 2015-2019 work-from-home share. Adds the
    within-metro (demeaned) share and growth, which remove differences between metros."""
    x = d[d["balanced"]].merge(acs[["zip"] + ACS_COLS], on="zip", how="left")
    x = x[x["wfh_share_2019"].notna()].copy()
    x["wfh_pct"] = 100 * x["wfh_share_2019"]
    x["unreliable"] = x["wfh_unreliable_2019"].fillna(False).astype(bool)
    x["wfh_pct_dm"] = x["wfh_pct"] - x.groupby("metro_short")["wfh_pct"].transform("median")
    for col in GROWTH:
        a = f"ann_{col}"
        x[f"{a}_dm"] = x[a] - x.groupby("metro_short")[a].transform("median")
    x["log_income"] = np.log(x["median_hh_income_2019"].where(x["median_hh_income_2019"] > 0))
    return x


def _scatter_exposure(ax, x, y, unrel, xlim, ylim):
    x, y, unrel = np.asarray(x, float), np.asarray(y, float), np.asarray(unrel, bool)
    ins = (x >= xlim[0]) & (x <= xlim[1]) & (y >= ylim[0]) & (y <= ylim[1])
    k = ins & ~unrel
    ax.scatter(x[k], y[k], s=20, color=C1, alpha=0.5, linewidths=0, zorder=2)
    k = ins & unrel
    ax.scatter(x[k], y[k], s=30, marker="D", facecolors="none", edgecolors=C1, linewidths=1.1, alpha=0.9, zorder=2)
    return int((~ins).sum())


def _binned(ax, x, y, nbins=8):
    df = pd.DataFrame({"x": x, "y": y}).dropna()
    df["b"] = pd.qcut(df["x"], nbins, duplicates="drop")
    g = df.groupby("b", observed=True).agg(x=("x", "mean"), y=("y", "mean"), se=("y", "sem"), n=("y", "size"))
    ax.errorbar(g["x"], g["y"], yerr=1.96 * g["se"], fmt="none", ecolor=BLUE_700, elinewidth=1.4, capsize=0, zorder=6)
    ax.scatter(g["x"], g["y"], s=52, color=BLUE_700, edgecolors=INK["surface"], linewidths=1.5, zorder=7)


def exposure_scatter(x: pd.DataFrame):
    """Figure 2.4a. Rows: within-metro (share and growth both measured against the metro median) and pooled raw.
    Columns: pre-2020 (a check: exposure should not predict growth before it mattered), 2020-22, 2023-25.
    Hollow diamonds = ZIPs whose 2015-2019 work-from-home share is unreliable (margin of error over half the estimate)."""
    fig, axes = plt.subplots(2, 3, figsize=(12.2, 8.6))
    rows = [("wfh_pct_dm", "_dm", "Within metro: work-from-home share minus the metro median (percentage points)",
             "Growth minus the metro median (points per year)"),
            ("wfh_pct", "", "Work-from-home share of workers, 2015–2019 (%)", "Annualized growth in home value")]
    out = []
    for r, (xc, suf, xlabel, ylabel) in enumerate(rows):
        for ax, (col, (a, b, _, name)) in zip(axes[r], GROWTH.items()):
            yc = f"ann_{col}{suf}"
            xs, ys, un = x[xc], x[yc], x["unreliable"]
            xlim = (np.percentile(xs, 0.5) - 0.5, np.percentile(xs, 99.5) + 0.5)
            ylim = _robust_limits(ys, pad=0.8)
            off = _scatter_exposure(ax, xs, ys, un, xlim, ylim)
            fa = viz.ols(xs, ys)
            fr = viz.ols(xs[~un], ys[~un])
            viz._lines(ax, xs, ys, fa, xlim[1], xmin=xlim[0])
            _binned(ax, xs, ys)
            ax.axhline(0, color=INK["axis"], lw=1.0, zorder=1)
            ax.set_xlim(*xlim)
            ax.set_ylim(*ylim)
            if r == 1:
                viz._pct_axis(ax)
            rho = stats.spearmanr(xs, ys)[0]
            s_all = 5 * fa["slope"]
            lines = (f"All {fa['n']}: {signed(s_all, 2)} pts/yr per +5 pp  (CI {signed(5 * fa['lo'], 2)} to {signed(5 * fa['hi'], 2)})\n"
                     f"Reliable only ({fr['n']}): {signed(5 * fr['slope'], 2)}  (CI {signed(5 * fr['lo'], 2)} to {signed(5 * fr['hi'], 2)})")
            viz._heading(ax, name + (f"  (Dec {a} \u2192 Dec {b})" if r == 0 else ""), lines, lines=2)
            ax.set_xlabel(xlabel if ax is axes[r][1] else "", fontsize=10)
            out.append(("within metro" if r == 0 else "pooled", name, 5 * fa["slope"], 5 * fa["lo"], 5 * fa["hi"],
                        fa["r2"], rho, fa["n"], 5 * fr["slope"], 5 * fr["lo"], 5 * fr["hi"], fr["n"], off))
        axes[r][0].set_ylabel(ylabel)
    h = [Line2D([0], [0], marker="o", ls="", color=C1, alpha=0.8, markersize=7, label="ZIP, reliable estimate"),
         Line2D([0], [0], marker="D", ls="", markerfacecolor="none", markeredgecolor=C1, markersize=7,
                label="ZIP, unreliable estimate"),
         Line2D([0], [0], marker="o", ls="", color=BLUE_700, markersize=7, label="Mean of each eighth (95% CI)"),
         Line2D([0], [0], color=BLUE_700, lw=2.0, label="Linear fit (all ZIPs)"),
         Line2D([0], [0], color=BLUE_700, lw=2.0, ls=(0, (4.5, 2.5)), label="Smooth fit (LOWESS)")]
    fig.legend(handles=h, loc="lower center", ncol=5, frameon=False, handletextpad=0.4, columnspacing=1.4,
               bbox_to_anchor=(0.5, 0.0))
    fig.suptitle("Did ZIPs with more pre-pandemic work-from-home grow differently?", x=0.012, y=0.994, ha="left",
                 fontsize=14, fontweight="bold")
    off_total = sum(o[-1] for o in out)
    fig.text(0.012, 0.955, f"{len(x)} ZIP codes in the eight metros with a 2015\u20132019 work-from-home share and data at every date. "
             "Top row compares ZIPs with others in the same metro; bottom row pools metros (y-axis differs by column). "
             "Slopes are per +5 percentage points of work-from-home share. Left column is a check: it covers growth "
             "before 2020. " + (f"{off_total} points beyond the axes are not drawn but are in the fits." if off_total else ""),
             fontsize=9.2, color=INK["secondary"], ha="left", va="top", wrap=True)
    fig.tight_layout(rect=(0, 0.04, 1, 0.925), h_pad=2.4, w_pad=1.6)
    return fig, pd.DataFrame(out, columns=["view", "period", "slope_per5pp", "lo", "hi", "r2", "spearman", "n",
                                           "slope_reliable", "lo_reliable", "hi_reliable", "n_reliable", "off_axis"])


def exposure_confounds(x: pd.DataFrame):
    """Figure 2.4c: what the work-from-home share is tangled up with. Within-metro, vs. income and distance."""
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.9))
    xs = x["wfh_pct_dm"]
    for ax, (col, lab, title, fmt) in zip(axes, [
            ("log_income", "Median household income, 2015\u20132019", "Higher-income ZIPs have more work-from-home", True),
            ("dist_cityhall_mi", "Distance from city hall (miles)", "Work-from-home share varies with distance", False)]):
        yv = x[col] - x.groupby("metro_short")[col].transform("median") if fmt else x[col]
        ok = yv.notna() & xs.notna()
        un = x["unreliable"][ok]
        xlim = (np.percentile(yv[ok], 0.5), np.percentile(yv[ok], 99.5))
        ylim = _robust_limits(xs[ok], pad=0.8)
        _scatter_exposure(ax, yv[ok], xs[ok], un, xlim, ylim)
        f = viz.ols(yv[ok], xs[ok])
        viz._lines(ax, yv[ok], xs[ok], f, xlim[1], xmin=xlim[0])
        rho = stats.spearmanr(yv[ok], xs[ok])[0]
        ax.set_xlim(*xlim)
        ax.set_ylim(*ylim)
        ax.axhline(0, color=INK["axis"], lw=1.0, zorder=1)
        ax.set_ylabel("Work-from-home share minus the metro median (pp)")
        if fmt:
            ax.set_xlabel("Median household income relative to the metro median (log ratio; 0.5 \u2248 1.65\u00d7)")
            ax.axvline(0, color=INK["axis"], lw=1.0, zorder=1)
        else:
            ax.set_xlabel("Distance from city hall (miles)")
        viz._heading(ax, title, f"Spearman \u03c1 = {signed(rho, 2)}  \u00b7  n = {int(ok.sum())}")
    fig.suptitle("The exposure measure is entangled with income and place", x=0.012, y=0.995, ha="left",
                 fontsize=14, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    return fig


EXPOSURE_VARS = [("wfh_pct", "Work-from-home share, 2015\u20132019"),
                 ("occ_mgmt_biz_sci_arts_share_2019", "Management/professional share of workers"),
                 ("log_income", "Median household income (log)"),
                 ("sf_detached_share_2019", "Single-family detached share of homes"),
                 ("units_20plus_share_2019", "Share of homes in 20+ unit buildings"),
                 ("dist_cityhall_mi", "Distance from city hall"),
                 ("log_level", "Home value, Dec 2019 (log)"),
                 ("ann_cum_2017_2019", "Growth, pre-2020"),
                 ("ann_cum_2019_2022", "Growth, 2020\u20132022"),
                 ("ann_cum_2022_2025", "Growth, 2023\u20132025")]


def exposure_corr(x: pd.DataFrame):
    """Figure 2.4b: within-metro rank correlations. Each variable is converted to its percentile within its metro, so
    differences between metros do not drive the result."""
    z = x.copy()
    z["log_level"] = np.log(z["level_Dec 2019"])
    cols = [c for c, _ in EXPOSURE_VARS]
    pr = z.groupby("metro_short")[cols].rank(pct=True)
    m = pr.corr().to_numpy()
    n = len(cols)
    mask = np.triu(np.ones((n, n), bool), k=1)
    show = np.where(mask, np.nan, m)
    cmap = LinearSegmentedColormap.from_list("div", DIVERGING)
    fig, ax = plt.subplots(figsize=(10.4, 8.0))
    ax.imshow(show, cmap=cmap, norm=TwoSlopeNorm(0, -1, 1))
    for i in range(n):
        for j in range(i + 1):
            v = m[i, j]
            ax.text(j, i, f"{v:+.2f}".replace("-", MINUS) if i != j else "1", ha="center", va="center", fontsize=9.5,
                    color="white" if abs(v) > 0.62 and i != j else INK["primary"])
    ax.set_xticks(range(n))
    ax.set_xticklabels([l for _, l in EXPOSURE_VARS], rotation=40, ha="right", fontsize=9.5)
    ax.set_yticks(range(n))
    ax.set_yticklabels([l for _, l in EXPOSURE_VARS], fontsize=9.5)
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    fig.suptitle("How the exposure measure relates to everything else (within metro)", x=0.012, y=0.985, ha="left",
                 fontsize=14, fontweight="bold")
    fig.text(0.012, 0.935, f"Rank correlations among {len(z)} ZIP codes; each variable is first converted to its percentile "
             "within its own metro. Warm = move together, cool = move apart.", fontsize=9.2, color=INK["secondary"],
             ha="left", va="top", wrap=True)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    return fig, pd.DataFrame(m, index=[l for _, l in EXPOSURE_VARS], columns=[l for _, l in EXPOSURE_VARS])
