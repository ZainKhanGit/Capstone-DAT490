"""Build the LaTeX tables for the report from the pipeline outputs (so numbers cannot be mistyped).
Run from the repo root:  .venv/bin/python report/make_tables.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import viz  # noqa: E402

C = ROOT / "data" / "clean"
T = ROOT / "outputs" / "tables"
OUT = ROOT / "report" / "tables"
M = viz.METRO_ORDER
MINUS = "$-$"


def num(v, dec=1, plus=False):
    if pd.isna(v):
        return "-"
    s = f"{abs(v):.{dec}f}"
    if float(s) == 0:
        return s
    return (MINUS if v < 0 else ("+" if plus else "")) + s


TABLE_FONT = r"\footnotesize"          # every table is set at this size; nothing is scaled to fit
STACK = lambda a, b: r"\shortstack[r]{" + a + r"\\" + b + "}"   # two-line column header


def write(name, header, rows, colspec, note=None, font=None):
    lines = [TABLE_FONT + r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{" + colspec + "}", r"\toprule", " & ".join(header) + r" \\", r"\midrule"]
    lines += [" & ".join(r) + r" \\" for r in rows]
    lines += [r"\bottomrule", r"\end{tabular}"]
    (OUT / name).write_text("\n".join(lines) + "\n")


# ---- Table 1: data coverage and quality by metro
zm = pd.read_csv(C / "zhvi_zip_meta.csv", dtype={"zip": str})
acs = pd.read_csv(C / "zip_acs.csv", dtype={"zip": str})
zori = pd.read_csv(C / "zori_zip_meta.csv", dtype={"zip": str})
fl = pd.read_csv(C / "zip_flags.csv", dtype={"zip": str})
xw = pd.read_csv(C / "zip_metro_xwalk.csv", dtype={"zip": str})
rows = []
tot = dict(z=0, c=0, a=0, o=0, u=0, col=0)
for m in M:
    z = zm[zm.metro_short == m]
    n = len(z)
    c = int(z.complete_window.sum())
    a = int(acs.loc[acs.metro_short == m, "in_acs_2019"].sum())
    o = int(zori.loc[zori.metro_short == m, "has_any_zori"].sum())
    u = int(fl.loc[fl.metro_short == m, "wfh_unreliable"].sum())
    col = int((xw.metro_col == m).sum() - ((xw.metro_col == m) & (xw.metro_xwalk == m)).sum())
    rows.append([m, f"{n}", f"{c} ({100 * c / n:.0f}\\%)", f"{a} ({100 * a / n:.0f}\\%)", f"{o} ({100 * o / n:.0f}\\%)",
                 f"{u} ({100 * u / n:.0f}\\%)", f"{col}"])
    for k, v in zip(tot, (n, c, a, o, u, col)):
        tot[k] += v
n = tot["z"]
rows.append([r"\textbf{All}", f"\\textbf{{{n:,}}}", f"{tot['c']:,} ({100 * tot['c'] / n:.1f}\\%)",
             f"{tot['a']:,} ({100 * tot['a'] / n:.1f}\\%)", f"{tot['o']:,} ({100 * tot['o'] / n:.1f}\\%)",
             f"{tot['u']} ({100 * tot['u'] / n:.0f}\\%)", f"{tot['col']}"])
write("t_coverage.tex", ["Metro", "ZIPs", STACK("Complete", "ZHVI"), STACK("ACS 2015-19", "row"), STACK("Any", "ZORI"), STACK("WFH share", "unreliable"),
                        STACK("Metro column", "only")], rows, "lrrrrrr")

# ---- Table 3: gradient slopes (OLS, 95% CI), two stacked panels
g = pd.read_csv(T / "gradient_slopes.csv")
panels = [("level", "Home value: \\% change per 10 miles from the center", ["Dec 2019", "Dec 2022", "Dec 2025"], 1),
          ("growth", "Annualized growth: points per year per 10 miles", ["Pre-2020", "2020-2022", "2023-2025"], 2)]
lines = [TABLE_FONT + r"\setlength{\tabcolsep}{4pt}", r"\begin{tabular}{lccc}", r"\toprule"]
for k, (meas, title, pans, dec) in enumerate(panels):
    if k:
        lines.append(r"\midrule")
    lines += [r"Metro & \multicolumn{3}{c}{" + title + r"} \\", r"\cmidrule(lr){2-4}",
              " & ".join([""] + pans) + r" \\", r"\midrule"]
    for m in M:
        for dist in (["city hall"] + (["nearest of two centers"] if m in viz.TWO_CENTER else [])):
            r = [m + ("" if dist == "city hall" else " (nearest of 2)")]
            for pn in pans:
                x = g[(g.metro == m) & (g.distance == dist) & (g.measure == meas) & (g.panel == pn)].iloc[0]
                r.append(f"{num(x.slope, dec, True)} [{num(x.lo, dec)}, {num(x.hi, dec)}]")
            lines.append(" & ".join(r) + r" \\")
lines += [r"\bottomrule", r"\end{tabular}"]
(OUT / "t_slopes.tex").write_text("\n".join(lines) + "\n")

# ---- Table 3: exposure slopes
e = pd.read_csv(T / "exposure_slopes.csv")
rows = []
for view in ("within metro", "pooled"):
    for per in e.period.unique():
        x = e[(e.view == view) & (e.period == per)].iloc[0]
        rows.append([view.capitalize(), per.replace(chr(0x2013), "-"), num(x.slope_per5pp, 2, True),
                     f"[{num(x.lo, 2)}, {num(x.hi, 2)}]", f"{x.r2:.3f}", num(x.spearman, 2, True),
                     num(x.slope_reliable, 2, True), f"[{num(x.lo_reliable, 2)}, {num(x.hi_reliable, 2)}]"])
write("t_exposure.tex", ["View", "Period", "Slope", "95\\% CI", "R$^2$", STACK("Rank", "corr."), STACK("Slope, reliable", "only"), "95\\% CI"],
      rows, "llrcrrrc")

# ---- Table 4: cluster profile
p = pd.read_csv(T / "cluster_profile.csv")
rows = []
for _, r in p.iterrows():
    rows.append([f"Group {int(r.cluster)}", f"{int(r.zips)}", f"{r.median_distance_mi:.0f}",
                 f"\\${r.median_value_dec2019 / 1e3:,.0f}k", f"\\${r.median_income / 1e3:,.0f}k",
                 f"{100 * r.median_wfh_share:.0f}\\%", f"{100 * r.median_sf_detached:.0f}\\%",
                 num(r.growth_pre2020, 1), num(r.growth_2020_22, 1), num(r.growth_2023_25, 1)])
write("t_clusters.tex", ["Group", "ZIPs", STACK("Distance", "(mi)"), STACK("Value", "Dec 2019"), "Income", STACK("WFH", "share"), STACK("Single-", "family"),
                        STACK("Growth", "pre-2020"), STACK("Growth", "2020-22"), STACK("Growth", "2023-25")], rows, "lrrrrrrrrr")

# ---- Table 5: ZORI coverage by distance band
b = zori.copy()
rows = []
for band in ["0-10 mi", "10-20 mi", "20-30 mi", "30+ mi"]:
    s = b[b.dist_band == band]
    rows.append([band, f"{len(s)}", f"{100 * s.has_any_zori.mean():.0f}\\%",
                 f"{100 * s.zori_both_ends.mean():.0f}\\%" if "zori_both_ends" in s else "-"])
write("t_zori.tex", ["Distance from city hall", "ZIPs", "Any ZORI", STACK("ZORI at Dec 2019", "and Dec 2025")], rows, "lrrr")
print("tables written:", sorted(p.name for p in OUT.glob("*.tex")))

# ---- Table 6: city-hall coordinates and sources
ref = pd.read_csv(ROOT / "data" / "reference" / "city_centers.csv")
rows = []
for _, r in ref.iterrows():
    src = r.source.replace("Wikipedia: ", "Wikipedia, ").replace("OpenStreetMap Nominatim lookup of the address", "OpenStreetMap address lookup")
    src = src.split(" (no Wikipedia")[0]
    rows.append([r.metro + ("" if r.role == "primary" else f" (2nd: {r.city})"), r.building.split(" (")[0].replace("&", "\\&"),
                 f"{r.lat:.4f}", num(r.lon, 4), src.replace("&", "\\&")])
write("t_centers.tex", ["Metro", "Center", "Lat.", "Lon.", "Source"], rows, "p{2.7cm}p{3.9cm}rrp{4.0cm}")

# ---- Table 7: direction test for the highest-value fifth (audit_wedge.csv)
w = pd.read_csv(T / "audit_wedge.csv")
names = {"N": "north", "NE": "northeast", "E": "east", "SE": "southeast", "S": "south", "SW": "southwest", "W": "west", "NW": "northwest"}
rows = []
for _, r in w.iterrows():
    ptxt = "$<$0.001" if r.perm_p < 0.001 else f"{r.perm_p:.2f}" if r.perm_p >= 0.01 else f"{r.perm_p:.3f}"
    rows.append([r.metro + (" (midpoint of halls)" if r.metro == "Dallas" else ""), f"{int(r.n_top_fifth)}", names[r.mean_direction],
                 f"{r.R:.2f}", ptxt, f"{int(r.pct_within_60deg)}\\%", "yes" if r.perm_p < 0.01 else "no"])
write("t_wedge.tex", ["Metro", STACK("Top-fifth", "ZIPs"), STACK("Mean", "direction"), STACK("Concentration", "R"), STACK("Permutation", "p"), STACK("Within", "60$^\\circ$"), STACK("Directional", "(p $<$ 0.01)")],
      rows, "lrlrrrr")

# ---- Table 8: exposure slopes with the pre-2020 trend controlled (audit_exposure_controls.csv)
ec = pd.read_csv(T / "audit_exposure_controls.csv")
ec.columns = ["outcome", "controls", "slope", "ci", "r2", "n"]
rows = []
for outc, lab in (("2019_2022", "2020-22 growth"), ("2022_2025", "2023-25 growth")):
    r = [lab]
    for ctl in ("WFH only", "+ pre-2020 growth", "+ pre-2020 growth + income"):
        x = ec[(ec.outcome == outc) & (ec.controls == ctl)].iloc[0]
        lo, hi = [float(v) for v in x.ci.strip("[]").split(",")]
        r.append(f"{num(x.slope, 2, True)} [{num(lo, 2)}, {num(hi, 2)}]")
    rows.append(r)
write("t_exposure_controls.tex", ["Outcome", STACK("Work-from-home", "share only"), STACK("+ pre-2020", "growth"), STACK("+ pre-2020 growth", "and income")], rows, "lccc")

# ---- Table 9: inner and outer distance bands relative to the metro (audit_band_bootstrap.csv)
bb = pd.read_csv(T / "audit_band_bootstrap.csv")
rows = []
for m in ("Atlanta", "Nashville", "Austin", "Tampa"):
    for band, lab in (("0-10 mi", "0-10 mi"), ("30+ mi", "30+ mi")):
        r = bb[(bb.metro == m) & (bb.band == band)].iloc[0]
        rows.append([m, lab, f"{int(r.n)}", f"{r['2018-01_med']:.1f}", f"{r['2022-12_med']:.1f}",
                     f"{r['2025-12_med']:.1f} [{r['2025-12_lo']:.1f}, {r['2025-12_hi']:.1f}]"])
write("t_donut.tex", ["Metro", "Band", "ZIPs", "Jan 2018", "Dec 2022", "Dec 2025 [95\\% interval]"], rows, "llrrrr")
print("tables written:", sorted(p.name for p in OUT.glob("*.tex")))
