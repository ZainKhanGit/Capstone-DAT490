"""Check the numbers quoted in the report against the data.

For every number the report states, this script (1) recomputes it from the data files and checks that it rounds to the
number in the report, and (2) checks that the number appears in report/Team10_EDA.tex. A failure of either kind is printed.

    .venv/bin/python src/check_report_numbers.py          # run from the project root, after audit_checks.py

Exit status is 1 if any check fails.
"""
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import skew

sys.path.insert(0, str(Path(__file__).resolve().parent))
import viz  # noqa: E402

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
C, T = ROOT / "data" / "clean", ROOT / "outputs" / "tables"
TEX = re.sub(r"\s+", " ", (ROOT / "report" / "Team10_EDA.tex").read_text() + " " + " ".join(f.read_text() for f in sorted((ROOT / "report" / "tables").glob("*.tex"))))   # the report text plus its generated tables

passed, failed = [], []


def S(v, dec):          # signed number as typeset in the report: $-$7.7 / $+$0.69
    return ("$-$" if v < 0 else "$+$") + f"{abs(v):.{dec}f}"


def U(v, dec):          # unsigned
    return f"{v:.{dec}f}"


def chk(label, computed, claimed, dec=1, signed=False, plain=None, ctx=None):
    """computed: value from the data. claimed: the number in the report. plain: override token. ctx: a longer string that
    must appear in the tex (typeset exactly as in the report)."""
    tol = 0.5 * 10 ** (-dec) + 1e-9
    ok_val = abs(float(computed) - float(claimed)) <= tol
    token = plain if plain is not None else (S(claimed, dec) if signed else U(abs(claimed), dec) if claimed >= 0 else S(claimed, dec))
    # the same number can be typeset as prose ($+$0.63) or as a table entry (+0.63, or a bare 0.64 inside an interval)
    forms = [token, token.replace("$+$", "+")] + ([token.replace("$+$", "")] if "interval" in label or "low" in label or "high" in label else [])
    ok_txt = any(f in TEX for f in forms) and (ctx is None or ctx in TEX)
    (passed if ok_val and ok_txt else failed).append(
        f"{label}: data {float(computed):.{dec + 2}f} vs report {claimed} | value {'ok' if ok_val else 'MISMATCH'} | text {'ok' if ok_txt else 'NOT FOUND: ' + (ctx or token)}")


def present(label, token):
    (passed if token in TEX else failed).append(f"{label}: text {'ok' if token in TEX else 'NOT FOUND: ' + token}")


def true(label, cond):
    (passed if cond else failed).append(f"{label}: {'ok' if cond else 'FALSE'}")


# ------------------------------------------------------------------------------------------------ data
gd = viz.gradient_data(C)
b = gd[gd["balanced"]]
zm = pd.read_csv(C / "zhvi_zip_meta.csv", dtype={"zip": str})
xw = pd.read_csv(C / "zip_metro_xwalk.csv", dtype={"zip": str})
fl = pd.read_csv(C / "zip_flags.csv", dtype={"zip": str})
acs = pd.read_csv(C / "zip_acs.csv", dtype={"zip": str})
zo = pd.read_csv(C / "zori_zip_meta.csv", dtype={"zip": str})
dist = pd.read_csv(C / "zip_distance.csv", dtype={"zip": str})
pan = pd.read_parquet(C / "zhvi_panel.parquet")
sl = pd.read_csv(T / "gradient_slopes.csv")
ex = pd.read_csv(T / "exposure_slopes.csv")
cm = pd.read_csv(T / "exposure_corr.csv", index_col=0)
fc = pd.read_csv(T / "two_center_fits.csv")
rb = pd.read_csv(T / "robustness_flag_free.csv")
rent = pd.read_csv(T / "rent_vs_price_slopes.csv")
sil = pd.read_csv(T / "cluster_silhouette.csv", index_col=0).iloc[:, 0]
prof = pd.read_csv(T / "cluster_profile.csv", index_col=0)
wedge = pd.read_csv(T / "audit_wedge.csv").set_index("metro")
hump = pd.read_csv(T / "audit_hump.csv")
ctl = pd.read_csv(T / "audit_exposure_controls.csv"); ctl.columns = ["out", "ctl", "slope", "ci", "r2", "n"]
band = pd.read_csv(T / "audit_band_bootstrap.csv")
inout = pd.read_csv(T / "audit_inner_outer_growth.csv")
phx = pd.read_csv(T / "audit_phoenix_exclusions.csv").set_index("exclusion")
phf = pd.read_csv(T / "audit_phoenix_flagged.csv").set_index("key")["value"]
cores = pd.read_csv(T / "audit_cores.csv")
coreq = pd.read_csv(T / "audit_core_quintiles.csv").set_index("metro")
clus = pd.read_csv(T / "audit_clusters.csv").set_index("key")["value"]
rsd = pd.read_csv(T / "audit_residual_sd.csv").set_index("period")
gsd = pd.read_csv(T / "audit_growth_sd.csv", index_col=0)
shift = pd.read_csv(T / "audit_slope_shifts.csv").set_index("metro")
sect = pd.read_csv(T / "audit_sector_medians.csv")
reg = pd.read_csv(T / "audit_regional.csv").set_index("key")["value"]
cdef = pd.read_csv(T / "robustness_center_definition.csv")
comp = pd.read_csv(T / "cluster_metro_composition.csv", index_col=0)


def S_(m, meas, pan_, dist_="city hall"):
    return sl[(sl.metro == m) & (sl.measure == meas) & (sl.panel == pan_) & (sl.distance == dist_)].iloc[0]


# ================================================================================================ section 1
import glob
raw = pd.read_csv(glob.glob(str(ROOT / "data" / "raw" / "Zip_zhvi_*.csv"))[0], usecols=["Metro"])
chk("ZHVI ZIPs nationally", len(raw), 26268, 0, plain="26,268")
chk("ZIPs in eight metros", pan.zip.nunique(), 1099, 0, plain="1,099")
chk("blank Metro labels", int(raw["Metro"].isna().sum()), 4712, 0, plain="4,712")
chk("both methods agree", int((xw.status == "both_agree").sum()), 1087, 0, plain="1,087")
chk("Metro-column-only ZIPs", int((xw.status == "metro_col_only").sum()), 12, 0, plain="Twelve ZIP codes")
chk("crosswalk-only ZIPs", int((xw.status == "xwalk_only").sum()), 5, 0, plain="five are in a delineation county")
chk("panel rows", len(pan), 351680, 0, plain="351,680")
chk("complete ZHVI series", int(zm.complete_window.sum()), 1072, 0, plain="1,072 (97.5\\%)")
chk("late entrants", int(zm.late_entry.sum()), 17, 0, plain="17 start after January 2018")
chk("interior gaps", int((zm.n_interior_gaps > 0).sum()), 10, 0, plain="10 have gaps in the middle")
chk("balanced sample", len(b), 1082, 0, plain="1,082 ZIP codes that have a value at every date")
chk("ACS 2015-19 matches", int(acs.in_acs_2019.sum()), 1092, 0, plain="1,092 of 1,099")
chk("ZIPs flagged unreliable (of 1,092)", int(fl.wfh_unreliable.sum()), 248, 0, plain="248 of 1,092")
d_ = dist.merge(fl[["zip", "wfh_unreliable"]], on="zip").merge(acs[["zip", "in_acs_2019"]], on="zip"); d_ = d_[d_.in_acs_2019]
chk("median distance, unreliable", d_[d_.wfh_unreliable].dist_cityhall_mi.median(), 39, 0, plain="39 miles")
chk("median distance, rest", d_[~d_.wfh_unreliable].dist_cityhall_mi.median(), 17, 0, plain="17 miles")
chk("ZIPs with any ZORI", int(zo.has_any_zori.sum()), 799, 0, plain="799 of our 1,099")
chk("ZIPs with complete ZORI", int(zo.complete_window.sum()), 398, 0, plain="398 have every month")
bz = dist.merge(zo[["zip", "has_any_zori"]], on="zip")
chk("ZORI share 30+ mi", 100 * bz[bz.dist_band == "30+ mi"].has_any_zori.mean(), 36, 0, plain="36\\%")
chk("ZORI share 0-10 mi", 100 * bz[bz.dist_band == "0-10 mi"].has_any_zori.mean(), 94, 0, plain="94\\%")
corr_min = min(dist[dist.metro_short == m][["dist_cityhall_mi", "dist_zctactr_mi"]].corr(method="spearman").iloc[0, 1] for m in viz.METRO_ORDER)
true("rank correlation of ZCTA-centroid distance >= 0.986", corr_min >= 0.986 - 1e-3)
present("0.986 in text", "0.986")
present("Phoenix figure caption peak distance agrees with text", "The smooth fit peaks about 24 miles from city hall")

# ================================================================================================ section 2.1
v = gd["level_Dec 2019"].dropna()
chk("skewness dollars", skew(v), 2.6, 1); chk("skewness logs", skew(np.log(v)), 0.4, 1)
med = b.groupby("metro_short")[["level_Dec 2019", "level_Dec 2022", "level_Dec 2025"]].median() / 1e3
for lab, m, col, claim in (("Charlotte 2019", "Charlotte", "level_Dec 2019", 204), ("Austin 2019", "Austin", "level_Dec 2019", 331),
                           ("Austin 2022", "Austin", "level_Dec 2022", 525), ("Phoenix 2022", "Phoenix", "level_Dec 2022", 460),
                           ("Austin 2025", "Austin", "level_Dec 2025", 446), ("Phoenix 2025", "Phoenix", "level_Dec 2025", 441)):
    chk(f"median value {lab}", med.loc[m, col], claim, 0, plain=f"\\${claim}k")
gm = b.groupby("metro_short")[["ann_cum_2019_2022", "ann_cum_2022_2025"]].median()
chk("Las Vegas 2020-22 median growth", gm.loc["Las Vegas", "ann_cum_2019_2022"], 12.6, 1, plain="12.6\\%")
chk("Tampa 2020-22 median growth", gm.loc["Tampa", "ann_cum_2019_2022"], 17.5, 1, plain="17.5\\%")
chk("Austin 2023-25 median growth", gm.loc["Austin", "ann_cum_2022_2025"], -5.1, 1, plain="$-$5.1\\%")
chk("Charlotte 2023-25 median growth", gm.loc["Charlotte", "ann_cum_2022_2025"], 1.5, 1, plain="$+$1.5\\%")

# ================================================================================================ section 2.2
for lab, m, meas, pn, claim, dec in [
        ("Atlanta level 2019", "Atlanta", "level", "Dec 2019", -7.7, 1), ("Atlanta level 2022", "Atlanta", "level", "Dec 2022", -6.0, 1),
        ("Atlanta level 2025", "Atlanta", "level", "Dec 2025", -3.0, 1), ("Atlanta growth pre", "Atlanta", "growth", "Pre-2020", -0.44, 2),
        ("Atlanta growth 20-22", "Atlanta", "growth", "2020–2022", 0.69, 2), ("Atlanta growth 23-25", "Atlanta", "growth", "2023–2025", 1.03, 2),
        ("Austin growth 23-25", "Austin", "growth", "2023–2025", 0.63, 2), ("Austin growth 20-22", "Austin", "growth", "2020–2022", 0.21, 2),
        ("Tampa growth 20-22", "Tampa", "growth", "2020–2022", 0.57, 2), ("Tampa growth 23-25", "Tampa", "growth", "2023–2025", -0.32, 2),
        ("Phoenix growth pre", "Phoenix", "growth", "Pre-2020", 0.46, 2), ("Phoenix growth 23-25", "Phoenix", "growth", "2023–2025", -0.30, 2),
        ("Phoenix level 2019", "Phoenix", "level", "Dec 2019", -4.3, 1), ("Phoenix level 2025", "Phoenix", "level", "Dec 2025", -5.6, 1),
        ("Nashville growth pre", "Nashville", "growth", "Pre-2020", 1.02, 2)]:
    chk(lab, S_(m, meas, pn).slope, claim, dec, signed=True)
x = S_("Austin", "growth", "2020–2022"); chk("Austin 2020-22 interval low", x.lo, -0.22, 2, signed=True); chk("Austin 2020-22 interval high", x.hi, 0.64, 2, signed=True)
x = S_("Tampa", "growth", "2023–2025"); chk("Tampa 2023-25 interval low", x.lo, -0.68, 2, signed=True); chk("Tampa 2023-25 interval high", x.hi, 0.03, 2, signed=True)
chk("Charlotte level slope", S_("Charlotte", "level", "Dec 2019").slope, -18.1, 1, signed=True)
chk("Austin level slope", S_("Austin", "level", "Dec 2019").slope, -14.9, 1, signed=True)
chk("Nashville level slope", S_("Nashville", "level", "Dec 2019").slope, -13.5, 1, signed=True)
true("Charlotte R2 about 0.5", 0.45 <= S_("Charlotte", "level", "Dec 2019").r2 <= 0.52)
true("Atlanta/Tampa/Phoenix R2 under 0.12", max(S_(m, "level", p).r2 for m in ("Atlanta", "Tampa", "Phoenix") for p in ("Dec 2019", "Dec 2022", "Dec 2025")) < 0.12)
true("Dallas/Las Vegas R2 below 0.01", max(S_(m, "level", p).r2 for m in ("Dallas", "Las Vegas") for p in ("Dec 2019", "Dec 2022", "Dec 2025")) < 0.01)
true("six metros have a level-slope interval excluding zero at Dec 2019", sum((S_(m, "level", "Dec 2019").hi < 0) for m in viz.METRO_ORDER) == 6)
chg = {m: S_(m, "level", "Dec 2025").slope - S_(m, "level", "Dec 2019").slope for m in viz.METRO_ORDER}
chk("Atlanta level-slope change", chg["Atlanta"], 4.7, 1, signed=True); chk("Austin level-slope change", chg["Austin"], 2.2, 1, signed=True)
true("others within 1.5", all(abs(chg[m]) <= 1.5 for m in viz.METRO_ORDER if m not in ("Atlanta", "Austin")))
true("level-slope intervals at the three dates overlap in every metro",
     all(max(S_(m, "level", p).lo for p in ("Dec 2019", "Dec 2022", "Dec 2025")) <= min(S_(m, "level", p).hi for p in ("Dec 2019", "Dec 2022", "Dec 2025")) for m in viz.METRO_ORDER))
true("Atlanta growth intervals pre vs 2020-22 do not overlap", S_("Atlanta", "growth", "Pre-2020").hi < S_("Atlanta", "growth", "2020–2022").lo)
true("Phoenix level intervals Dec 2019 vs Dec 2025 overlap", S_("Phoenix", "level", "Dec 2025").hi > S_("Phoenix", "level", "Dec 2019").lo)
# humps and Phoenix far tail
for lab, m, claim in (("Phoenix LOWESS peak", "Phoenix", 24), ("Las Vegas LOWESS peak", "Las Vegas", 15)):
    chk(lab, hump[(hump.metro == m) & (hump.date == "Dec 2025")].lowess_peak_mi.iloc[0], claim, 0, plain=f"about 24 and 15 miles" if m == "Phoenix" else "about 24 and 15 miles")
true("Phoenix quadratic p (Dec 2025) rounds to 0.004", round(hump[(hump.metro == "Phoenix") & (hump.date == "Dec 2025")].quad_p_HC1.iloc[0], 3) == 0.004)
true("Las Vegas quadratic p (Dec 2025) < 0.001", hump[(hump.metro == "Las Vegas") & (hump.date == "Dec 2025")].quad_p_HC1.iloc[0] < 0.001)
chk("Phoenix level slope beyond-40-mi dropped", phx.loc["drop ZIPs beyond 40 mi", "slope"], 8.1, 1, signed=True)
chk("   interval low", phx.loc["drop ZIPs beyond 40 mi", "lo"], 1.4, 1, signed=True); chk("   interval high", phx.loc["drop ZIPs beyond 40 mi", "hi"], 15.1, 1, signed=True)
chk("ZIPs beyond 40 miles removed", phx.loc["all ZIPs", "n"] - phx.loc["drop ZIPs beyond 40 mi", "n"], 20, 0, plain="20 ZIP codes beyond 40 miles")
chk("unreliable-WFH ZIPs in Phoenix sample", phf["phoenix_wfh_unreliable_n"], 16, 0, plain="16 ZIP codes with an unreliable work-from-home share")
chk("their median distance", phf["phoenix_wfh_unreliable_median_mi"], 56, 0, plain="median distance 56 miles")
chk("Phoenix flag-free level slope", phx.loc["drop wfh_unreliable", "slope"], 0.5, 1, plain="$+$0.5\\%")
true("other three Phoenix flags change nothing", all(abs(phx.loc[f"drop {k}", "slope"] - phx.loc["all ZIPs", "slope"]) < 0.1 for k in ("zhvi_incomplete", "metro_col_only", "acs_baseline_missing")))
true("shift rule: Atlanta, Nashville, Tampa, Phoenix, Austin shifted; Charlotte, Dallas, Las Vegas did not",
     all(shift.loc[m, "shifted"] for m in ("Atlanta", "Nashville", "Tampa", "Phoenix", "Austin")) and not any(shift.loc[m, "shifted"] for m in ("Charlotte", "Dallas", "Las Vegas")))
# two-center
def F(metro, meas, row, group, panel_prefix):
    f = fc[(fc.metro == metro) & (fc.measure == meas) & (fc.row.str.startswith(row)) & (fc.group == group) & (fc.panel.str.startswith(panel_prefix))]
    return f.iloc[0]
chk("Dallas level slope city hall", F("Dallas", "level", "A.", "pooled", "Dec 2019").slope, -1.9, 1, signed=True)
chk("Dallas level slope nearest", F("Dallas", "level", "B.", "pooled", "Dec 2019").slope, 1.5, 1, signed=True)
chk("Dallas level R2 city hall (mean of dates)", fc[(fc.metro == "Dallas") & (fc.measure == "level") & fc.row.str.startswith("A.")].r2.mean(), 0.005, 3, plain="about 0.005")
chk("Tampa level R2 city hall (mean)", fc[(fc.metro == "Tampa") & (fc.measure == "level") & fc.row.str.startswith("A.")].r2.mean(), 0.065, 3, plain="0.065 to 0.080")
chk("Tampa level R2 nearest (mean)", fc[(fc.metro == "Tampa") & (fc.measure == "level") & fc.row.str.startswith("B.")].r2.mean(), 0.080, 3, plain="0.065 to 0.080")
for lab, metro, a, bb in (("Dallas", "Dallas", 0.004, 0.019), ("Tampa", "Tampa", 0.117, 0.163)):
    chk(f"{lab} growth R2 city hall 2020-22", F(metro, "growth", "A.", "pooled", "2020").r2, a, 3, plain=f"{a}")
    chk(f"{lab} growth R2 nearest 2020-22", F(metro, "growth", "B.", "pooled", "2020").r2, bb, 3, plain=f"{bb}")
fw = fc[(fc.metro == "Dallas") & (fc.measure == "level") & fc.row.str.startswith("C.") & (fc.group == "Fort Worth")]
true("Fort Worth level slopes +8 to +10%", 8 <= fw.slope.min() and fw.slope.max() <= 10 and 0.09 <= fw.r2.min() and fw.r2.max() <= 0.11)
for lab, m_, k, claim in (("Dallas core $k", "Dallas", "primary", 221), ("Fort Worth core $k", "Dallas", "second", 183), ("Tampa core $k", "Tampa", "primary", 220), ("St. Petersburg core $k", "Tampa", "second", 227)):
    chk(lab, cores[(cores.metro == m_) & (cores.role == k)].median_value_k.iloc[0], claim, 0, plain=f"\\${claim}k")
chk("Dallas per-center growth 2020-22", F("Dallas", "growth", "C.", "Dallas", "2020").slope, 0.47, 2, signed=True)
chk("Dallas per-center growth 2023-25", F("Dallas", "growth", "C.", "Dallas", "2023").slope, -0.25, 2, signed=True)
chk("Fort Worth per-center growth 2020-22", F("Dallas", "growth", "C.", "Fort Worth", "2020").slope, -0.29, 2, signed=True)
chk("Fort Worth per-center growth 2023-25", F("Dallas", "growth", "C.", "Fort Worth", "2023").slope, 0.37, 2, signed=True)
chk("ZIPs nearer St. Petersburg", int((viz._sample(gd, "Tampa")[0].nearest_center == "St. Petersburg").sum()), 39, 0, plain="39 ZIP codes")

# ================================================================================================ section 2.3
for m in ("Phoenix", "Austin", "Atlanta", "Dallas", "Nashville"):
    true(f"wedge significant: {m}", wedge.loc[m, "perm_p"] < 0.01)
for m, claim in (("Tampa", 0.77), ("Charlotte", 0.15), ("Las Vegas", 0.08)):
    chk(f"wedge p {m}", wedge.loc[m, "perm_p"], claim, 2, plain=f"{claim}")
true("wedge directions", [wedge.loc[m, "mean_direction"] for m in ("Phoenix", "Austin", "Atlanta", "Dallas", "Nashville", "Las Vegas")] == ["NE", "NW", "N", "NE", "S", "SW"])
chk("Dallas cores in bottom two fifths", coreq.loc["Dallas", "pct_in_bottom_two_fifths"], 63, 0, plain="63\\%")
r2 = {m: sl[(sl.metro == m) & (sl.measure == "level") & (sl.distance == "city hall")].r2 for m in viz.METRO_ORDER}
true("Austin R2 0.15-0.24", f"{r2['Austin'].min():.2f} to {r2['Austin'].max():.2f}" == "0.15 to 0.24" and "R$^2$ 0.15 to 0.24" in TEX)
true("Nashville R2 0.26-0.37", f"{r2['Nashville'].min():.2f} to {r2['Nashville'].max():.2f}" == "0.26 to 0.37" and "0.26 to 0.37" in TEX)
def IO(m, col): return inout[(inout.metro == m) & (inout.period == "2023-25")].iloc[0][col]
for m, a, bb in (("Atlanta", -2.9, 1.5), ("Austin", -1.3, 0.4), ("Nashville", -1.7, 0.8)):
    chk(f"{m} inner 2023-25", IO(m, "inner_med_rel"), a, 1, signed=True); chk(f"{m} outer 2023-25", IO(m, "outer_med_rel"), bb, 1, signed=True)
    true(f"{m} inner/outer difference p<0.01", IO(m, "p_outer_vs_inner") < 0.01)
chk("Charlotte inner 2023-25", IO("Charlotte", "inner_med_rel"), -0.7, 1, signed=True)
true("Charlotte inner-outer difference not significant", IO("Charlotte", "p_outer_vs_inner") > 0.05)
cs = sect[(sect.metro == "Charlotte")]
sec = sect[(sect.metro == "Atlanta") & (sect.period == "pre-2020")].set_index("sector").median_rel_growth
chk("Atlanta north pre-2020", sec["N"], -3.7, 1, signed=True); chk("Atlanta south", sec["S"], 1.1, 1, signed=True); chk("Atlanta southeast", sec["SE"], 2.2, 1, signed=True)
chk("Dallas-FW cores pre-2020 (<10 mi of either hall)", reg["dallas_within10_either_hall_pre2020"], 2.4, 1, signed=True)
chk("Dallas-FW beyond", reg["dallas_beyond10_pre2020"], -0.5, 1, signed=True); chk("Dallas north beyond 10 mi", reg["dallas_north_beyond10_pre2020"], -3.5, 1, signed=True)
chk("Dallas south beyond 10 mi", reg["dallas_south_beyond10_pre2020"], 1.4, 1, signed=True)
chk("Phoenix far southeast", reg["phoenix_far_southeast_pre2020"], 2.6, 1, signed=True); chk("Phoenix inner core", reg["phoenix_inner_pre2020"], 0.9, 1, signed=True)
chk("Charlotte far south", reg["charlotte_far_south_2023_25"], -0.7, 1, signed=True); chk("Charlotte elsewhere beyond 30 mi", reg["charlotte_beyond30_elsewhere_2023_25"], 0.6, 1, signed=True)
chk("Charlotte far-south ZIPs", reg["charlotte_far_south_n"], 10, 0, plain="10 ZIP codes)")
true("seven of eight metros had larger growth dispersion pre-2020 than 2020-22", int((gsd.sd_pre2020 > gsd.sd_2020_22).sum()) == 7 and gsd.loc["Austin", "sd_pre2020"] < gsd.loc["Austin", "sd_2020_22"])
chk("Atlanta SD pre-2020", gsd.loc["Atlanta", "sd_pre2020"], 4.9, 1, plain="4.9 against 3.5"); chk("Atlanta SD 2020-22", gsd.loc["Atlanta", "sd_2020_22"], 3.5, 1)
chk("Dallas SD pre-2020", gsd.loc["Dallas", "sd_pre2020"], 4.2, 1, plain="4.2 against 1.9"); chk("Dallas SD 2020-22", gsd.loc["Dallas", "sd_2020_22"], 1.9, 1)

# ================================================================================================ section 2.4
def EX(view, p): return ex[(ex.view == view) & (ex.period == p)].iloc[0]
chk("within pre-2020", EX("within metro", "Pre-2020").slope_per5pp, -1.48, 2, signed=True)
chk("within 2020-22", EX("within metro", "2020–2022").slope_per5pp, -0.30, 2, signed=True)
chk("within 2023-25", EX("within metro", "2023–2025").slope_per5pp, 0.40, 2, signed=True)
chk("pooled 2020-22", EX("pooled", "2020–2022").slope_per5pp, 0.17, 2, signed=True); chk("pooled 2023-25", EX("pooled", "2023–2025").slope_per5pp, -0.10, 2, signed=True)
chk("pooled 2020-22 interval low", EX("pooled", "2020–2022").lo, -0.01, 2, signed=True); chk("pooled 2020-22 interval high", EX("pooled", "2020–2022").hi, 0.35, 2, signed=True)
chk("R2 pre-2020", EX("within metro", "Pre-2020").r2, 0.13, 2, plain="R$^2$ 0.13")
for p, claim in (("Pre-2020", -1.41), ("2020–2022", -0.26), ("2023–2025", 0.52)):
    chk(f"reliable-only {p}", EX("within metro", p).slope_reliable, claim, 2, signed=True)
chk("unreliable ZIPs in exposure sample", int(EX("within metro", "Pre-2020").n - EX("within metro", "Pre-2020").n_reliable), 233, 0, plain="233 ZIP codes")
chk("rank corr WFH-income", cm.loc["Median income (log)", "Work-from-home share"], 0.66, 2, signed=True)
chk("rank corr WFH-home value", cm.loc["Home value, Dec 2019 (log)", "Work-from-home share"], 0.74, 2, signed=True)
chk("rank corr WFH-management share", cm.loc["Management/professional share", "Work-from-home share"], 0.74, 2, signed=True)
chk("rank corr growth pre-2020 vs home value", cm.loc["Growth, pre-2020", "Home value, Dec 2019 (log)"], -0.72, 2, signed=True)
chk("rank corr WFH-single-family share (not 'tracks closely')", cm.loc["Single-family detached share", "Work-from-home share"], 0.15, 2)
C_ = lambda out, c: ctl[(ctl.out == out) & (ctl.ctl == c)].iloc[0]
def ci(x): lo, hi = [float(v) for v in x.ci.strip("[]").split(",")]; return lo, hi
for out, c, claim, lo_c, hi_c in (("2019_2022", "+ pre-2020 growth", 0.03, -0.13, 0.20), ("2022_2025", "+ pre-2020 growth", 0.13, -0.03, 0.30),
                                  ("2019_2022", "+ pre-2020 growth + income", -0.15, -0.36, 0.06), ("2022_2025", "+ pre-2020 growth + income", 0.00, -0.15, 0.15)):
    x = C_(out, c); lo, hi = ci(x)
    chk(f"controlled slope {out} {c}", float(x.slope), claim, 2, signed=(claim != 0)); chk("   interval low", lo, lo_c, 2, signed=True); chk("   interval high", hi, hi_c, 2, signed=True)
    true(f"   interval includes zero ({out}, {c})", lo <= 0 <= hi)
chk("controlled sample size", int(C_("2019_2022", "WFH only").n), 1073, 0, plain="1,073")
true("residual spread 8% to 24% larger", round(100 * (rsd.ratio.min() - 1)) == 8 and round(100 * (rsd.ratio.max() - 1)) == 24)

# ================================================================================================ section 2.5
bn = lambda m, bd, c: band[(band.metro == m) & (band.band == bd)].iloc[0][c]
chk("Atlanta inner Dec 2022", bn("Atlanta", "0-10 mi", "2022-12_med"), 85.1, 1, plain="85\\%"); chk("Atlanta inner Dec 2025", bn("Atlanta", "0-10 mi", "2025-12_med"), 83.0, 1, plain="83\\%")
chk("   interval low", bn("Atlanta", "0-10 mi", "2025-12_lo"), 80.5, 1); chk("   interval high", bn("Atlanta", "0-10 mi", "2025-12_hi"), 87.2, 1)
chk("Atlanta outer Dec 2025", bn("Atlanta", "30+ mi", "2025-12_med"), 104.8, 1, plain="about 105\\%")
chk("   outer interval low", bn("Atlanta", "30+ mi", "2025-12_lo"), 103.6, 1); chk("   outer interval high", bn("Atlanta", "30+ mi", "2025-12_hi"), 106.2, 1)
chk("Atlanta inner Jan 2018", bn("Atlanta", "0-10 mi", "2018-01_med"), 103.3, 1)
chk("Atlanta post-2020 fall in 3 years", 100 - bn("Atlanta", "0-10 mi", "2022-12_med"), 15, 0, plain="15 points in three years")
chk("Atlanta pre-2020 fall in 2 years", bn("Atlanta", "0-10 mi", "2018-01_med") - 100, 3, 0, plain="3 points in two years")
chk("Nashville inner Jan 2018", bn("Nashville", "0-10 mi", "2018-01_med"), 107.2, 1); chk("Nashville inner Dec 2022", bn("Nashville", "0-10 mi", "2022-12_med"), 102.9, 1)
chk("Nashville inner Dec 2025", bn("Nashville", "0-10 mi", "2025-12_med"), 97.1, 1); chk("   interval low", bn("Nashville", "0-10 mi", "2025-12_lo"), 93.6, 1); chk("   interval high", bn("Nashville", "0-10 mi", "2025-12_hi"), 100.0, 1)
chk("Austin inner Dec 2025", bn("Austin", "0-10 mi", "2025-12_med"), 95.6, 1); chk("   low", bn("Austin", "0-10 mi", "2025-12_lo"), 92.3, 1); chk("   high", bn("Austin", "0-10 mi", "2025-12_hi"), 97.4, 1)
chk("Austin outer Dec 2025", bn("Austin", "30+ mi", "2025-12_med"), 101.4, 1); chk("   low", bn("Austin", "30+ mi", "2025-12_lo"), 95.5, 1); chk("   high", bn("Austin", "30+ mi", "2025-12_hi"), 106.8, 1)
true("Austin outer interval spans 100", bn("Austin", "30+ mi", "2025-12_lo") < 100 < bn("Austin", "30+ mi", "2025-12_hi"))
chk("Tampa inner Dec 2025", bn("Tampa", "0-10 mi", "2025-12_med"), 105.8, 1); chk("Tampa outer Dec 2025", bn("Tampa", "30+ mi", "2025-12_med"), 106.7, 1)
chk("Tampa 10-20 band", bn("Tampa", "10-20 mi", "2025-12_med"), 97.7, 1); chk("Tampa 20-30 band", bn("Tampa", "20-30 mi", "2025-12_med"), 98.8, 1)
chk("Austin outer minimum (about 92%)", bn("Austin", "30+ mi", "min_med_all_dates"), 92, 0, plain="about 92\\%"); chk("Las Vegas outer minimum (about 94%)", bn("Las Vegas", "30+ mi", "min_med_all_dates"), 94, 0, plain="about 94\\%")
chk("Las Vegas outer Dec 2025 (about 96%)", bn("Las Vegas", "30+ mi", "2025-12_med"), 96, 0, plain="near 96\\%")
chk("Las Vegas outer ZIPs", int(bn("Las Vegas", "30+ mi", "n")), 7, 0, plain="only 7 ZIP codes")
# clusters
chk("ZIPs in the grouping", int(prof.zips.sum()), 1072, 0, plain="1,072 ZIP codes with complete series")
chk("Group 3 size", int(prof.loc[3, "zips"]), 89, 0, plain="Group 3 (89 ZIP codes"); chk("Group 4 size", int(prof.loc[4, "zips"]), 48, 0, plain="Group 4 (48 ZIP codes")
chk("Group 1 size", int(prof.loc[1, "zips"]), 520, 0, plain="520 and 415"); chk("Group 2 size", int(prof.loc[2, "zips"]), 415, 0)
chk("Group 4 median distance", prof.loc[4, "median_distance_mi"], 4, 0, plain="median 4 miles"); chk("Group 4 single-family", 100 * prof.loc[4, "median_sf_detached"], 18, 0, plain="18\\%")
true("other groups' single-family share 65% to 71%", [round(100 * prof.loc[k, "median_sf_detached"]) for k in (1, 2, 3)] == [71, 69, 65])
chk("Cramer's V metro", clus["cramers_v_metro"], 0.60, 2); chk("Cramer's V distance band", clus["cramers_v_band"], 0.18, 2)
chk("PC1 share", 100 * clus["pc1"], 71, 0, plain="explains 71\\%")
chk("share with silhouette < 0.25", 100 * clus["share_silhouette_below_025"], 25, 0, plain="25\\% of ZIP codes have a silhouette below 0.25")
chk("bootstrap ARI median", clus["ari_bootstrap_median"], 0.85, 2); chk("bootstrap ARI 5th percentile", clus["ari_bootstrap_p5"], 0.45, 2)
true("stable to starting point (ARI >= 0.99)", clus["ari_random_starts_min"] >= 0.99)
chk("silhouette min over k", sil.min(), 0.22, 2, plain="0.22 to 0.38"); chk("silhouette max over k", sil.max(), 0.38, 2)
chk("silhouette k=4", sil[4], 0.36, 2); chk("silhouette k=2", sil[2], 0.375, 3, plain="0.375")
chk("Group 3 share in Austin", comp.loc[2, "Austin"], 74, 0, plain="74\\% of them in Austin")

# ================================================================================================ section 2.6
true("834 of 1,082 remain flag-free", int(rb[(rb["sample"] == "flag-free ZIPs") & (rb.panel == "Dec 2019")].n.sum()) == 834)
w = rb.pivot_table(index=["metro", "measure", "panel"], columns="sample", values="slope"); w["d"] = w["flag-free ZIPs"] - w["all ZIPs"]
chk("max level-slope change", w.xs("level", level="measure")["d"].abs().max(), 6, 0, plain="up to about 6 points")
chk("mean level-slope change", w.xs("level", level="measure")["d"].mean(), 2, 0, plain="about 2 points")
chk("mean growth-slope change", w.xs("growth", level="measure")["d"].mean(), 0.00, 2, plain="0.00 on average")
chk("growth change min", w.xs("growth", level="measure")["d"].min(), -0.37, 2, signed=True); chk("growth change max", w.xs("growth", level="measure")["d"].max(), 0.59, 2, signed=True)
FFs = lambda m, meas, pn: rb[(rb.metro == m) & (rb.measure == meas) & (rb.panel == pn) & (rb["sample"] == "flag-free ZIPs")].iloc[0]
chk("Phoenix flag-free growth pre", FFs("Phoenix", "growth", "Pre-2020").slope, 0.09, 2, signed=True); chk("   2020-22", FFs("Phoenix", "growth", "2020–2022").slope, 0.03, 2, signed=True)
chk("   2023-25", FFs("Phoenix", "growth", "2023–2025").slope, -0.09, 2, signed=True)
chk("Atlanta flag-free 2020-22", FFs("Atlanta", "growth", "2020–2022").slope, 1.25, 2, signed=True)
x = FFs("Dallas", "growth", "2023–2025"); chk("Dallas flag-free 2023-25", x.slope, -0.35, 2, signed=True); chk("   interval low", x.lo, -0.57, 2, signed=True); chk("   interval high", x.hi, -0.12, 2, signed=True)
chk("Dallas all-ZIP 2023-25", S_("Dallas", "growth", "2023–2025").slope, -0.03, 2, signed=True)
true("Atlanta flag-free and all-ZIP 2020-22 intervals overlap", FFs("Atlanta", "growth", "2020–2022").lo < S_("Atlanta", "growth", "2020–2022").hi)
fv = gd[gd.balanced].merge(fl[["zip", "zhvi_incomplete", "metro_col_only", "acs_baseline_missing", "wfh_unreliable"]], on="zip", how="left")
anyf = fv[["zhvi_incomplete", "metro_col_only", "acs_baseline_missing", "wfh_unreliable"]].fillna(False).astype(bool).any(axis=1)
chk("flagged median value", fv.loc[anyf, "level_Dec 2019"].median() / 1e3, 213, 0, plain="\\$213k"); chk("unflagged median value", fv.loc[~anyf, "level_Dec 2019"].median() / 1e3, 269, 0, plain="\\$269k")
cd_ = cdef.assign(a=cdef["diff"].abs()); chk("ZCTA-centroid slope change, levels", cd_[cd_.measure == "level"].a.max(), 0.5, 1, plain="0.5 percentage points"); chk("   growth", cd_[cd_.measure == "growth"].a.max(), 0.06, 2, plain="0.06 points per year")
RP = lambda k, p: rent[(rent.series == k) & rent.period.str.startswith(p)].iloc[0]
chk("price slope 2020-22", RP("price", "2020").slope, 0.83, 2, signed=True); chk("rent slope 2020-22", RP("rent", "2020").slope, 0.41, 2, signed=True)
chk("price slope 2023-25", RP("price", "2023").slope, -0.07, 2, signed=True); chk("rent slope 2023-25", RP("rent", "2023").slope, 0.33, 2, signed=True)
chk("rent sample size", int(RP("price", "2020").n), 478, 0, plain="478 ZIP codes")
chk("outer ZIPs with rents at both ends", 100 * zo[zo.dist_band == "30+ mi"].zori_both_ends.mean(), 13, 0, plain="13\\%")

# ================================================================================================ summary / section 3 consistency
for tok in ("clear only in Atlanta", "Tampa's flattening does not hold", "depends on far-out ZIP codes", "In five of the eight metros",
            "$+$0.03 in 2020--22 and $+$0.13 in 2023--25", "falls to about zero", "overlaps strongly with income"):
    present("Summary wording", tok)
for tok in ("show no flattening", "five of the eight metros", "weakly separated"):
    present("Section 3 wording", tok)
true("no leftover wording: 'close to being the same'", "close to being the same" not in TEX)
true("no leftover wording: 'tracks income so closely'", "tracks income so closely" not in TEX)
true("no leftover wording: 'uninterpretable'", "uninterpretable" not in TEX)
true("no leftover wording: 'clearest signs of a donut'", "clearest signs of a donut" not in TEX)
true("no leftover wording: 'show nothing'", "show nothing" not in TEX)
true("no leftover wording: 'the plan said would point toward'", "the plan said would point" not in TEX)
true("no leftover wording: 'northwest of Las Vegas'", "northwest of Las Vegas" not in TEX)
true("no leftover wording: 'income, education and housing type'", "income, education and housing type" not in TEX)
true("no leftover wording: 'recovered to about 106'", "recovered to about 106" not in TEX)
true("Section 3 no longer says the two-center metros have centers at different price levels", "the two-center metros have centers at different price levels" not in TEX)

print(f"\nPASSED {len(passed)} checks; FAILED {len(failed)}")
for f in failed:
    print("  FAIL:", f)
sys.exit(1 if failed else 0)
