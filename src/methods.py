"""Preliminary results for the methodology submission (notebook 02 and report/Team10_Methodology.tex).

Everything here builds on the EDA data: the same 1,082 ZIPs that have a full price history ("balanced"), the same
distance (miles to the nearer city hall) and the same 2015-2019 ACS baseline. Four pieces:

  event_study     - how the price gradient moves year by year relative to Dec 2019 (SQ1), with two kinds of interval
  mixed_model     - growth on work-from-home share with county random effects (SQ2)
  moran           - is there spatial correlation left in the residuals? (justifies the interval and CV choices)
  ml_cv           - supervised models scored on metros they never saw (SQ2, and a check on SQ1)
  cluster_methods - k-means vs hierarchical vs Gaussian mixture on the price paths (SQ3)
"""
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

import viz
import viz_eda

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean"   # not "C": patsy formulas call C(...) and look the name up in this module
SEED = 0
METROS = viz.METRO_ORDER
YEARS = list(range(2017, 2026))


# ----------------------------------------------------------------------------- data
def load():
    """Returns gd (one row per ZIP: growth, distance, balanced flag, county, lat/lon) and xd (the exposure sample)."""
    gd = viz.gradient_data(CLEAN)
    dist = pd.read_csv(CLEAN / "zip_distance.csv", dtype={"zip": str})[["zip", "county", "zcta_lat", "zcta_lon"]]
    gd = gd.merge(dist, on="zip", how="left")
    gd["county_id"] = gd["metro_short"] + " / " + gd["county"].fillna("unknown")
    acs = pd.read_csv(CLEAN / "zip_acs.csv", dtype={"zip": str})
    xd = viz_eda.exposure_data(gd, acs)
    xd["log_value19"] = np.log(xd["zhvi_dec2019"])
    xd["log_pop"] = np.log(xd["pop_2019"].where(xd["pop_2019"] > 0))
    xd["mgmt_pct"] = 100 * xd["occ_mgmt_biz_sci_arts_share_2019"]
    xd["sfd_pct"] = 100 * xd["sf_detached_share_2019"]
    xd["mf20_pct"] = 100 * xd["units_20plus_share_2019"]
    return gd, xd


def annual_log_values(gd):
    """ZIP x year matrix of 100 * log(home value) every December 2017-2025, for the balanced ZIPs."""
    p = pd.read_parquet(CLEAN / "zhvi_analysis_panel.parquet", columns=["zip", "date", "log_zhvi"])
    p = p[(p["date"].dt.month == 12) & (p["date"].dt.year.isin(YEARS))]
    m = p.assign(year=p["date"].dt.year).pivot(index="zip", columns="year", values="log_zhvi") * 100
    keep = gd.loc[gd["balanced"], "zip"]
    return m.loc[m.index.intersection(keep)].dropna(how="any")


def _blocks(df, cell=0.25):
    """Spatial blocks: a grid of about 15 x 17 mile cells within each metro. Used to resample neighbors together."""
    return (df["metro_short"] + "|" + np.floor(df["zcta_lat"] / cell).astype(int).astype(str) + "|"
            + np.floor(df["zcta_lon"] / cell).astype(int).astype(str))


# ----------------------------------------------------------------------------- 1. event study
def _slopes(y, x, metro, w=None):
    """Within-metro slope of every column of y on x. Equivalent to the event-study coefficient on distance x year when
    the model has ZIP fixed effects and metro-by-year fixed effects (the reference year drops out of y)."""
    yd = y - pd.DataFrame(y).groupby(metro).transform("mean").to_numpy()
    xd_ = x - pd.Series(x).groupby(metro).transform("mean").to_numpy()
    return (xd_[:, None] * yd).sum(0) / (xd_ ** 2).sum()


def event_study(gd, ref=2019, B=1000):
    """Coefficient on (miles / 10) by year, relative to December `ref`, as % change in home value per 10 miles out.
    Two intervals: ordinary (HC1-style, treats ZIPs as independent) and a spatial block bootstrap (resamples whole
    grid cells of neighboring ZIPs, within metro). Returns (long table, summary table)."""
    rng = np.random.default_rng(SEED)
    L = annual_log_values(gd)
    d = gd.set_index("zip").loc[L.index].copy()
    d["block"] = _blocks(d)
    yrs = [y for y in YEARS if y != ref]
    Y = (L[yrs].to_numpy() - L[[ref]].to_numpy())
    x = d["dist_nearest_mi"].to_numpy() / 10
    out, boots = [], {}
    available_metros = [m for m in METROS if (d["metro_short"] == m).any()]
    pooled_name = "All eight (within-metro)" if len(available_metros) == 8 else f"All {len(available_metros)} (within-metro)"
    scopes = [(pooled_name, np.ones(len(d), bool))] + [(m, (d["metro_short"] == m).to_numpy()) for m in available_metros]
    for name, sel in scopes:
        Ys, xs, ms, bl = Y[sel], x[sel], d["metro_short"].to_numpy()[sel], d["block"].to_numpy()[sel]
        beta = _slopes(Ys, xs, ms)
        # ordinary interval: heteroskedasticity-robust (HC1) SE of the within-metro regression
        yd = Ys - pd.DataFrame(Ys).groupby(ms).transform("mean").to_numpy()
        xdm = xs - pd.Series(xs).groupby(ms).transform("mean").to_numpy()
        n, k = len(xs), 1 + len(set(ms))
        res = yd - xdm[:, None] * beta
        se = np.sqrt(((xdm[:, None] * res) ** 2).sum(0) * n / (n - k)) / (xdm ** 2).sum()
        # block bootstrap, stratified by metro so every draw keeps all the metros
        cells = {m: pd.Series(np.arange(len(bl))[ms == m]).groupby(bl[ms == m]).apply(list).tolist() for m in sorted(set(ms))}   # sorted: set order changes between runs
        draws = np.empty((B, len(yrs)))
        for b in range(B):
            idx = []
            for m, cl in cells.items():
                pick = rng.integers(0, len(cl), len(cl))
                idx.extend(i for j in pick for i in cl[j])
            idx = np.array(idx)
            draws[b] = _slopes(Ys[idx], xs[idx], ms[idx])
        boots[name] = draws
        lo, hi = np.percentile(draws, [2.5, 97.5], axis=0)
        for j, yr in enumerate(yrs):
            out.append({"scope": name, "year": yr, "beta": beta[j], "naive_lo": beta[j] - 1.96 * se[j],
                        "naive_hi": beta[j] + 1.96 * se[j], "boot_lo": lo[j], "boot_hi": hi[j], "n": int(sel.sum()),
                        "boot_se": draws[:, j].std(ddof=1), "basic_lo": 2 * beta[j] - hi[j], "basic_hi": 2 * beta[j] - lo[j]})
        out.append({"scope": name, "year": ref, "beta": 0.0, "naive_lo": 0.0, "naive_hi": 0.0, "boot_lo": 0.0,
                    "boot_hi": 0.0, "n": int(sel.sum()), "boot_se": 0.0, "basic_lo": 0.0, "basic_hi": 0.0})
    tab = pd.DataFrame(out).sort_values(["scope", "year"]).reset_index(drop=True)
    # summary: pre-trend, 2022, 2025, and whether the 2022-to-2025 change is distinguishable from zero
    rows = []
    for name, _ in scopes:
        t = tab[tab["scope"] == name].set_index("year")
        j22, j25 = yrs.index(2022), yrs.index(2025)
        diff = boots[name][:, j25] - boots[name][:, j22]
        w_naive = (t.loc[2022, "naive_hi"] - t.loc[2022, "naive_lo"])
        w_boot = (t.loc[2022, "boot_hi"] - t.loc[2022, "boot_lo"])
        rows.append({"scope": name, "n": t["n"].iloc[0],
                     "pre-trend 2017": t.loc[2017, "beta"], "2018": t.loc[2018, "beta"], "2022": t.loc[2022, "beta"],
                     "2025": t.loc[2025, "beta"], "2022 lo": t.loc[2022, "boot_lo"], "2022 hi": t.loc[2022, "boot_hi"],
                     "2025 lo": t.loc[2025, "boot_lo"], "2025 hi": t.loc[2025, "boot_hi"],
                     "2025 minus 2022": t.loc[2025, "beta"] - t.loc[2022, "beta"],
                     "diff lo": np.percentile(diff, 2.5), "diff hi": np.percentile(diff, 97.5), "diff se": diff.std(ddof=1),
                     "diff basic lo": 2 * (t.loc[2025, "beta"] - t.loc[2022, "beta"]) - np.percentile(diff, 97.5),
                     "diff basic hi": 2 * (t.loc[2025, "beta"] - t.loc[2022, "beta"]) - np.percentile(diff, 2.5),
                     "boot/naive width (2022)": w_boot / w_naive})
    return tab, pd.DataFrame(rows)


# ----------------------------------------------------------------------------- 2. mixed-effects model
def _exposure_frame(xd):
    """The ZIP codes and standardized variables used by equation (2): same sample and scaling for every model."""
    x = xd.dropna(subset=["log_income", "log_value19", "sfd_pct", "mf20_pct", "ann_cum_2017_2019", "ann_cum_2019_2022",
                          "ann_cum_2022_2025", "county_id"]).copy()
    x["wfh5"] = x["wfh_pct"] / 5
    x["dist10"] = x["dist_nearest_mi"] / 10
    x["log_income_z"] = (x["log_income"] - x["log_income"].mean()) / x["log_income"].std()
    x["log_value_z"] = (x["log_value19"] - x["log_value19"].mean()) / x["log_value19"].std()
    x["sfd_pct10"], x["mf20_pct10"] = x["sfd_pct"] / 10, x["mf20_pct"] / 10
    x["pre"] = x["ann_cum_2017_2019"]
    return x.reset_index(drop=True)


EXPOSURE_BASE = ["wfh5", "dist10", "log_income_z", "log_value_z", "sfd_pct10", "mf20_pct10"]
EXPOSURE_OUTCOMES = [("ann_cum_2019_2022", "2020-22"), ("ann_cum_2022_2025", "2023-25")]
EXPOSURE_CONTROLS = [(EXPOSURE_BASE, "controls"), (EXPOSURE_BASE + ["pre"], "controls + pre-2020 growth")]


def exposure_block_bootstrap(x, B=1000):
    """The OLS version of equation (2) refit on spatial block-bootstrap resamples (the same grid cells as the event study,
    redrawn with replacement within each metro). The county random intercept is left out here: a mixed model refit 1,000
    times is slow, and redrawing whole cells already lets neighbors move together.
    Returns one row per outcome and control set: the coefficient on work-from-home share, the bootstrap standard error, and
    four 95% intervals from the same resamples: percentile, basic (reverse percentile), symmetric (estimate +- 1.96 SE) and
    BCa. lo/hi hold the BCa interval, which is the one the document reports. The BCa acceleration comes from a jackknife that
    deletes one grid cell at a time."""
    from scipy import stats
    rng = np.random.default_rng(SEED)
    blocks = _blocks(x).to_numpy()
    metro = x["metro_short"].to_numpy()
    cells = {m: pd.Series(np.arange(len(x))[metro == m]).groupby(blocks[metro == m]).apply(list).tolist() for m in sorted(set(metro))}
    dummies = pd.get_dummies(x["metro_short"], drop_first=True).astype(float).to_numpy()
    designs = {name: np.c_[np.ones(len(x)), x[cols].to_numpy(float), dummies] for cols, name in EXPOSURE_CONTROLS}
    ys = {o: x[o].to_numpy(float) for o, _ in EXPOSURE_OUTCOMES}
    coef = lambda X, y: np.linalg.lstsq(X, y, rcond=None)[0][1]                  # column 1 = wfh5
    draws = {(o, n): np.empty(B) for o, _ in EXPOSURE_OUTCOMES for _, n in EXPOSURE_CONTROLS}
    for b in range(B):
        idx = []
        for m, cl in cells.items():
            pick = rng.integers(0, len(cl), len(cl))
            idx.extend(i for j in pick for i in cl[j])
        idx = np.array(idx)
        for out, _ in EXPOSURE_OUTCOMES:
            for _, n in EXPOSURE_CONTROLS:
                draws[(out, n)][b] = coef(designs[n][idx], ys[out][idx])
    rows = []
    for out, lab in EXPOSURE_OUTCOMES:
        for cols, n in EXPOSURE_CONTROLS:
            d, est = draws[(out, n)], coef(designs[n], ys[out])
            se = d.std(ddof=1)
            pct = np.percentile(d, [2.5, 97.5])
            jk = np.array([coef(designs[n][blocks != bk], ys[out][blocks != bk]) for bk in np.unique(blocks)])
            dev = jk.mean() - jk
            accel = (dev ** 3).sum() / (6 * ((dev ** 2).sum()) ** 1.5)
            z0 = stats.norm.ppf((d < est).mean())
            za = stats.norm.ppf([0.025, 0.975])
            bca = np.percentile(d, 100 * stats.norm.cdf(z0 + (z0 + za) / (1 - accel * (z0 + za))))
            rows.append({"outcome": lab, "controls": n, "model": "OLS, spatial block bootstrap", "wfh_per5pp": est, "se": se,
                         "lo": bca[0], "hi": bca[1], "n": int(len(x)), "counties": int(x["county_id"].nunique()),
                         "county_share_of_variance": np.nan, "pct_lo": pct[0], "pct_hi": pct[1],
                         "basic_lo": 2 * est - pct[1], "basic_hi": 2 * est - pct[0],
                         "sym_lo": est - 1.96 * se, "sym_hi": est + 1.96 * se, "boot_mean": d.mean(), "bias_z0": z0, "accel": accel})
    return pd.DataFrame(rows)


def mixed_model(xd, B=1000):
    """Growth on pre-2020 work-from-home share with metro fixed effects and a random intercept for county.
    Compared with plain OLS (HC1), OLS with county-clustered errors, and OLS with a spatial block-bootstrap interval."""
    import statsmodels.formula.api as smf
    x = _exposure_frame(xd)
    rows = []
    for out, lab in EXPOSURE_OUTCOMES:
        for cols, cname in EXPOSURE_CONTROLS:
            f = f"{out} ~ {' + '.join(cols)} + C(metro_short)"
            ols = smf.ols(f, data=x).fit(cov_type="HC1")
            cl = smf.ols(f, data=x).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(x["county_id"])[0]})
            mm = smf.mixedlm(f, data=x, groups=x["county_id"]).fit(reml=True, method="lbfgs")
            icc = float(mm.cov_re.iloc[0, 0] / (mm.cov_re.iloc[0, 0] + mm.scale))
            for label, fit in [("OLS (HC1)", ols), ("OLS, clustered by county", cl), ("Mixed (county random intercept)", mm)]:
                b, se = fit.params["wfh5"], fit.bse["wfh5"]
                rows.append({"outcome": lab, "controls": cname, "model": label, "wfh_per5pp": b, "se": se,
                             "lo": b - 1.96 * se, "hi": b + 1.96 * se, "n": int(len(x)),
                             "counties": int(x["county_id"].nunique()), "county_share_of_variance": icc if "Mixed" in label else np.nan})
    return pd.concat([pd.DataFrame(rows), exposure_block_bootstrap(x, B)], ignore_index=True)


# ----------------------------------------------------------------------------- 3. spatial correlation
def moran(xd, k=8, perms=999):
    """Moran's I of within-metro growth and of the residuals after the controls, using each ZIP's k nearest neighbors."""
    import statsmodels.formula.api as smf
    from sklearn.neighbors import NearestNeighbors
    rng = np.random.default_rng(SEED)
    x = xd.dropna(subset=["log_income", "log_value19", "sfd_pct", "mf20_pct", "zcta_lat", "zcta_lon"]).copy().reset_index(drop=True)
    x["wfh5"], x["dist10"] = x["wfh_pct"] / 5, x["dist_nearest_mi"] / 10
    xy = np.c_[x["zcta_lat"] * 69.0, x["zcta_lon"] * 69.0 * np.cos(np.radians(x["zcta_lat"]))]
    nn = NearestNeighbors(n_neighbors=k + 1).fit(xy)
    _, idx = nn.kneighbors(xy)
    nbr = idx[:, 1:]

    def I(z):
        z = z - z.mean()
        return (z * z[nbr].mean(1)).sum() / (z * z).sum()

    rows = []
    for out, lab in [("ann_cum_2017_2019", "pre-2020"), ("ann_cum_2019_2022", "2020-22"), ("ann_cum_2022_2025", "2023-25")]:
        f = f"{out} ~ wfh5 + dist10 + log_income + log_value19 + sfd_pct + mf20_pct + C(metro_short)"
        resid = smf.ols(f, data=x).fit().resid.to_numpy()
        for what, z in [("growth minus metro median", x[f"{out}_dm"].to_numpy()), ("residual after controls", resid)]:
            obs = I(z)
            sim = np.array([I(rng.permutation(z)) for _ in range(perms)])
            rows.append({"period": lab, "variable": what, "morans_I": obs, "p_value": (1 + (sim >= obs).sum()) / (perms + 1)})
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------- 4. supervised ML, leave-one-metro-out
FEATURE_SETS = {
    "A. Place and housing": ["dist_nearest_mi", "log_value_dm", "sfd_pct", "mf20_pct", "log_pop"],
    "B. A + income and occupation": ["dist_nearest_mi", "log_value_dm", "sfd_pct", "mf20_pct", "log_pop", "log_income_dm", "mgmt_pct"],
    "C. B + work-from-home share": ["dist_nearest_mi", "log_value_dm", "sfd_pct", "mf20_pct", "log_pop", "log_income_dm", "mgmt_pct", "wfh_pct_dm"],
    "D. C + pre-2020 growth": ["dist_nearest_mi", "log_value_dm", "sfd_pct", "mf20_pct", "log_pop", "log_income_dm", "mgmt_pct", "wfh_pct_dm", "pre_growth_dm"],
}
NICE = {"dist_nearest_mi": "Miles from center", "log_value_dm": "Home value, Dec 2019 (log, vs metro)",
        "sfd_pct": "Detached houses (%)", "mf20_pct": "Buildings with 20+ units (%)", "log_pop": "Population (log)",
        "log_income_dm": "Household income (log, vs metro)", "mgmt_pct": "Management/professional jobs (%)",
        "wfh_pct_dm": "Work-from-home share (vs metro)", "pre_growth_dm": "Growth before 2020 (vs metro)"}


def ml_data(xd):
    x = xd.dropna(subset=["log_income", "log_value19", "sfd_pct", "mf20_pct", "log_pop", "mgmt_pct", "ann_cum_2017_2019"]).copy()
    for src, dst in [("log_value19", "log_value_dm"), ("log_income", "log_income_dm"), ("ann_cum_2017_2019", "pre_growth_dm")]:
        x[dst] = x[src] - x.groupby("metro_short")[src].transform("median")
    return x.reset_index(drop=True)


def _models():
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import Lasso, Ridge
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    return {
        "Ridge": (make_pipeline(StandardScaler(), Ridge()), {"ridge__alpha": [0.1, 1, 10, 100]}),
        "Lasso": (make_pipeline(StandardScaler(), Lasso(max_iter=20000)), {"lasso__alpha": [0.003, 0.01, 0.03, 0.1]}),
        "Random forest": (RandomForestRegressor(n_estimators=150, random_state=SEED, n_jobs=-1),
                          {"max_depth": [4, 8, None], "min_samples_leaf": [5, 15]}),
        "Gradient boosting": (GradientBoostingRegressor(random_state=SEED, subsample=0.8),
                              {"n_estimators": [100, 300], "max_depth": [2, 3], "learning_rate": [0.03]}),
    }


def ml_cv(x, target, sets=None, models=None, perm_set=None):
    """Leave-one-metro-out. For each of the eight metros: tune on the other seven (inner GroupKFold by metro), then predict
    the held-out metro. Out-of-sample R2 compares with always predicting the training mean. Also runs ordinary random
    5-fold CV on the same data to show how much it flatters the models. Permutation importance (held-out metro) is saved
    for `perm_set` with the random forest."""
    from sklearn.base import clone
    from sklearn.inspection import permutation_importance
    from sklearn.model_selection import GridSearchCV, GroupKFold, KFold
    sets = sets or list(FEATURE_SETS)
    mods = _models()
    models = models or list(mods)
    y = x[target].to_numpy()
    g = x["metro_short"].to_numpy()
    rows, imp, preds = [], [], {}
    for sname in sets:
        cols = FEATURE_SETS[sname]
        X = x[cols].to_numpy()
        for mname in models:
            est, grid = mods[mname]
            pred = np.zeros(len(y))
            base = np.zeros(len(y))
            for m in METROS:
                te, tr = g == m, g != m
                gs = GridSearchCV(clone(est), grid, cv=GroupKFold(n_splits=4), scoring="neg_mean_squared_error", n_jobs=1)
                gs.fit(X[tr], y[tr], groups=g[tr])
                pred[te] = gs.predict(X[te])
                base[te] = y[tr].mean()
                if perm_set == sname and mname == "Random forest":
                    r = permutation_importance(gs.best_estimator_, X[te], y[te], n_repeats=10, random_state=SEED,
                                               scoring="neg_mean_squared_error")
                    imp.append(pd.DataFrame({"feature": cols, "importance": r.importances_mean, "held_out": m}))
            sse, sst = ((y - pred) ** 2).sum(), ((y - base) ** 2).sum()
            # random 5-fold, same tuned-model family (hyperparameters from a single inner search on all data: good enough for the contrast)
            rp = np.zeros(len(y))
            for tr, te in KFold(5, shuffle=True, random_state=SEED).split(X):
                gs = GridSearchCV(clone(est), grid, cv=KFold(4, shuffle=True, random_state=SEED), scoring="neg_mean_squared_error")
                gs.fit(X[tr], y[tr])
                rp[te] = gs.predict(X[te])
            rows.append({"features": sname, "model": mname, "target": target, "RMSE": np.sqrt(sse / len(y)),
                         "MAE": np.abs(y - pred).mean(), "R2_leave_one_metro_out": 1 - sse / sst,
                         "R2_random_5fold": 1 - ((y - rp) ** 2).sum() / ((y - y.mean()) ** 2).sum(),
                         "baseline_RMSE": np.sqrt(sst / len(y))})
            preds[(sname, mname)] = pred
    imp = pd.concat(imp) if imp else pd.DataFrame()
    return pd.DataFrame(rows), imp, preds


def lasso_selection(x, target, set_name):
    """Which features the lasso keeps (standardized coefficients) when tuned on all eight metros with grouped CV."""
    from sklearn.linear_model import LassoCV
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    cols = FEATURE_SETS[set_name]
    cv = list(GroupKFold(8).split(x[cols], x[target], x["metro_short"]))
    p = make_pipeline(StandardScaler(), LassoCV(cv=cv, max_iter=20000, alphas=40))
    p.fit(x[cols], x[target])
    return pd.Series(p[-1].coef_, index=[NICE[c] for c in cols], name="coefficient")


# ----------------------------------------------------------------------------- 5. clustering comparison
def cluster_methods(P, ks=range(2, 8)):
    """Three clustering methods on the same price paths. k-means and Ward on the log index; the Gaussian mixture on the
    first five principal components (full covariance is not estimable on 96 monthly columns)."""
    from scipy.cluster.hierarchy import fcluster, linkage
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.metrics import adjusted_rand_score, silhouette_score
    from sklearn.mixture import GaussianMixture
    X = np.log(P.to_numpy() / 100.0)
    pca = PCA(n_components=5, random_state=SEED).fit(X)
    Z = pca.transform(X)
    link = linkage(X, method="ward")
    rows, labs = [], {}
    for k in ks:
        km = KMeans(k, n_init=20, random_state=SEED).fit_predict(X)
        wd = fcluster(link, k, criterion="maxclust") - 1
        gm = GaussianMixture(k, covariance_type="full", n_init=5, random_state=SEED).fit(Z)
        gl = gm.predict(Z)
        for name, lab, extra in [("k-means", km, np.nan), ("Ward hierarchical", wd, np.nan), ("Gaussian mixture", gl, gm.bic(Z))]:
            rows.append({"k": k, "method": name, "silhouette": silhouette_score(X, lab), "BIC": extra,
                         "smallest_group": int(np.bincount(lab).min())})
            labs[(name, k)] = lab
    t = pd.DataFrame(rows)
    ari = pd.DataFrame([{"k": k, "k-means vs Ward": adjusted_rand_score(labs[("k-means", k)], labs[("Ward hierarchical", k)]),
                         "k-means vs mixture": adjusted_rand_score(labs[("k-means", k)], labs[("Gaussian mixture", k)]),
                         "Ward vs mixture": adjusted_rand_score(labs[("Ward hierarchical", k)], labs[("Gaussian mixture", k)])}
                        for k in ks])
    return t, ari, pca.explained_variance_ratio_
