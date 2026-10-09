"""Extra computations behind docs/interpretation_audit.md.

These are checks on interpretive claims in the report (wedges, donut, humps, clusters, exposure pre-trend). They are NOT
part of the report's results; each one asks "does the number behind this sentence support it?"

    .venv/bin/python src/audit_checks.py     # prints everything and writes outputs/tables/audit_*.csv
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

import viz
import viz_eda

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
C, T = ROOT / "data" / "clean", ROOT / "outputs" / "tables"
rng = np.random.default_rng(0)
pd.set_option("display.width", 220)
pd.set_option("display.max_columns", 30)

gd = viz.gradient_data(C)
dist = pd.read_csv(C / "zip_distance.csv", dtype={"zip": str})
ref = pd.read_csv(ROOT / "data" / "reference" / "city_centers.csv")
acs = pd.read_csv(C / "zip_acs.csv", dtype={"zip": str})
flags = pd.read_csv(C / "zip_flags.csv", dtype={"zip": str})
d = gd.merge(dist[["zip", "zcta_lat", "zcta_lon", "dist_band"]], on="zip")

# -------------------------------------------------------------------------------- geometry helpers
def centers(metro):
    r = ref[ref["metro"] == metro]
    return r["lat"].to_numpy(), r["lon"].to_numpy()


def bearing_deg(lat0, lon0, lat, lon):
    """Compass bearing (0 = north, 90 = east) from the point (lat0, lon0) to each (lat, lon)."""
    p0, p1 = np.radians(lat0), np.radians(lat)
    dl = np.radians(lon - lon0)
    x = np.sin(dl) * np.cos(p1)
    y = np.cos(p0) * np.sin(p1) - np.sin(p0) * np.cos(p1) * np.cos(dl)
    return (np.degrees(np.arctan2(x, y)) + 360) % 360


COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
compass = lambda b: COMPASS[int(((b + 22.5) % 360) // 45)]


def origin(metro):
    lat, lon = centers(metro)
    return lat.mean(), lon.mean()          # midpoint for the two-center metros


def with_bearing(g, metro):
    lat0, lon0 = origin(metro)
    g = g.copy()
    g["bearing"] = bearing_deg(lat0, lon0, g["zcta_lat"].to_numpy(), g["zcta_lon"].to_numpy())
    return g


def mean_resultant(theta_deg):
    t = np.radians(theta_deg)
    return np.hypot(np.cos(t).mean(), np.sin(t).mean())


# ================================================================================ 1. wedge test (section 2.3)
print("\n=== 1. Is the top fifth of home values directional? (permutation test on bearing from the center) ===")
rows = []
for m in viz.METRO_ORDER:
    g = with_bearing(d[(d["metro_short"] == m) & d["level_Dec 2019"].notna() & (d["dist_cityhall_mi"] > 2)], m)
    top = g["level_Dec 2019"] >= g["level_Dec 2019"].quantile(0.8)
    R = mean_resultant(g.loc[top, "bearing"])
    sims = np.array([mean_resultant(g["bearing"].to_numpy()[rng.permutation(len(g))[: int(top.sum())]]) for _ in range(5000)])
    mb = (np.degrees(np.arctan2(np.sin(np.radians(g.loc[top, "bearing"])).mean(), np.cos(np.radians(g.loc[top, "bearing"])).mean())) + 360) % 360
    within60 = (np.abs(((g.loc[top, "bearing"] - mb + 180) % 360) - 180) <= 60).mean()
    # ring check: is the top fifth at a particular distance? median distance of top fifth vs others
    rows.append((m, int(top.sum()), compass(mb), round(mb), round(R, 2), round((sims >= R).mean(), 4), round(100 * within60),
                 round(g.loc[top, "dist_cityhall_mi"].median(), 1), round(g.loc[~top, "dist_cityhall_mi"].median(), 1)))
wedge = pd.DataFrame(rows, columns=["metro", "n_top_fifth", "mean_direction", "bearing_deg", "R", "perm_p", "pct_within_60deg", "median_mi_top", "median_mi_rest"])
print(wedge.to_string(index=False))
print("R = 0 means the top-fifth ZIPs point in all directions equally, R = 1 means all in one direction. perm_p compares with random fifths of the same ZIPs.")
wedge.to_csv(T / "audit_wedge.csv", index=False)

# ================================================================================ 2. growth-map directional claims
print("\n=== 2. Growth-map claims: median growth relative to the metro, by band and by sector ===")
rel = viz_eda.relative_growth(gd).set_index("zip")
dd = d.drop(columns=[c for c in d.columns if c.startswith("rel_")]).set_index("zip").join(rel[["rel_cum_2017_2019", "rel_cum_2019_2022", "rel_cum_2022_2025"]])
per = {"pre-2020": "rel_cum_2017_2019", "2020-22": "rel_cum_2019_2022", "2023-25": "rel_cum_2022_2025"}
rows = []
for m in viz.METRO_ORDER:
    g = dd[dd["metro_short"] == m]
    for pn, col in per.items():
        inner = g.loc[g["dist_cityhall_mi"] < 10, col].dropna()
        outer = g.loc[g["dist_cityhall_mi"] >= 30, col].dropna()
        rows.append((m, pn, len(inner), round(inner.median(), 2), len(outer), round(outer.median(), 2),
                     round(stats.mannwhitneyu(outer, inner).pvalue, 4) if len(inner) > 4 and len(outer) > 4 else np.nan))
band = pd.DataFrame(rows, columns=["metro", "period", "n_inner", "inner_med_rel", "n_outer", "outer_med_rel", "p_outer_vs_inner"])
print("rel growth = annualized growth minus the metro median (points per year); inner = <10 mi, outer = 30+ mi")
print(band.pivot(index="metro", columns="period", values=["inner_med_rel", "outer_med_rel"]).reindex(viz.METRO_ORDER).round(2).to_string())
band.to_csv(T / "audit_inner_outer_growth.csv", index=False)


def sector_table(m, col):
    g = with_bearing(dd[dd["metro_short"] == m].dropna(subset=[col, "zcta_lat"]), m)
    g["sector"] = [compass(b) for b in g["bearing"]]
    return g.groupby("sector")[col].agg(["size", "median"]).reindex(COMPASS).round(2)

print("\nAtlanta, pre-2020, median relative growth by compass sector from city hall (claim: north slow, south/southeast fast):")
print(sector_table("Atlanta", "rel_cum_2017_2019").T.to_string())
g = with_bearing(dd[(dd["metro_short"] == "Dallas")].dropna(subset=["rel_cum_2017_2019", "zcta_lat"]), "Dallas")
g["near_either"] = g["dist_cityhall_mi"].where(g["dist_nearest_mi"].notna(), np.nan)
g["core"] = g["dist_nearest_mi"] < 10
print("\nDallas-Fort Worth pre-2020 relative growth: within 10 mi of either hall vs beyond; beyond-10-mi ZIPs north vs south of the midpoint")
print("  within 10 mi of either hall: n=%d median %.2f | beyond: n=%d median %.2f" % (
    g["core"].sum(), g.loc[g["core"], "rel_cum_2017_2019"].median(), (~g["core"]).sum(), g.loc[~g["core"], "rel_cum_2017_2019"].median()))
north = g["bearing"].between(315, 360) | g["bearing"].between(0, 45)
south = g["bearing"].between(135, 225)
print("  beyond 10 mi, north (315-45 deg): n=%d median %.2f | south (135-225): n=%d median %.2f" % (
    (north & ~g["core"]).sum(), g.loc[north & ~g["core"], "rel_cum_2017_2019"].median(), (south & ~g["core"]).sum(), g.loc[south & ~g["core"], "rel_cum_2017_2019"].median()))
g = with_bearing(dd[dd["metro_short"] == "Phoenix"].dropna(subset=["rel_cum_2017_2019", "zcta_lat"]), "Phoenix")
se = g["bearing"].between(90, 180)
print("\nPhoenix pre-2020 relative growth: within 10 mi: n=%d median %.2f | 30+ mi and southeast (90-180 deg): n=%d median %.2f | 30+ mi elsewhere: n=%d median %.2f" % (
    (g["dist_cityhall_mi"] < 10).sum(), g.loc[g["dist_cityhall_mi"] < 10, "rel_cum_2017_2019"].median(),
    ((g["dist_cityhall_mi"] >= 30) & se).sum(), g.loc[(g["dist_cityhall_mi"] >= 30) & se, "rel_cum_2017_2019"].median(),
    ((g["dist_cityhall_mi"] >= 30) & ~se).sum(), g.loc[(g["dist_cityhall_mi"] >= 30) & ~se, "rel_cum_2017_2019"].median()))
print("\nCharlotte 2023-25 relative growth by sector (claim: slow core, and far-south ZIPs also slow):")
print(sector_table("Charlotte", "rel_cum_2022_2025").T.to_string())
g = with_bearing(dd[dd["metro_short"] == "Charlotte"].dropna(subset=["rel_cum_2022_2025", "zcta_lat"]), "Charlotte")
fs = (g["bearing"].between(135, 225)) & (g["dist_cityhall_mi"] >= 30)
print("  Charlotte 30+ mi and south (135-225 deg): n=%d median %.2f; 30+ mi elsewhere: n=%d median %.2f" % (fs.sum(), g.loc[fs, "rel_cum_2022_2025"].median(), ((g["dist_cityhall_mi"] >= 30) & ~fs).sum(), g.loc[(g["dist_cityhall_mi"] >= 30) & ~fs, "rel_cum_2022_2025"].median()))

# ================================================================================ 3. donut (section 2.5)
print("\n=== 3. Distance-band medians of the index relative to the metro, with bootstrap 95% intervals ===")
panel = pd.read_parquet(C / "zhvi_analysis_panel.parquet", columns=["zip", "date", "index_dec2019"])
P = viz_eda.path_matrix(panel, gd)
ddb = gd.drop(columns=["dist_band"], errors="ignore").merge(dist[["zip", "dist_band"]], on="zip").set_index("zip")
rows = []
for m in viz.METRO_ORDER:
    z = P.index[ddb.loc[P.index, "metro_short"] == m]
    relp = 100 * P.loc[z] / P.loc[z].median()
    bands = ddb.loc[z, "dist_band"]
    for b in viz_eda.BANDS:
        zz = z[bands.values == b]
        if len(zz) < 3:
            continue
        out = {"metro": m, "band": b, "n": len(zz), "2018-01_med": round(float(np.median(relp.loc[zz, pd.Timestamp("2018-01-31")])), 1),
               "2019-12_med": round(float(np.median(relp.loc[zz, pd.Timestamp("2019-12-31")])), 1),
               "min_med_all_dates": round(float(relp.loc[zz].median().min()), 1)}
        for dt in ("2022-12-31", "2025-12-31"):
            v = relp.loc[zz, pd.Timestamp(dt)].to_numpy()
            bs = np.array([np.median(rng.choice(v, len(v))) for _ in range(2000)])
            out[f"{dt[:7]}_med"] = round(np.median(v), 1)
            out[f"{dt[:7]}_lo"], out[f"{dt[:7]}_hi"] = np.round(np.percentile(bs, [2.5, 97.5]), 1)
        rows.append(out)
don = pd.DataFrame(rows)
print(don.to_string(index=False))
don.to_csv(T / "audit_band_bootstrap.csv", index=False)

# ================================================================================ 4. humps (section 2.2)
print("\n=== 4. Humps: where does the smooth curve peak, and is there a curved (quadratic) term? ===")
rows = []
for m in viz.METRO_ORDER:
    g, _, _ = viz._sample(gd, m)
    for lab in ("Dec 2019", "Dec 2025"):
        x, y = g["dist_cityhall_mi"].to_numpy(), np.log(g[f"level_{lab}"].to_numpy())
        sc = viz.smooth_curve(x, g[f"level_{lab}"].to_numpy(), log=True)
        peak = sc[0][np.argmax(sc[1])] if sc is not None else np.nan
        X = sm.add_constant(np.column_stack([x, x ** 2]))
        fit = sm.OLS(y, X).fit(cov_type="HC1")
        rows.append((m, lab, round(peak, 1), round(np.percentile(x, 95), 1), round(fit.params[2] * 1e3, 3), round(fit.pvalues[2], 4)))
hump = pd.DataFrame(rows, columns=["metro", "date", "lowess_peak_mi", "95pct_range_mi", "quad_coef_x1000", "quad_p_HC1"])
print(hump.to_string(index=False))
hump.to_csv(T / "audit_hump.csv", index=False)

# ================================================================================ 5. two-center price levels
print("\n=== 5. Do the two cores sit at different price levels? (median Dec 2019 value within 10 mi of each hall) ===")
for m, (a, b) in viz.TWO_CENTER.items():
    g = gd[(gd["metro_short"] == m) & gd["level_Dec 2019"].notna()].copy()
    lat, lon = centers(m)
    zz = dist.set_index("zip").loc[g["zip"]]
    out = []
    for k, nm in enumerate([a, b]):
        r = ref[(ref["metro"] == m)].iloc[[0, 1]] if False else None
    prim = ref[(ref["metro"] == m) & (ref["role"] == "primary")].iloc[0]
    sec = ref[(ref["metro"] == m) & (ref["role"] == "second_center")].iloc[0]
    for nm, c in ((a, prim), (b, sec)):
        dmi = viz.__dict__.get("haversine", None)
        p0, p1 = np.radians(c["lat"]), np.radians(zz["zcta_lat"].to_numpy())
        dl = np.radians(zz["zcta_lon"].to_numpy() - c["lon"])
        hav = np.sin((p1 - p0) / 2) ** 2 + np.cos(p0) * np.cos(p1) * np.sin(dl / 2) ** 2
        mi = 2 * 3958.76 * np.arcsin(np.sqrt(hav))
        v = g.loc[mi < 10, "level_Dec 2019"]
        out.append((nm, int((mi < 10).sum()), round(v.median() / 1e3)))
    print(m, "| " + " | ".join(f"{nm}: n={n}, median ${v}k" for nm, n, v in out))

# ================================================================================ 6. Phoenix: what drives the vanishing gradient?
print("\n=== 6. Phoenix level slope (Dec 2019, % per 10 mi) under different exclusions ===")
g, _, _ = viz._sample(gd, "Phoenix")
g = g.merge(flags[["zip", "zhvi_incomplete", "metro_col_only", "acs_baseline_missing", "wfh_unreliable"]], on="zip", how="left")
def slope(gs):
    f = viz.ols(gs["dist_cityhall_mi"], np.log(gs["level_Dec 2019"]))
    return f"{viz._pct_per_10mi(f['slope']):+.1f}% [{viz._pct_per_10mi(f['lo']):+.1f}, {viz._pct_per_10mi(f['hi']):+.1f}] n={f['n']}"
print("  all ZIPs:                         ", slope(g))
for fl in ("zhvi_incomplete", "metro_col_only", "acs_baseline_missing", "wfh_unreliable"):
    print(f"  drop {fl:<22s}:", slope(g[~g[fl].fillna(False).astype(bool)]), f"(removes {int(g[fl].fillna(False).astype(bool).sum())})")
print("  drop ZIPs beyond 60 mi:           ", slope(g[g['dist_cityhall_mi'] <= 60]), f"(removes {(g['dist_cityhall_mi'] > 60).sum()})")
print("  drop ZIPs beyond 40 mi:           ", slope(g[g['dist_cityhall_mi'] <= 40]), f"(removes {(g['dist_cityhall_mi'] > 40).sum()})")
flag_any = g[["zhvi_incomplete", "metro_col_only", "acs_baseline_missing", "wfh_unreliable"]].fillna(False).astype(bool).any(axis=1)
print("  flagged ZIPs: median distance %.1f mi, median Dec 2019 value $%dk | unflagged: %.1f mi, $%dk" % (
    g.loc[flag_any, "dist_cityhall_mi"].median(), g.loc[flag_any, "level_Dec 2019"].median() / 1e3,
    g.loc[~flag_any, "dist_cityhall_mi"].median(), g.loc[~flag_any, "level_Dec 2019"].median() / 1e3))
allm = gd[gd["balanced"]].merge(flags[["zip", "zhvi_incomplete", "metro_col_only", "acs_baseline_missing", "wfh_unreliable"]], on="zip", how="left")
fa = allm[["zhvi_incomplete", "metro_col_only", "acs_baseline_missing", "wfh_unreliable"]].fillna(False).astype(bool).any(axis=1)
print("  all metros, flagged vs unflagged median Dec 2019 value: $%dk vs $%dk (n=%d vs %d)" % (
    allm.loc[fa, "level_Dec 2019"].median() / 1e3, allm.loc[~fa, "level_Dec 2019"].median() / 1e3, fa.sum(), (~fa).sum()))

# ================================================================================ 7. clusters (section 2.5)
print("\n=== 7. How real are the four price-path groups? ===")
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_samples
X = np.log(P.to_numpy() / 100.0)
base = KMeans(n_clusters=4, n_init=20, random_state=0).fit(X)
labs = [KMeans(n_clusters=4, n_init=20, random_state=s).fit_predict(X) for s in range(1, 11)]
print("  stability across 10 random starts: adjusted Rand index vs the reported solution, min %.2f, median %.2f" % (
    min(adjusted_rand_score(base.labels_, l) for l in labs), np.median([adjusted_rand_score(base.labels_, l) for l in labs])))
# bootstrap stability: recluster resampled ZIPs, compare labels of the resampled ZIPs with the original labels
ari_b = []
for _ in range(40):
    idx = rng.choice(len(X), len(X))
    kb = KMeans(n_clusters=4, n_init=5, random_state=int(rng.integers(1e6))).fit(X[idx])
    ari_b.append(adjusted_rand_score(base.labels_, kb.predict(X)))
print("  bootstrap (40 resamples, recluster, label all ZIPs): adjusted Rand index vs reported solution: median %.2f, 5th pct %.2f" % (np.median(ari_b), np.percentile(ari_b, 5)))
metro_lab = gd.set_index("zip").loc[P.index, "metro_short"].to_numpy()
band_lab = dist.set_index("zip").loc[P.index, "dist_band"].to_numpy()
print("  agreement with metro labels (adjusted Rand): %.2f | with distance-band labels: %.2f" % (
    adjusted_rand_score(base.labels_, metro_lab), adjusted_rand_score(base.labels_, band_lab)))
def cramers_v(a, b):
    ct = pd.crosstab(a, b)
    chi2 = stats.chi2_contingency(ct)[0]
    n = ct.to_numpy().sum()
    return float(np.sqrt(chi2 / (n * (min(ct.shape) - 1))))
print("  Cramer's V: cluster vs metro %.2f | cluster vs distance band %.2f" % (cramers_v(base.labels_, metro_lab), cramers_v(base.labels_, band_lab)))
dm = dist.set_index("zip").loc[P.index, "dist_cityhall_mi"].to_numpy()
H = stats.kruskal(*[dm[base.labels_ == k] for k in range(4)])[0]
print("  distance explained by cluster membership (Kruskal-Wallis epsilon^2): %.3f" % (H / (len(dm) - 1)))
sf = acs.set_index("zip").loc[P.index, "sf_detached_share_2023"].to_numpy()
ok = ~np.isnan(sf)
H2 = stats.kruskal(*[sf[(base.labels_ == k) & ok] for k in range(4)])[0]
print("  single-family share explained by cluster membership (epsilon^2): %.3f" % (H2 / (ok.sum() - 1)))
s = silhouette_samples(X, base.labels_)
print("  silhouette by group:", {k + 1: round(s[base.labels_ == k].mean(), 2) for k in range(4)}, "| share of ZIPs with silhouette below 0.25: %.0f%%" % (100 * (s < 0.25).mean()))
# does a continuum explain it? 1st principal component of the paths
from sklearn.decomposition import PCA
pca = PCA(n_components=3).fit(X)
print("  variance share of the first three principal components of the paths:", np.round(pca.explained_variance_ratio_, 3))

# ================================================================================ 8. exposure with the pre-trend controlled
print("\n=== 8. Exposure slope with the pre-2020 trend and income controlled (within-metro, HC1 errors) ===")
xd = viz_eda.exposure_data(gd, acs)
for c in ["wfh_pct", "ann_cum_2017_2019", "log_income", "ann_cum_2019_2022", "ann_cum_2022_2025"]:
    xd[c + "_w"] = xd[c] - xd.groupby("metro_short")[c].transform("median")
xd = xd.dropna(subset=["wfh_pct_w", "ann_cum_2017_2019_w", "log_income_w"])
rows = []
for y in ("ann_cum_2019_2022_w", "ann_cum_2022_2025_w"):
    for name, cols in (("WFH only", ["wfh_pct_w"]), ("+ pre-2020 growth", ["wfh_pct_w", "ann_cum_2017_2019_w"]),
                       ("+ pre-2020 growth + income", ["wfh_pct_w", "ann_cum_2017_2019_w", "log_income_w"])):
        f = sm.OLS(xd[y], sm.add_constant(xd[cols])).fit(cov_type="HC1")
        b = 5 * f.params["wfh_pct_w"]
        lo, hi = 5 * f.conf_int().loc["wfh_pct_w"]
        rows.append((y.replace("ann_cum_", "").replace("_w", ""), name, round(b, 2), f"[{lo:+.2f}, {hi:+.2f}]", round(f.rsquared, 3), len(xd)))
ex = pd.DataFrame(rows, columns=["outcome (annualized growth)", "controls", "WFH slope per +5 pp", "95% CI (HC1)", "R2", "n"])
print(ex.to_string(index=False))
ex.to_csv(T / "audit_exposure_controls.csv", index=False)
print("(2019_2022 = 2020-22 growth; 2022_2025 = 2023-25 growth. Not in the report; shown only to judge how much the pre-trend matters.)")


# ================================================================================ 9. save the other numbers the report quotes
print("\n=== 9. Saving the numbers quoted in the report ===")
# Phoenix exclusions
rows = []
def sl(gs):
    f = viz.ols(gs["dist_cityhall_mi"], np.log(gs["level_Dec 2019"]))
    return viz._pct_per_10mi(f["slope"]), viz._pct_per_10mi(f["lo"]), viz._pct_per_10mi(f["hi"]), f["n"]
rows.append(("all ZIPs", *sl(g)))
for fl in ("zhvi_incomplete", "metro_col_only", "acs_baseline_missing", "wfh_unreliable"):
    keep = ~g[fl].fillna(False).astype(bool)
    rows.append((f"drop {fl}", *sl(g[keep])))
rows.append(("drop ZIPs beyond 60 mi", *sl(g[g["dist_cityhall_mi"] <= 60])))
rows.append(("drop ZIPs beyond 40 mi", *sl(g[g["dist_cityhall_mi"] <= 40])))
pd.DataFrame(rows, columns=["exclusion", "slope", "lo", "hi", "n"]).round(2).to_csv(T / "audit_phoenix_exclusions.csv", index=False)
fl_any = g[["zhvi_incomplete", "metro_col_only", "acs_baseline_missing", "wfh_unreliable"]].fillna(False).astype(bool).any(axis=1)
pd.DataFrame([("phoenix_flagged_median_mi", g.loc[fl_any, "dist_cityhall_mi"].median()), ("phoenix_unflagged_median_mi", g.loc[~fl_any, "dist_cityhall_mi"].median()),
              ("phoenix_flagged_median_value", g.loc[fl_any, "level_Dec 2019"].median()), ("phoenix_unflagged_median_value", g.loc[~fl_any, "level_Dec 2019"].median()),
              ("phoenix_wfh_unreliable_n", int(g["wfh_unreliable"].fillna(False).astype(bool).sum())),
              ("phoenix_wfh_unreliable_median_mi", g.loc[g["wfh_unreliable"].fillna(False).astype(bool), "dist_cityhall_mi"].median())],
             columns=["key", "value"]).round(1).to_csv(T / "audit_phoenix_flagged.csv", index=False)
# core price levels
rows = []
for m in viz.TWO_CENTER:
    gg = gd[(gd["metro_short"] == m) & gd["level_Dec 2019"].notna()]
    zz = dist.set_index("zip").loc[gg["zip"]]
    prim = ref[(ref["metro"] == m) & (ref["role"] == "primary")].iloc[0]
    sec = ref[(ref["metro"] == m) & (ref["role"] == "second_center")].iloc[0]
    for role, c in (("primary", prim), ("second", sec)):
        p0, p1 = np.radians(c["lat"]), np.radians(zz["zcta_lat"].to_numpy())
        dl = np.radians(zz["zcta_lon"].to_numpy() - c["lon"])
        mi = 2 * 3958.76 * np.arcsin(np.sqrt(np.sin((p1 - p0) / 2) ** 2 + np.cos(p0) * np.cos(p1) * np.sin(dl / 2) ** 2))
        rows.append((m, role, c["city"], int((mi < 10).sum()), round(gg.loc[mi < 10, "level_Dec 2019"].median() / 1e3)))
pd.DataFrame(rows, columns=["metro", "role", "city", "n_within_10mi", "median_value_k"]).to_csv(T / "audit_cores.csv", index=False)
rows = []
for m in viz.TWO_CENTER:
    h = gd[(gd["metro_short"] == m) & gd["level_Dec 2019"].notna()].copy(); h["q"] = pd.qcut(h["level_Dec 2019"], 5, labels=False); c = h["dist_nearest_mi"] < 10
    rows.append((m, int(c.sum()), round(100 * (h.loc[c, "q"] <= 1).mean())))
pd.DataFrame(rows, columns=["metro", "n_within_10mi_either_hall", "pct_in_bottom_two_fifths"]).to_csv(T / "audit_core_quintiles.csv", index=False)
# clusters
pc = PCA(n_components=3).fit(X).explained_variance_ratio_
cl = [("ari_random_starts_min", min(adjusted_rand_score(base.labels_, l) for l in labs)), ("ari_bootstrap_median", np.median(ari_b)), ("ari_bootstrap_p5", np.percentile(ari_b, 5)),
      ("ari_vs_metro", adjusted_rand_score(base.labels_, metro_lab)), ("ari_vs_band", adjusted_rand_score(base.labels_, band_lab)),
      ("cramers_v_metro", cramers_v(base.labels_, metro_lab)), ("cramers_v_band", cramers_v(base.labels_, band_lab)),
      ("eps2_distance", H / (len(dm) - 1)), ("eps2_singlefamily", H2 / (ok.sum() - 1)), ("share_silhouette_below_025", (s < 0.25).mean()),
      ("pc1", pc[0]), ("pc2", pc[1]), ("pc3", pc[2])] + [(f"silhouette_group{k + 1}", s[base.labels_ == k].mean()) for k in range(4)]
pd.DataFrame(cl, columns=["key", "value"]).round(3).to_csv(T / "audit_clusters.csv", index=False)
# residual spread of unreliable vs reliable
rows = []
xd2 = viz_eda.exposure_data(gd, acs)
for col, lab in (("ann_cum_2017_2019", "Pre-2020"), ("ann_cum_2019_2022", "2020-22"), ("ann_cum_2022_2025", "2023-25")):
    yv = xd2[col] - xd2.groupby("metro_short")[col].transform("median")
    rs = sm.OLS(yv, sm.add_constant(xd2["wfh_pct_dm"])).fit().resid
    rows.append((lab, rs[~xd2["unreliable"]].std(), rs[xd2["unreliable"]].std(), rs[xd2["unreliable"]].std() / rs[~xd2["unreliable"]].std()))
pd.DataFrame(rows, columns=["period", "sd_reliable", "sd_unreliable", "ratio"]).round(2).to_csv(T / "audit_residual_sd.csv", index=False)
# dispersion of growth, pre-2020 vs 2020-22
b_ = gd[gd["balanced"]].groupby("metro_short")[["ann_cum_2017_2019", "ann_cum_2019_2022", "ann_cum_2022_2025"]].std().reindex(viz.METRO_ORDER)
b_.columns = ["sd_pre2020", "sd_2020_22", "sd_2023_25"]
b_.round(2).to_csv(T / "audit_growth_sd.csv")
# slope shifts vs interval widths
sl_ = pd.read_csv(T / "gradient_slopes.csv"); rows = []
for m in viz.METRO_ORDER:
    x = sl_[(sl_.measure == "growth") & (sl_.distance == "city hall") & (sl_.metro == m)].set_index("panel").loc[["Pre-2020", "2020\u20132022", "2023\u20132025"]]
    sv, w = x.slope.to_numpy(), (x.hi - x.lo).to_numpy()
    rows.append((m, max(abs(sv[1] - sv[0]), abs(sv[2] - sv[1]), abs(sv[2] - sv[0])), w.mean()))
pd.DataFrame(rows, columns=["metro", "largest_shift", "mean_interval_width"]).assign(shifted=lambda d: d.largest_shift > d.mean_interval_width).round(2).to_csv(T / "audit_slope_shifts.csv", index=False)
# sector medians quoted in the maps paragraph
rows = []
for m, col, pn in (("Atlanta", "rel_cum_2017_2019", "pre-2020"), ("Charlotte", "rel_cum_2022_2025", "2023-25")):
    t_ = sector_table(m, col)
    for sec_, r in t_.iterrows():
        rows.append((m, pn, sec_, r["size"], r["median"]))
pd.DataFrame(rows, columns=["metro", "period", "sector", "n", "median_rel_growth"]).to_csv(T / "audit_sector_medians.csv", index=False)
print("saved audit_phoenix_exclusions, audit_phoenix_flagged, audit_cores, audit_core_quintiles, audit_clusters, audit_residual_sd, audit_growth_sd, audit_slope_shifts, audit_sector_medians")

# regional medians quoted in the maps paragraph (relative growth, points per year)
rows = []
gg = with_bearing(dd[(dd["metro_short"] == "Dallas")].dropna(subset=["rel_cum_2017_2019", "zcta_lat"]), "Dallas")
core_ = gg["dist_nearest_mi"] < 10
north_ = gg["bearing"].between(315, 360) | gg["bearing"].between(0, 45)
south_ = gg["bearing"].between(135, 225)
rows += [("dallas_within10_either_hall_pre2020", gg.loc[core_, "rel_cum_2017_2019"].median()), ("dallas_beyond10_pre2020", gg.loc[~core_, "rel_cum_2017_2019"].median()),
         ("dallas_north_beyond10_pre2020", gg.loc[north_ & ~core_, "rel_cum_2017_2019"].median()), ("dallas_south_beyond10_pre2020", gg.loc[south_ & ~core_, "rel_cum_2017_2019"].median())]
gp = with_bearing(dd[dd["metro_short"] == "Phoenix"].dropna(subset=["rel_cum_2017_2019", "zcta_lat"]), "Phoenix")
se_ = gp["bearing"].between(90, 180)
rows += [("phoenix_inner_pre2020", gp.loc[gp["dist_cityhall_mi"] < 10, "rel_cum_2017_2019"].median()),
         ("phoenix_far_southeast_pre2020", gp.loc[(gp["dist_cityhall_mi"] >= 30) & se_, "rel_cum_2017_2019"].median())]
gc = with_bearing(dd[dd["metro_short"] == "Charlotte"].dropna(subset=["rel_cum_2022_2025", "zcta_lat"]), "Charlotte")
fs_ = gc["bearing"].between(135, 225) & (gc["dist_cityhall_mi"] >= 30)
rows += [("charlotte_far_south_2023_25", gc.loc[fs_, "rel_cum_2022_2025"].median()), ("charlotte_far_south_n", int(fs_.sum())),
         ("charlotte_beyond30_elsewhere_2023_25", gc.loc[(gc["dist_cityhall_mi"] >= 30) & ~fs_, "rel_cum_2022_2025"].median())]
pd.DataFrame(rows, columns=["key", "value"]).round(2).to_csv(T / "audit_regional.csv", index=False)
print("saved audit_regional")
