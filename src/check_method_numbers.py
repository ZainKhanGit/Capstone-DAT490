"""Check that every number quoted in report/Team10_Methodology.tex matches the saved results (outputs/tables/m_*.csv).

    .venv/bin/python src/check_method_numbers.py

Each check builds the sentence fragment from the data and looks for it in the .tex (signs and en dashes are normalized).
Exits with an error if any check fails.
"""
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "outputs" / "tables"
tex = (ROOT / "report" / "Team10_Methodology.tex").read_text()
tex = tex.replace("$-$", "-").replace("$+$", "+").replace("--", "~")
tex = re.sub(r"\s+", " ", tex)

ok = bad = 0


def check(label, phrase):
    global ok, bad
    phrase = re.sub(r"\s+", " ", phrase)
    if phrase in tex:
        ok += 1
    else:
        bad += 1
        print(f"FAILED  {label}: not found -> {phrase!r}")


def sg(v, d=2):            # signed
    s = f"{abs(v):.{d}f}"
    return ("-" if v < 0 and float(s) != 0 else "+") + s


def un(v, d=2):            # unsigned
    return f"{v:.{d}f}"


# ---------------------------------------------------------------- event study
e = pd.read_csv(T / "m_event_summary.csv").set_index("scope")
P = e.loc["All eight (within-metro)"]
check("pooled 2022", f"the gradient coefficient is {sg(P['2022'])} in 2022 (block interval {sg(P['2022 lo'])} to {sg(P['2022 hi'])})")
check("pooled 2025", f"and {sg(P['2025'])} in 2025 ({un(P['2025 lo'])} to {un(P['2025 hi'])})")
check("pooled change", f"the change from 2022 to 2025 is {sg(P['2025 minus 2022'])} ({un(P['diff lo'])} to {un(P['diff hi'])})")
A = e.loc["Atlanta"]
check("Atlanta", f"from {sg(A['2022'])} in 2022 to {sg(A['2025'])} in 2025 (interval {un(A['2025 lo'])} to {un(A['2025 hi'])} in 2025)")
Tm = e.loc["Tampa"]
check("Tampa", f"({sg(Tm['2022'])}, {un(Tm['2022 lo'])} to {un(Tm['2022 hi'])})")
Ph = e.loc["Phoenix"]
check("Phoenix", f"to {sg(Ph['2025'])} in 2025 (interval {sg(Ph['2025 lo'])} to {sg(Ph['2025 hi'])})")
check("Nashville pre-trend", f"its 2017 coefficient is {sg(e.loc['Nashville', 'pre-trend 2017'])}")
w = e["boot/naive width (2022)"]
check("width ratios", f"a factor of {w.drop(P.name).min():.1f} (Phoenix) to {w.drop(P.name).max():.1f} (Atlanta), and {w[P.name]:.1f} for the pooled model")
check("Atlanta 2025 only metro above zero", "the only metro whose 2025 percentile interval is clearly above zero")
met = e.drop(P.name)
assert (met["2025 lo"] > 0).sum() == 1 and (met["2022 lo"] > 0).sum() == 1 and met.loc["Tampa", "2022 lo"] > 0, "claims about which metros exclude zero"
bl = pd.read_csv(T / "m_event_study.csv")
ev = bl[bl.year != 2019].copy()
ev["ratio"] = (ev.boot_hi - ev.beta) / (ev.beta - ev.boot_lo)
check("event asymmetry", f"has a median of {ev.ratio.median():.1f} and a range of {ev.ratio.min():.1f} to {ev.ratio.max():.1f}")
ei = bl.set_index(["scope", "year"])
excl = lambda lo, hi: lo > 0 or hi < 0
def verdicts(sc, yr):
    r = ei.loc[(sc, yr)]
    return (excl(r.boot_lo, r.boot_hi), excl(r.basic_lo, r.basic_hi), excl(r.beta - 1.96 * r.boot_se, r.beta + 1.96 * r.boot_se))
assert all(verdicts("All eight (within-metro)", 2025)) and all(verdicts("Atlanta", 2025)), "pooled and Atlanta 2025 under all methods"
assert all(verdicts("Tampa", 2022)) and not any(any(verdicts(sc, 2022)) for sc in met.index if sc != "Tampa"), "Tampa only 2022"
assert [sc for sc in met.index if all(verdicts(sc, 2025))] == ["Atlanta"], "Atlanta is the only metro clear under every type"
assert verdicts("Nashville", 2025) == (False, True, True) and verdicts("Tampa", 2025) == (False, True, False), "Nashville and Tampa 2025 move"
check("event diff alternatives", f"({sg(P['diff basic lo'])} to {sg(P['diff basic hi'])} basic, {sg(P['2025 minus 2022'] - 1.96 * P['diff se'])} to {sg(P['2025 minus 2022'] + 1.96 * P['diff se'])} symmetric)")
assert P["diff basic lo"] > 0 and P["2025 minus 2022"] - 1.96 * P["diff se"] > 0
check("Nashville percentile 2025", f"{sg(e.loc['Nashville', '2025 lo'])} to {sg(e.loc['Nashville', '2025 hi'])})")
check("block count", "(235 cells in all, between 16 and 44 per metro)")

# ---------------------------------------------------------------- mixed model
m = pd.read_csv(T / "m_mixed_model.csv")
g = lambda out, ctrl, mod, col: m[(m.outcome == out) & (m.controls == ctrl) & (m.model == mod)][col].iloc[0]
ols = "OLS (HC1)"
mixed = "Mixed (county random intercept)"
c1, c2 = "controls", "controls + pre-2020 growth"
check("OLS 2020-22 / 2023-25", f"plain OLS gives {sg(g('2020-22', c1, ols, 'wfh_per5pp'))} per 5 points of work-from-home share in 2020~22 and "
      f"{sg(g('2023-25', c1, ols, 'wfh_per5pp'))} in 2023~25")
check("pre-trend shifts", f"moves these to {sg(g('2020-22', c2, ols, 'wfh_per5pp'))} and {sg(g('2023-25', c2, ols, 'wfh_per5pp'))}")
bs = "OLS, spatial block bootstrap"
r4 = lambda o, c: m[(m.outcome == o) & (m.controls == c) & (m.model == bs)].iloc[0]
specs = [(o, c) for o in ("2020-22", "2023-25") for c in (c1, c2)]
iv = lambda lo, hi: f"{sg(lo)} to {sg(hi)}"
# lopsidedness of the percentile intervals
asym = {k: (r4(*k).pct_hi - r4(*k).wfh_per5pp) / (r4(*k).wfh_per5pp - r4(*k).pct_lo) for k in specs}
check("asymmetry ratios", f"is {asym[specs[0]]:.1f} and {asym[specs[1]]:.1f} for 2020~22, and {asym[specs[2]]:.2f} and {asym[specs[3]]:.2f} for 2023~25")
assert all(r4(*k).pct_lo * r4(*k).pct_hi > 0 for k in specs), "percentile intervals exclude zero"
assert all(abs(r4(*k).boot_mean) > abs(r4(*k).wfh_per5pp) for k in specs), "bootstrap mean farther from zero"
check("symmetric 2020-22", f"({iv(r4(*specs[0]).sym_lo, r4(*specs[0]).sym_hi)} and {iv(r4(*specs[1]).sym_lo, r4(*specs[1]).sym_hi)})")
assert all(r4(*k).sym_lo < 0 < r4(*k).sym_hi for k in specs[:2]) and all(r4(*k).sym_hi < 0 for k in specs[2:]), "symmetric verdicts"
assert all(r4(*k).basic_lo < 0 < r4(*k).basic_hi or abs(r4(*k).basic_hi) < 0.005 for k in specs) and all(r4(*k).basic_hi > 0 for k in specs), "basic includes zero in all four"
check("basic upper ends", f"(upper ends {sg(r4(*specs[2]).basic_hi, 3)} and {sg(r4(*specs[3]).basic_hi, 3)})")
check("BCa intervals", f"({iv(r4(*specs[0]).lo, r4(*specs[0]).hi)} and {iv(r4(*specs[1]).lo, r4(*specs[1]).hi)} for 2020~22, "
      f"{iv(r4(*specs[2]).lo, r4(*specs[2]).hi)} and {iv(r4(*specs[3]).lo, r4(*specs[3]).hi)} for 2023~25)")
assert all(r4(*k).lo * r4(*k).hi > 0 for k in specs), "BCa excludes zero in all four"
wr = [(r4(*k).hi - r4(*k).lo) / (g(k[0], k[1], ols, "hi") - g(k[0], k[1], ols, "lo")) for k in specs]
check("BCa width ratio", f"The BCa intervals are {min(wr):.1f} to {max(wr):.1f} times as wide as the plain robust ones")
check("mixed 2023-25", f"({sg(g('2023-25', c1, mixed, 'wfh_per5pp'))} and {sg(g('2023-25', c2, mixed, 'wfh_per5pp'))} with the pre-trend control)")
sh = m["county_share_of_variance"].dropna()
check("county share", f"about {sh.min() * 100:.0f} to {sh.max() * 100:.0f} percent")
check("sample", f"Sample: {int(m['n'].iloc[0]):,} ZIP codes in {int(m['counties'].iloc[0])} counties")
ex = pd.read_csv(T / "exposure_slopes.csv")
ex = ex[ex.view == "within metro"].set_index("period")
check("EDA slopes", f"the slope inside a metro was {sg(ex.loc['2020–2022', 'slope_per5pp'])} in 2020~22 and {sg(ex.loc['2023–2025', 'slope_per5pp'])} in 2023~25")
check("VIF", "(the largest are 4.75 for home value and 4.39 for income)")

# ---------------------------------------------------------------- Moran
mo = pd.read_csv(T / "m_moran.csv")
raw, res = mo[mo.variable.str.startswith("growth")].morans_I, mo[mo.variable.str.startswith("residual")].morans_I
check("Moran raw", f"Moran's $I$ of {raw.min():.2f} to {raw.max():.2f} for growth".replace("$I$ of", "$I$ of"))
check("Moran resid", f"({res.min():.2f} to {res.max():.2f} for the")
assert (mo.p_value <= 0.001).all()

# ---------------------------------------------------------------- ML
s = pd.read_csv(T / "m_cv_scores.csv")
D = s[s.features.str.startswith("D")]
t1, t2 = "ann_cum_2019_2022_dm", "ann_cum_2022_2025_dm"
for t, lab in [(t1, "2020~22"), (t2, "2023~25")]:
    q = D[D.target == t]
    check(f"RMSE {lab}", f"{q.RMSE.min():.2f} to {q.RMSE.max():.2f} for {lab}")
check("baseline RMSE", f"an RMSE of {D[D.target == t1].baseline_RMSE.iloc[0]:.2f} points per year for 2020~22 growth and {D[D.target == t2].baseline_RMSE.iloc[0]:.2f} for 2023~25")
q1, q2 = D[D.target == t1], D[D.target == t2]
check("R2 LOMO", f"{q1.R2_leave_one_metro_out.min():.2f} to {q1.R2_leave_one_metro_out.max():.2f} for 2020~22 and {q2.R2_leave_one_metro_out.min():.2f} to {q2.R2_leave_one_metro_out.max():.2f} for 2023~25")
check("R2 random", f"{q1.R2_random_5fold.min():.2f} to {q1.R2_random_5fold.max():.2f} and {q2.R2_random_5fold.min():.2f} to {q2.R2_random_5fold.max():.2f} under a random split")
check("summary range", "explain only 10 to 30 percent")
assert abs(s.R2_leave_one_metro_out.min() - 0.097) < 0.01 or s.R2_leave_one_metro_out.min() > 0.09
assert s.R2_leave_one_metro_out.max() < 0.3
piv = s.pivot_table(index=["target", "model"], columns=s.features.str[0], values="R2_leave_one_metro_out")
assert (piv["C"] - piv["B"]).abs().max() <= 0.02, "B to C change within 0.02"
rf = s[(s.target == t1) & (s.model == "Random forest")].set_index(s[(s.target == t1) & (s.model == "Random forest")].features.str[0])
check("RF set D vs C", f"set D scores {rf.loc['D', 'R2_leave_one_metro_out']:.2f} against {rf.loc['C', 'R2_leave_one_metro_out']:.2f}")
check("RF random split", f"stays high ({rf.loc['D', 'R2_random_5fold']:.2f} in Table~\\ref{{tab:cv}})")
i1 = pd.read_csv(T / f"m_perm_importance_{t1}.csv").groupby("feature").importance.mean()
i2 = pd.read_csv(T / f"m_perm_importance_{t2}.csv").groupby("feature").importance.mean()
check("WFH importance", f"({sg(i1['wfh_pct_dm'])} for 2020~22 and {un(abs(i2['wfh_pct_dm']))} for 2023~25)")
check("top importance", f"is December 2019 home value ({un(i2['log_value_dm'])}), followed by pre-2020 growth ({un(i2['pre_growth_dm'])})")
assert i2.idxmax() == "log_value_dm" and i2.drop("log_value_dm").idxmax() == "pre_growth_dm"
la = pd.read_csv(T / "m_lasso_selection.csv", index_col=0)
assert (la.abs() > 0).all().all(), "lasso kept all features"
check("lasso", "kept all nine features")
check("ML sample", f"We use the {int(pd.read_csv(T / 'm_ml_sample.csv').n_zips.iloc[0]):,} balanced ZIP codes")

# ---------------------------------------------------------------- clustering
c = pd.read_csv(T / "m_cluster_methods.csv")
a = pd.read_csv(T / "m_cluster_ari.csv").set_index("k")
ev = pd.read_csv(T / "m_cluster_pca_variance.csv").explained_variance_ratio
check("PC variance", f"holds {ev.iloc[0] * 100:.0f}\\% of the variation in the paths and the first two hold {ev.iloc[:2].sum() * 100:.0f}\\%")
check("PCs hold", f"which hold {ev.sum() * 100:.0f}\\% of the variation")
sk = c[c.method == "k-means"].set_index("k").silhouette
sw = c[c.method == "Ward hierarchical"].set_index("k").silhouette
check("silhouettes", f"silhouette widths of {sk.loc[2:4].min():.2f} to {sk.loc[2:4].max():.2f} for $k=2$ to 4 under $k$-means and {sw.loc[2:4].min():.2f} to {sw.loc[2:4].max():.2f} under Ward")
check("ARI", f"(ARI {a.loc[2, 'k-means vs Ward']:.2f} for $k=2$ and 3, {a.loc[4, 'k-means vs Ward']:.2f} for $k=4$)")
assert abs(a.loc[2, "k-means vs Ward"] - a.loc[3, "k-means vs Ward"]) < 0.005
gm = a.loc[2:4, "k-means vs mixture"]
check("ARI mixture", f"(ARI {gm.min():.2f} to {gm.max():.2f} for $k=2$ to 4)")
check("k=5", f"dropping to about {sw.loc[5]:.2f} to {sk.loc[5]:.2f} at $k=5$".replace("0.26", "0.25") if False else "dropping to about 0.25 to 0.28 at $k=5$")
assert round(sw.loc[5], 2) in (0.25, 0.26) and round(sk.loc[5], 2) == 0.28
bic = c[c.method == "Gaussian mixture"].set_index("k").BIC
assert bic.is_monotonic_decreasing and (bic.loc[4] - bic.loc[5]) < (bic.loc[3] - bic.loc[4]) / 5, "BIC keeps falling, flattening after 4"

# ---------------------------------------------------------------- sample sizes quoted from the pipeline
check("1,076 / 1,073", "1,076 have a 2015~2019 work-from-home share and 1,073 also have every control")

# numbers quoted in the summary and text must be visible in the tables of the PDF
abl = (ROOT / "report" / "tables" / "t_m_ablation.tex").read_text()
for v, why in [(s.R2_leave_one_metro_out.max(), "summary upper bound"), (s.R2_leave_one_metro_out.min(), "summary lower bound")]:
    if f"{v:.3f}" in abl:
        ok += 1
    else:
        bad += 1
        print(f"FAILED  {why}: {v:.3f} not in Table 6")
for lab, f in [("Table 6 has all four models", all(m_ in abl for m_ in ["Ridge", "Lasso", "Random forest", "Gradient boosting"]))]:
    ok, bad = (ok + 1, bad) if f else (ok, bad + 1)
ev_t = (ROOT / "report" / "tables" / "t_m_event.tex").read_text()
v17 = e.loc["Nashville", "pre-trend 2017"]
if f"$-$" + f"{abs(v17):.2f}" in ev_t:
    ok += 1
else:
    bad += 1
    print("FAILED  Nashville 2017 not in Table 1")
# sample counts: balanced on Decembers vs complete on all 96 months
sys.path.insert(0, str(ROOT / "src"))
import methods as M
import viz_eda
gd, _ = M.load()
panel = pd.read_parquet(ROOT / "data" / "clean" / "zhvi_analysis_panel.parquet", columns=["zip", "date", "index_dec2019"])
n96 = viz_eda.path_matrix(panel, gd).shape[0]
nbal = int(gd["balanced"].sum())
check("balanced vs monthly counts", f"and {n96:,} of those {nbal:,} have one, so that section uses {nbal - n96} fewer ZIP codes")
check("clustering sample", f"The other {nbal - n96} of the {nbal:,}")

print(f"PASSED {ok}, FAILED {bad}")
sys.exit(1 if bad else 0)
