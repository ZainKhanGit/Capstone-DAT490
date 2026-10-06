"""Step 8: growth measures and period labels for ZHVI (and ZORI).

Definitions (decided with the team)
  growth     : year-over-year change, value_t / value_{t-12 months} - 1, in percent
  reference  : December 2019 (index_dec2019 = 100 * value_t / value_Dec2019)
  periods    : pre-2020 = 2018-2019, 2020-2022, 2023-2025 (by calendar year)
  window     : 2018-01 to 2025-12; all months stay in the panel, `in_window` marks the window

Series are nominal dollars. ZHVI is smoothed and seasonally adjusted, so YoY changes are smooth by
construction and say little about month-to-month timing.

Outputs
  data/clean/zhvi_analysis_panel.parquet  ZIP-month panel with log level, YoY, index, period
  data/clean/zori_analysis_panel.parquet  same for ZORI
  data/clean/zip_growth.csv               one row per ZIP: December YoY by year, cumulative growth by
                                          period, growth relative to the metro median
  data/clean/zori_growth.csv              ZIPs with ZORI at the reference and end dates
  outputs/logs/growth_report.md
"""
import numpy as np
import pandas as pd
from scipy.stats import skew, spearmanr

from config import BASE_MONTH, CLEAN, LOGS, PERIODS, WINDOW

YEARS = list(range(2018, 2026))
CUM = {  # name -> (start December, end December)
    "cum_2017_2019": (2017, 2019),   # the two pre-pandemic years
    "cum_2019_2022": (2019, 2022),   # reference to end of the 2020-2022 period
    "cum_2022_2025": (2022, 2025),   # the 2023-2025 period
    "cum_2019_2025": (2019, 2025),
}


def add_growth(panel: pd.DataFrame, col: str) -> pd.DataFrame:
    p = panel.sort_values(["zip", "date"]).reset_index(drop=True).copy()
    # the grid is complete (every ZIP has every month), so a 12-row shift is a 12-month lag
    n = p.groupby("zip")["date"].transform("count")
    assert (n == p["date"].nunique()).all(), "panel is not a complete ZIP x month grid"
    p["year"] = p["date"].dt.year
    p[f"log_{col}"] = np.log(p[col].where(p[col] > 0))
    p["yoy_pct"] = 100 * (p[col] / p.groupby("zip")[col].shift(12) - 1)
    ref = p.loc[p["date"] == pd.Timestamp(BASE_MONTH)].set_index("zip")[col]
    p["index_dec2019"] = 100 * p[col] / p["zip"].map(ref)
    lo, hi = pd.Timestamp(WINDOW[0]), pd.Timestamp(WINDOW[1])
    p["in_window"] = (p["date"] >= lo) & (p["date"] <= hi)
    p["period"] = pd.NA
    for name, (y0, y1) in PERIODS.items():
        p.loc[p["in_window"] & p["year"].between(y0, y1), "period"] = name
    p["period"] = pd.Categorical(p["period"], categories=list(PERIODS), ordered=True)
    return p


def dec_wide(p: pd.DataFrame, col: str) -> pd.DataFrame:
    d = p[(p["date"].dt.month == 12)].pivot(index="zip", columns="year", values=col)
    return d


def zip_growth(p: pd.DataFrame, col: str, meta: pd.DataFrame) -> pd.DataFrame:
    dec = dec_wide(p, col)
    g = pd.DataFrame(index=dec.index)
    g[f"{col}_dec2019"] = dec[2019]
    for y in YEARS:
        g[f"yoy_dec{y}"] = 100 * (dec[y] / dec[y - 1] - 1)
    for name, (a, b) in CUM.items():
        g[name] = 100 * (dec[b] / dec[a] - 1)
    g = g.reset_index().merge(meta, on="zip", how="left")
    for name in CUM:  # growth relative to the metro median: removes metro-wide movements
        g[f"rel_{name}"] = g[name] - g.groupby("metro_short")[name].transform("median")
    return g


def main() -> None:
    dist = pd.read_csv(CLEAN / "zip_distance.csv", dtype={"zip": str})
    meta = dist[["zip", "metro_short", "dist_cityhall_mi", "dist_nearest_mi", "dist_band"]]

    zh = add_growth(pd.read_parquet(CLEAN / "zhvi_panel.parquet")[["zip", "metro_short", "date", "zhvi"]], "zhvi")
    zh.to_parquet(CLEAN / "zhvi_analysis_panel.parquet", index=False)
    g = zip_growth(zh, "zhvi", meta)
    g.to_csv(CLEAN / "zip_growth.csv", index=False)

    zo = add_growth(pd.read_parquet(CLEAN / "zori_panel.parquet")[["zip", "metro_short", "date", "zori"]], "zori")
    zo.to_parquet(CLEAN / "zori_analysis_panel.parquet", index=False)
    gz = zip_growth(zo, "zori", meta)
    gz = gz[gz["cum_2019_2025"].notna()]
    gz.to_csv(CLEAN / "zori_growth.csv", index=False)

    # ---------------- report ----------------
    w = zh[zh["in_window"]]
    L = ["# Growth measures (step 8)\n",
         "Year-over-year change (percent), December 2019 as the reference point, periods pre-2020 "
         "(2018-19), 2020-2022 and 2023-2025. Nominal dollars. All months are kept in the panel; "
         f"`in_window` marks {WINDOW[0][:7]} to {WINDOW[1][:7]}.\n",
         f"\nPanel rows: {len(zh):,} ({zh['zip'].nunique():,} ZIPs x {zh['date'].nunique()} months); "
         f"in window: {int(zh['in_window'].sum()):,}. ZORI panel: {len(zo):,} rows, "
         f"{int(zo.loc[zo['in_window'], 'zori'].notna().sum()):,} observed ZIP-months in window.\n",
         "\n## Reference month (Dec 2019)\n"]
    ref = zh[zh["date"] == pd.Timestamp(BASE_MONTH)]
    nref = ref.groupby("metro_short")["zhvi"].agg(zips="size", have_ref=lambda s: int(s.notna().sum()))
    nref["lack_ref"] = nref["zips"] - nref["have_ref"]
    L.append(nref.to_markdown() + "\n")
    ck = zh.loc[zh["date"] == pd.Timestamp(BASE_MONTH), "index_dec2019"].dropna()
    L.append(f"\nCheck: index at the reference month equals 100 for all {len(ck)} ZIPs with a value: "
             f"{bool(np.allclose(ck, 100))}. ZIPs without a Dec 2019 value cannot be indexed "
             "(they are the late entrants flagged in step 1).\n")
    bad = int((zh["zhvi"] <= 0).sum())
    zh["mom_pct"] = 100 * zh.groupby("zip")["zhvi"].pct_change()
    big = zh[zh["mom_pct"].abs() > 5]
    first = zh[zh["zhvi"].notna()].groupby("zip")["date"].min()
    after_entry = int((big["date"] <= big["zip"].map(first) + pd.DateOffset(months=3)).sum())
    L.append(f"\nSanity: non-positive values: {bad}. Largest absolute month-over-month change: "
             f"{zh['mom_pct'].abs().max():.1f}%. ZIP-months with a change above 5%: {len(big)} in the full "
             f"history, {int(big['in_window'].sum())} inside the analysis window "
             f"(by year: {big['year'].value_counts().sort_index().to_dict()}). They cluster in the "
             "2008-09 crash (Phoenix, Las Vegas) and the 2021 boom (Austin, Phoenix), i.e. real market moves, "
             f"not index artifacts: {after_entry} fall within three months of a ZIP first appearing.\n")

    L.append("\n## Median December-to-December growth (%) by metro and year\n\n"
             "A sanity check against the known pandemic-era pattern, not an analysis.\n\n")
    yo = g.groupby("metro_short")[[f"yoy_dec{y}" for y in YEARS]].median().round(1)
    yo.columns = YEARS
    L.append(yo.to_markdown() + "\n")

    L.append("\n## Median cumulative growth (%) by metro and period\n\n")
    cm = g.groupby("metro_short")[list(CUM)].median().round(1)
    L.append(cm.to_markdown() + "\n")

    L.append("\n## Work in logs? Skewness of the Dec 2019 level\n\n")
    lv = g["zhvi_dec2019"].dropna()
    sk = g.dropna(subset=["zhvi_dec2019"]).groupby("metro_short")["zhvi_dec2019"].apply(
        lambda s: pd.Series({"skew_level": skew(s), "skew_log_level": skew(np.log(s))})).unstack()
    sk.loc["ALL (pooled)"] = [skew(lv), skew(np.log(lv))]
    L.append(sk.round(2).to_markdown() + "\n\nLevels are right-skewed in most metros and the logs are "
             "closer to symmetric, which supports plotting levels on a log scale and estimating growth in "
             "logs or percent. Cumulative growth is already a ratio, so it is plotted in percent.\n")

    L.append("\n## Preview: rank correlation of growth with distance (sanity check of the columns)\n\n"
             "Spearman correlation between city-hall distance and cumulative growth, by metro. This only "
             "checks that signs are plausible; the gradient analysis proper belongs to the EDA and the "
             "later models. Positive = outer ZIPs grew faster.\n\n")
    rows = []
    for k, d in g.groupby("metro_short"):
        r = {"metro": k}
        for name in ("cum_2017_2019", "cum_2019_2022", "cum_2022_2025"):
            x = d[["dist_cityhall_mi", name]].dropna()
            r[name] = spearmanr(x["dist_cityhall_mi"], x[name])[0] if len(x) > 10 else np.nan
        rows.append(r)
    L.append(pd.DataFrame(rows).set_index("metro").round(2).to_markdown() + "\n")

    L.append("\n## ZORI growth columns\n\n"
             f"`zori_growth.csv` keeps the {len(gz)} ZIPs with ZORI at both Dec 2019 and Dec 2025 (fixed "
             "sample, see the ZORI limitation in `zori_coverage_report.md`); growth in a changing sample "
             "would mix real rent changes with ZIPs entering the index. Median cumulative rent growth "
             "Dec 2019 to Dec 2025 by metro (%):\n\n")
    L.append(gz.groupby("metro_short")["cum_2019_2025"].agg(["count", "median"]).round(1).to_markdown() + "\n")

    (LOGS / "growth_report.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
