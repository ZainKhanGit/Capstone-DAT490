"""Shared plotting style and the figure builders for EDA section 2.2 (the gradient).

Colors come from the dataviz reference palette (categorical slots 1-2 validated all-pairs in light mode;
sequential blue ramp for the fit). Rules applied: thin marks, hairline recessive grid, text in ink tokens
(never the series color), a legend whenever there are two or more series, one axis per panel.

Import from a notebook with:  sys.path.insert(0, str(ROOT / "src")); import viz
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, FixedLocator, NullLocator, MaxNLocator
from scipy import stats
from statsmodels.nonparametric.smoothers_lowess import lowess
import matplotlib.patheffects as pe

INK = {"primary": "#0b0b0b", "secondary": "#52514e", "muted": "#898781",
       "grid": "#e1e0d9", "axis": "#c3c2b7", "surface": "#fcfcfb"}
C1, C2 = "#2a78d6", "#eb6834"        # categorical slots 1 and 2
BLUE_700 = "#0d366b"                 # sequential blue step 700, for fit lines on one-color panels
ORDINAL = ["#86b6ef", "#3987e5", "#184f95"]   # blue steps 250/400/600: ordered dates or periods (validated --ordinal)
LOWESS_FRAC = 0.45                   # share of ZIPs in each local fit; the same everywhere
HALO = [pe.withStroke(linewidth=3.8, foreground="#fcfcfb")]
MINUS = "−"

# period -> (start December, end December, years, column title)
GROWTH = {
    "cum_2017_2019": (2017, 2019, 2, "Pre-2020"),
    "cum_2019_2022": (2019, 2022, 3, "2020–2022"),
    "cum_2022_2025": (2022, 2025, 3, "2023–2025"),
}
LEVEL_DATES = [("2019-12-31", "Dec 2019"), ("2022-12-31", "Dec 2022"), ("2025-12-31", "Dec 2025")]


def set_style() -> None:
    plt.rcParams.update({
        "figure.facecolor": INK["surface"], "axes.facecolor": INK["surface"],
        "savefig.facecolor": INK["surface"], "figure.dpi": 110, "savefig.dpi": 200,
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "DejaVu Sans"],
        "font.size": 10.5, "axes.titlesize": 11.5, "axes.labelsize": 10.5,
        "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "legend.fontsize": 10,
        "text.color": INK["primary"], "axes.labelcolor": INK["secondary"],
        "xtick.color": INK["muted"], "ytick.color": INK["muted"],
        "axes.edgecolor": INK["axis"], "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "axes.grid.axis": "y", "grid.color": INK["grid"], "grid.linewidth": 0.7, "grid.linestyle": "-",
        "axes.axisbelow": True, "xtick.major.size": 0, "ytick.major.size": 0,
        "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
    })


# ----------------------------------------------------------------------------- data
def gradient_data(clean: Path) -> pd.DataFrame:
    """One row per ZIP: distances, price levels at three Decembers, annualized growth by period."""
    zg = pd.read_csv(clean / "zip_growth.csv", dtype={"zip": str})
    dist = pd.read_csv(clean / "zip_distance.csv", dtype={"zip": str})[["zip", "city", "nearest_center"]]
    d = zg.merge(dist, on="zip", how="left")
    panel = pd.read_parquet(clean / "zhvi_analysis_panel.parquet", columns=["zip", "date", "zhvi"])
    for date, label in LEVEL_DATES:
        s = panel[panel["date"] == pd.Timestamp(date)].set_index("zip")["zhvi"]
        d[f"level_{label}"] = d["zip"].map(s)
    for col, (_, _, years, _) in GROWTH.items():
        d[f"ann_{col}"] = 100 * ((1 + d[col] / 100) ** (1 / years) - 1)
    # Same ZIPs in every panel: a change in slope between panels must not come from a changing sample.
    need = [f"level_{lab}" for _, lab in LEVEL_DATES] + [f"ann_{c}" for c in GROWTH]
    d["balanced"] = d[need].notna().all(axis=1)
    return d


# ----------------------------------------------------------------------------- statistics
def ols(x, y) -> dict:
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    n = len(x)
    b, a = np.polyfit(x, y, 1)
    resid = y - (a + b * x)
    se = np.sqrt((resid @ resid) / (n - 2) / ((x - x.mean()) ** 2).sum())
    t = stats.t.ppf(0.975, n - 2)
    return {"n": n, "slope": b, "intercept": a, "lo": b - t * se, "hi": b + t * se,
            "r2": 1 - (resid @ resid) / ((y - y.mean()) ** 2).sum()}


def signed(v: float, dec: int = 1) -> str:
    s = f"{abs(v):.{dec}f}"
    if float(s) == 0:          # no sign on a value that rounds to zero (avoids "\u22120.0")
        return s
    return (MINUS if v < 0 else "+") + s


def binned_medians(x, y, width=10.0, min_n=5):
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    edges = np.arange(0, x.max() + width, width)
    bx, by = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        k = (x >= lo) & (x < hi)
        if k.sum() >= min_n:
            bx.append(np.median(x[k]))
            by.append(np.median(y[k]))
    return np.array(bx), np.array(by)



CENTER_NAME = {"Phoenix": "Phoenix City Hall", "Austin": "Austin City Hall", "Atlanta": "Atlanta City Hall",
               "Dallas": "Dallas City Hall", "Tampa": "Tampa City Hall",
               "Charlotte": "Charlotte-Mecklenburg Government Center", "Nashville": "Nashville Metro Courthouse",
               "Las Vegas": "Las Vegas City Hall"}
METRO_ORDER = ["Phoenix", "Austin", "Atlanta", "Dallas", "Tampa", "Charlotte", "Nashville", "Las Vegas"]
TWO_CENTER = {"Dallas": ("Dallas", "Fort Worth"), "Tampa": ("Tampa", "St. Petersburg")}

# ----------------------------------------------------------------------------- drawing helpers
def _money(v, _):
    return f"${v / 1e6:.1f}M" if v >= 1e6 else f"${v / 1e3:.0f}k"


def _pct(v, _):
    return MINUS + f"{abs(v):.0f}%" if v < 0 else f"{v:.0f}%" if v == 0 else f"+{v:.0f}%"


def _pct_axis(ax):
    """Whole-number percent ticks only, so a label never rounds a tick like 2.5 to '2%'."""
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6, steps=[1, 2, 5, 10], integer=True))
    ax.yaxis.set_major_formatter(FuncFormatter(_pct))


def _heading(ax, title, sub, lines=1):
    ax.set_title(title, loc="left", fontsize=11.5, fontweight="bold", pad=21 + 12 * (lines - 1))
    ax.text(0, 1.025, sub, transform=ax.transAxes, ha="left", va="bottom", fontsize=9.3,
            color=INK["secondary"], linespacing=1.35)


def _scatter(ax, x, y, color, ylim=None, size=20):
    """Dots; a ZIP beyond the axis range is drawn as a triangle at the edge (it stays in every fit)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if ylim is None:
        ax.scatter(x, y, s=size, color=color, alpha=0.5, linewidths=0, zorder=2)
        return 0
    lo, hi = ylim
    ins = (y >= lo) & (y <= hi)
    ax.scatter(x[ins], y[ins], s=size, color=color, alpha=0.5, linewidths=0, zorder=2)
    for m, mk, edge in ((y > hi, "^", hi), (y < lo, "v", lo)):
        if m.any():
            ax.scatter(x[m], np.full(m.sum(), edge), s=40, marker=mk, color=color, alpha=0.95,
                       edgecolors=INK["surface"], linewidths=1.0, zorder=3, clip_on=False)
    return int((~ins).sum())


def _robust_limits(values, pad=1.5):
    v = np.asarray(values, float)
    v = v[np.isfinite(v)]
    return np.percentile(v, 1) - pad, np.percentile(v, 99) + pad


def smooth_curve(x, y, log=False):
    """LOWESS (robust, frac=LOWESS_FRAC) over the range holding 95% of the ZIPs, where the data are dense
    enough to say anything. For log=True the smoothing is done on log(y) and returned in dollars."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    x, y = x[m], y[m]
    if len(x) < 25:
        return None
    yy = np.log(y) if log else y
    r = lowess(yy, x, frac=LOWESS_FRAC, it=3, return_sorted=True)
    keep = r[:, 0] <= np.percentile(x, 95)
    xs, ys = r[keep, 0], r[keep, 1]
    xs, idx = np.unique(xs, return_index=True)
    ys = ys[idx]
    return xs, (np.exp(ys) if log else ys)


def _lines(ax, x, y, f, xmax, log=False, color=BLUE_700, xmin=0.0, smooth=True):
    """Linear fit (solid) and smooth fit (dashed), same color: color = which group, style = which method."""
    xs = np.array([xmin, xmax])
    ys = f["intercept"] + f["slope"] * xs
    ax.plot(xs, np.exp(ys) if log else ys, color=color, lw=2.0, zorder=5, path_effects=HALO, solid_capstyle="round")
    if smooth:
        sc = smooth_curve(x, y, log=log)
        if sc is not None:
            ax.plot(*sc, color=color, lw=2.0, ls=(0, (4.5, 2.5)), zorder=6, path_effects=HALO)


def _level_axis(ax, lo, hi):
    ax.set_yscale("log")
    ax.set_ylim(lo, hi)
    ax.yaxis.set_major_locator(FixedLocator([v for v in (1e5, 2e5, 4e5, 8e5, 1.6e6) if lo <= v <= hi]))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(_money))


def _pct_per_10mi(b):
    return 100 * (np.exp(10 * b) - 1)


def _sample(d, metro):
    g = d[d["metro_short"] == metro]
    kept = g[g["balanced"]]
    return kept, len(g) - len(kept), len(g)


def _legend(fig, extra=(), y=0.0):
    h = list(extra) + [Line2D([0], [0], color=BLUE_700, lw=2.0, label="Linear fit (OLS)"),
                       Line2D([0], [0], color=BLUE_700, lw=2.0, ls=(0, (4.5, 2.5)),
                              label="Smooth fit (LOWESS)")]
    fig.legend(handles=h, loc="lower center", ncol=len(h), frameon=False, handletextpad=0.5,
               columnspacing=1.8, bbox_to_anchor=(0.5, y))


def _dot_key(color=C1, label="ZIP code"):
    return Line2D([0], [0], marker="o", ls="", color=color, alpha=0.8, markersize=7, label=label)


# ----------------------------------------------------------------------------- figure 2.2: one metro
def gradient_metro(d: pd.DataFrame, metro: str, center_name: str = None, xcol="dist_cityhall_mi"):
    """2 rows x 3 columns: home value (log scale) by distance at three dates; annualized growth by
    distance for three periods. Same ZIPs in every panel. Solid = OLS, dashed = LOWESS."""
    center_name = center_name or CENTER_NAME[metro]
    g, dropped, n_all = _sample(d, metro)
    xmax = float(np.ceil(g[xcol].max() / 10) * 10) + 2
    fig, axes = plt.subplots(2, 3, figsize=(12.2, 7.4), sharex=True)

    lv = [f"level_{lab}" for _, lab in LEVEL_DATES]
    lo, hi = g[lv].min().min() * 0.9, g[lv].max().max() * 1.1
    for ax, (_, lab), c in zip(axes[0], LEVEL_DATES, lv):
        _scatter(ax, g[xcol], g[c], C1)
        f = ols(g[xcol], np.log(g[c]))
        _lines(ax, g[xcol], g[c], f, xmax, log=True)
        _heading(ax, lab, f"{signed(_pct_per_10mi(f['slope']))}% per 10 mi  (95% CI "
                          f"{signed(_pct_per_10mi(f['lo']))} to {signed(_pct_per_10mi(f['hi']))})")
        _level_axis(ax, lo, hi)
    axes[0][0].set_ylabel("Home value (ZHVI, log scale)")

    ac = [f"ann_{c}" for c in GROWTH]
    ylim = _robust_limits(g[ac].to_numpy().ravel())
    off = 0
    for ax, (col, (a, b, yrs, name)), c in zip(axes[1], GROWTH.items(), ac):
        off += _scatter(ax, g[xcol], g[c], C1, ylim=ylim)
        f = ols(g[xcol], g[c])
        _lines(ax, g[xcol], g[c], f, xmax)
        ax.axhline(0, color=INK["axis"], lw=1.0, zorder=1)
        _heading(ax, f"{name}  (Dec {a} \u2192 Dec {b})",
                 f"{signed(10 * f['slope'], 2)} pts/yr per 10 mi  (95% CI {signed(10 * f['lo'], 2)} to "
                 f"{signed(10 * f['hi'], 2)})")
        ax.set_ylim(*ylim)
        _pct_axis(ax)
        ax.set_xlabel(f"Distance from {center_name} (miles)")
    axes[1][0].set_ylabel("Annualized growth in home value")
    for ax in axes.ravel():
        ax.set_xlim(0, xmax)

    fig.suptitle(f"{metro}: home values and growth by distance from {center_name}",
                 x=0.012, y=0.992, ha="left", fontsize=14, fontweight="bold")
    note = (f"Each dot is one of {len(g)} ZIP codes with data at every date ({dropped} of {n_all} left out so the "
            "same ZIPs appear in every panel). Growth is annualized so periods of different length compare. "
            "The smooth fit is drawn over the range holding 95% of the ZIPs.")
    if off:
        note += f" \u25b2\u25bc = ZIP beyond the axis range, drawn at the edge and kept in the fits ({off})."
    fig.text(0.012, 0.947, note, fontsize=9.2, color=INK["secondary"], ha="left", va="top", wrap=True)
    _legend(fig, extra=[_dot_key()])
    fig.tight_layout(rect=(0, 0.04, 1, 0.915), h_pad=2.4, w_pad=1.6)
    return fig


# ----------------------------------------------------------------------------- figure 2.2b/c: two-center test
def two_center(d: pd.DataFrame, metro: str, primary: str = None, second: str = None, measure: str = "growth"):
    """Rows: A = distance to the first-named city's hall (pooled fit); B = distance to the nearer of the two
    halls (pooled fit); C = same distances as B with a separate fit for each center's ZIPs.
    Dots are colored by the center each ZIP is nearer to in every row. Solid = OLS, dashed = LOWESS."""
    primary, second = (primary, second) if primary else TWO_CENTER[metro]
    g, dropped, n_all = _sample(d, metro)
    xmax = float(np.ceil(g["dist_cityhall_mi"].max() / 10) * 10) + 2
    fig, axes = plt.subplots(3, 3, figsize=(12.2, 10.8), sharex=True, sharey=True)
    rows = [("dist_cityhall_mi", f"Distance to {primary} City Hall (miles)", "A. First-named city only"),
            ("dist_nearest_mi", f"Distance to the nearer of the two city halls (miles)",
             "B. Nearest of two centers, one pooled fit"),
            ("dist_nearest_mi", f"Distance to the nearer of the two city halls (miles)",
             "C. Nearest of two centers, a fit per center")]
    if measure == "level":
        cols = [(f"level_{lab}", lab) for _, lab in LEVEL_DATES]
        vals = g[[c for c, _ in cols]]
        lo, hi = vals.min().min() * 0.9, vals.max().max() * 1.1
        ylim = None
    else:
        cols = [(f"ann_{c}", f"{v[3]}  (Dec {v[0]} \u2192 Dec {v[1]})") for c, v in GROWTH.items()]
        ylim = _robust_limits(g[[c for c, _ in cols]].to_numpy().ravel())
    log = measure == "level"
    unit = "% per 10 mi" if log else " pts/yr per 10 mi"
    cval = lambda f: _pct_per_10mi(f["slope"]) if log else 10 * f["slope"]
    colors = {primary: C1, second: C2}
    out, off = [], 0
    for r, (xcol, xlabel, rowname) in enumerate(rows):
        for ax, (c, title) in zip(axes[r], cols):
            for center in (primary, second):
                s = g[g["nearest_center"] == center]
                off += _scatter(ax, s[xcol], s[c], colors[center], ylim=ylim) if r == 0 else \
                    _scatter(ax, s[xcol], s[c], colors[center], ylim=ylim)
            if not log:
                ax.axhline(0, color=INK["axis"], lw=1.0, zorder=1)
            y_for_fit = lambda s_: np.log(s_[c]) if log else s_[c]
            if r < 2:
                f = ols(g[xcol], y_for_fit(g))
                _lines(ax, g[xcol], g[c], f, xmax, log=log)
                rho = stats.spearmanr(g[xcol], g[c])[0]
                _heading(ax, title if r == 0 else "",
                         f"{signed(cval(f), 2 if not log else 1)}{unit}  \u00b7  R\u00b2 = {f['r2']:.3f}  \u00b7  "
                         f"Spearman \u03c1 = {signed(rho, 2)}")
                out.append((rowname, "pooled", title, cval(f), cval({'slope': f['lo']}), cval({'slope': f['hi']}),
                            f["r2"], rho, f["n"]))
            else:
                parts = []
                for center in (primary, second):
                    s = g[g["nearest_center"] == center]
                    f = ols(s[xcol], y_for_fit(s))
                    _lines(ax, s[xcol], s[c], f, float(s[xcol].max()), log=log, color=colors[center],
                           xmin=float(s[xcol].min()))
                    rho = stats.spearmanr(s[xcol], s[c])[0]
                    parts.append(f"{center} {signed(cval(f), 2 if not log else 1)}{'%' if log else ''}")
                    out.append((rowname, center, title, cval(f), cval({'slope': f['lo']}), cval({'slope': f['hi']}),
                                f["r2"], rho, f["n"]))
                _heading(ax, "", f"{parts[0]}  \u00b7  {parts[1]}  per 10 mi" + ("" if log else " (pts/yr)"))
        axes[r][0].set_ylabel(f"{rowname}\n" + ("Home value (ZHVI, log scale)" if log else "Annualized growth"),
                              fontsize=9.8)
    for ax in axes.ravel():
        ax.set_xlim(0, xmax)
        ax.tick_params(labelbottom=True)
    if log:
        _level_axis(axes[0][0], lo, hi)
    else:
        axes[0][0].set_ylim(*ylim)
        _pct_axis(axes[0][0])
    for r in range(3):
        for k in range(3):
            axes[r][k].set_xlabel(rows[r][1] if k == 1 else "")
    what = "home values" if log else "growth"
    fig.suptitle(f"{primary}\u2013{second}: does a second center change the {what} gradient?",
                 x=0.012, y=0.994, ha="left", fontsize=14, fontweight="bold")
    note = (f"Same {len(g)} ZIPs, same {what}; only the distance changes. Dot color is the center each ZIP is nearer to "
            f"({int((g['nearest_center'] == second).sum())} of {len(g)} are nearer to {second}), in every row. "
            "Row C fits each center's ZIPs on their own, with line color matching the dots.")
    if off:
        note += f" \u25b2\u25bc = beyond the axis range, kept in the fits ({off // 3 if off % 3 == 0 else off})."
    fig.text(0.012, 0.957, note, fontsize=9.2, color=INK["secondary"], ha="left", va="top", wrap=True)
    handles = [_dot_key(C1, f"Nearer to {primary}"), _dot_key(C2, f"Nearer to {second}")]
    _legend(fig, extra=handles)
    fig.tight_layout(rect=(0, 0.035, 1, 0.935), h_pad=2.7, w_pad=1.6)
    return fig, pd.DataFrame(out, columns=["row", "group", "panel", "slope", "slope_lo", "slope_hi", "r2",
                                           "spearman", "n"])


# ----------------------------------------------------------------------------- slope table + summary figure
def slope_table(d: pd.DataFrame) -> pd.DataFrame:
    """OLS gradient slopes for every metro: levels as % per 10 mi, growth as pts/yr per 10 mi, with 95% CIs.
    Dallas and Tampa also get a row using the nearest-center distance."""
    rows = []
    for metro in METRO_ORDER:
        g, _, _ = _sample(d, metro)
        defs = [("city hall", "dist_cityhall_mi")]
        if metro in TWO_CENTER:
            defs.append(("nearest of two centers", "dist_nearest_mi"))
        for dname, xcol in defs:
            for _, lab in LEVEL_DATES:
                f = ols(g[xcol], np.log(g[f"level_{lab}"]))
                rows.append((metro, dname, "level", lab, _pct_per_10mi(f["slope"]), _pct_per_10mi(f["lo"]),
                             _pct_per_10mi(f["hi"]), f["r2"], stats.spearmanr(g[xcol], g[f"level_{lab}"])[0], f["n"]))
            for col, (a, b, _, name) in GROWTH.items():
                f = ols(g[xcol], g[f"ann_{col}"])
                rows.append((metro, dname, "growth", name, 10 * f["slope"], 10 * f["lo"], 10 * f["hi"], f["r2"],
                             stats.spearmanr(g[xcol], g[f"ann_{col}"])[0], f["n"]))
    return pd.DataFrame(rows, columns=["metro", "distance", "measure", "panel", "slope", "lo", "hi", "r2",
                                       "spearman", "n"])


def slope_summary(tab: pd.DataFrame):
    """Dot-and-whisker summary of the OLS gradient slopes: one row per metro (plus the nearest-center rows for
    Dallas and Tampa), three markers per row for the three dates / periods, 95% CI as whiskers."""
    rows = []
    for m in METRO_ORDER:
        rows.append((m, "city hall", m))
    for m in TWO_CENTER:
        rows.append((m, "nearest of two centers", f"{m} (nearest of two centers)"))
    # keep two-center "nearest" rows directly below the main block, in metro order
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 6.9), sharey=True)
    ylab = [r[2] for r in rows]
    ypos = {lab: i for i, lab in enumerate(ylab)}
    for ax, measure, labels, xlabel in ((axes[0], "level", [l for _, l in LEVEL_DATES], "Home value: % change per 10 miles from the center"),
                                        (axes[1], "growth", [v[3] for v in GROWTH.values()],
                                         "Annualized growth: points per year, per 10 miles")):
        for k, (lab, col) in enumerate(zip(labels, ORDINAL)):
            off = (k - 1) * 0.22
            for metro, dist, text in rows:
                t = tab[(tab["metro"] == metro) & (tab["distance"] == dist) & (tab["measure"] == measure)
                        & (tab["panel"] == lab)]
                if t.empty:
                    continue
                t = t.iloc[0]
                y = ypos[text] + off
                ax.plot([t["lo"], t["hi"]], [y, y], color=col, lw=1.6, solid_capstyle="round", zorder=3)
                ax.scatter([t["slope"]], [y], s=46, color=col, edgecolors=INK["surface"], linewidths=1.5, zorder=4)
        ax.axvline(0, color=INK["muted"], lw=1.0, zorder=1)
        ax.set_xlabel(xlabel)
        ax.set_yticks(range(len(ylab)))
        ax.set_yticklabels(ylab)
        ax.set_ylim(len(ylab) - 0.4, -0.6)
        ax.grid(axis="x", visible=True)
        ax.grid(axis="y", visible=False)
        ax.axhline(len(METRO_ORDER) - 0.5, color=INK["axis"], lw=0.8, zorder=1)
    axes[0].set_title("Price level (Dec 2019, Dec 2022, Dec 2025)", loc="left", fontsize=11.5, fontweight="bold", pad=10)
    axes[1].set_title("Annualized growth (by period)", loc="left", fontsize=11.5, fontweight="bold", pad=10)
    for ax in axes:
        ax.tick_params(axis="y", labelcolor=INK["secondary"], labelsize=10)
    h_lv = [Line2D([0], [0], marker="o", color=c, lw=1.6, markersize=7, label=l)
            for (_, l), c in zip(LEVEL_DATES, ORDINAL)]
    h_gr = [Line2D([0], [0], marker="o", color=c, lw=1.6, markersize=7, label=v[3])
            for v, c in zip(GROWTH.values(), ORDINAL)]
    axes[0].legend(handles=h_lv, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3, frameon=False)
    axes[1].legend(handles=h_gr, loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3, frameon=False)
    fig.suptitle("The distance gradient by metro: linear (OLS) slopes with 95% intervals", x=0.012, y=0.995,
                 ha="left", fontsize=14, fontweight="bold")
    fig.text(0.012, 0.935, "Negative = values or growth fall with distance from the center. A monocentric, "
             "post-2020 flattening would show the level slope moving toward zero and the growth slope turning "
             "positive. Intervals that cross zero cannot be told from a flat gradient.", fontsize=9.2,
             color=INK["secondary"], ha="left", va="top", wrap=True)
    fig.tight_layout(rect=(0, 0, 1, 0.9), w_pad=2.0)
    return fig
