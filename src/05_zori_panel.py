"""Step 5: ZORI (Zillow Observed Rent Index) panel for the same ZIPs as the ZHVI panel, with coverage.

ZORI is a secondary outcome: a rent-based check on whether post-2022 patterns reflect mortgage rates.
It is selected by ZIP membership in the ZHVI panel (not by the ZORI `Metro` column), so both outcomes
cover identical places; the `Metro`-column view is reported alongside for comparison.

Outputs
  data/clean/zori_panel.parquet      long ZIP-month panel (months kept; NaN where missing)
  data/clean/zori_zip_meta.csv       one row per ZIP: coverage flags and gap stats
  outputs/logs/zori_coverage_report.md
"""
import glob

import pandas as pd

from config import CLEAN, LOGS, METROS, RAW, WINDOW

ID_COLS = ["RegionID", "SizeRank", "RegionName", "RegionType", "StateName", "State",
           "City", "Metro", "CountyName"]
KEY_DATES = ["2018-01-31", "2019-12-31", "2022-12-31", "2025-12-31"]


def main() -> None:
    path = glob.glob(str(RAW / "Zip_zori_*.csv"))
    if len(path) != 1:
        raise FileNotFoundError(f"expected exactly one ZORI csv in {RAW}, found {path}")
    raw = pd.read_csv(path[0], dtype={"RegionName": str, "RegionID": str})
    raw["RegionName"] = raw["RegionName"].str.zfill(5)

    dist = pd.read_csv(CLEAN / "zip_distance.csv", dtype={"zip": str})
    zhvi_zips = dist[["zip", "metro_short", "city", "sizerank", "dist_cityhall_mi", "dist_band"]]
    inv = {v: k for k, v in METROS.items()}

    month_cols = [c for c in raw.columns if c not in ID_COLS]
    sel = raw[raw["RegionName"].isin(zhvi_zips["zip"])]
    long = sel.melt(id_vars=["RegionName"], value_vars=month_cols, var_name="date", value_name="zori")
    long["date"] = pd.to_datetime(long["date"])
    long = long.rename(columns={"RegionName": "zip"}).sort_values(["zip", "date"])
    long = long.merge(zhvi_zips[["zip", "metro_short"]], on="zip", how="left")
    long[["zip", "metro_short", "date", "zori"]].to_parquet(CLEAN / "zori_panel.parquet", index=False)

    # ---- per-ZIP coverage, over all 1,099 ZHVI ZIPs (not just those present in ZORI) ----
    lo, hi = pd.Timestamp(WINDOW[0]), pd.Timestamp(WINDOW[1])
    w = long[(long["date"] >= lo) & (long["date"] <= hi)]
    n_months = w["date"].nunique()
    rows = []
    for z, g in w.groupby("zip"):
        obs = g.loc[g["zori"].notna(), "date"]
        if obs.empty:
            rows.append((z, pd.NaT, pd.NaT, 0, 0))
            continue
        span = g[(g["date"] >= obs.min()) & (g["date"] <= obs.max())]
        rows.append((z, obs.min(), obs.max(), len(obs), int(span["zori"].isna().sum())))
    gs = pd.DataFrame(rows, columns=["zip", "first_obs", "last_obs", "n_obs_window", "n_interior_gaps"])
    meta = zhvi_zips.merge(gs, on="zip", how="left")
    meta["n_obs_window"] = meta["n_obs_window"].fillna(0).astype(int)
    meta["n_interior_gaps"] = meta["n_interior_gaps"].fillna(0).astype(int)
    meta["in_zori_file"] = meta["zip"].isin(raw["RegionName"])
    meta["has_any_zori"] = meta["n_obs_window"] > 0
    meta["complete_window"] = meta["n_obs_window"] == n_months
    meta["late_entry"] = meta["has_any_zori"] & (meta["first_obs"] > lo)
    meta.to_csv(CLEAN / "zori_zip_meta.csv", index=False)

    # ---------------- report ----------------
    L = ["# ZORI coverage report (step 5)\n",
         f"Source file: `{path[0]}`  \n",
         f"National rows: {len(raw):,}; date columns: {len(month_cols)} "
         f"({month_cols[0]} to {month_cols[-1]}). Window for completeness: {WINDOW[0]} to {WINDOW[1]} "
         f"({n_months} months). Rows selected: ZIPs in the ZHVI panel.\n",
         "\n## Coverage by metro (denominator: the ZHVI ZIPs)\n"]
    t = meta.groupby("metro_short").agg(
        zhvi_zips=("zip", "count"), in_zori_file=("in_zori_file", "sum"),
        any_zori=("has_any_zori", "sum"), complete=("complete_window", "sum"),
        late_entry=("late_entry", "sum"),
        interior_gap=("n_interior_gaps", lambda s: int((s > 0).sum())))
    t.loc["TOTAL"] = t.sum()
    t["pct_any"] = (100 * t["any_zori"] / t["zhvi_zips"]).round(1)
    t["pct_complete"] = (100 * t["complete"] / t["zhvi_zips"]).round(1)
    L.append(t.astype({c: int for c in t.columns if not c.startswith("pct")}).to_markdown() + "\n")
    L.append("\n`any_zori` = at least one observation in the window; `complete` = every month in the "
             "window; `late_entry` = first observation after the window start.\n")

    L.append("\n## ZIPs with a ZORI value at key dates\n")
    k = (long[long["date"].isin(pd.to_datetime(KEY_DATES))]
         .assign(obs=lambda d: d["zori"].notna())
         .pivot_table(index="metro_short", columns="date", values="obs", aggfunc="sum"))
    k.columns = [c.strftime("%Y-%m") for c in k.columns]
    L.append(k.astype(int).to_markdown() + "\n")

    L.append("\n## Does ZORI coverage depend on distance from the center?\n\n"
             "Share of ZHVI ZIPs that have ZORI, by city-hall distance band, pooled and by metro.\n\n")
    L.append((meta.groupby("dist_band", observed=True)["has_any_zori"].agg(["count", "sum", "mean"])
              .rename(columns={"count": "zips", "sum": "with_zori", "mean": "share"}).round(3)
              ).to_markdown() + "\n\n")
    L.append((meta.pivot_table(index="metro_short", columns="dist_band", values="has_any_zori",
                               aggfunc="mean", observed=True) * 100).round(0).to_markdown() + "\n")
    L.append("\n(percent of ZIPs in each band with any ZORI.)\n")
    L.append("\nMedian city-hall distance (miles): "
             f"with ZORI {meta.loc[meta['has_any_zori'], 'dist_cityhall_mi'].median():.1f}, "
             f"without {meta.loc[~meta['has_any_zori'], 'dist_cityhall_mi'].median():.1f}.\n")

    # fixed-sample view: ZIPs with ZORI at both ends of the post-pandemic comparison
    ends = pd.to_datetime(["2019-12-31", "2025-12-31"])
    both_ends = (long[long["date"].isin(ends) & long["zori"].notna()]
                 .groupby("zip")["date"].nunique().eq(2))
    meta["zori_both_ends"] = meta["zip"].map(both_ends).fillna(False).astype(bool)
    fs = meta.groupby("dist_band", observed=True).agg(
        zhvi_zips=("zip", "count"), zori_both_ends=("zori_both_ends", "sum"))
    fs["pct"] = (100 * fs["zori_both_ends"] / fs["zhvi_zips"]).round(0)
    fs.loc["ALL"] = [fs["zhvi_zips"].sum(), fs["zori_both_ends"].sum(),
                     round(100 * fs["zori_both_ends"].sum() / fs["zhvi_zips"].sum())]
    out_ring = meta[meta["dist_band"] == "30+ mi"]
    acs = pd.read_csv(CLEAN / "zip_acs.csv", dtype={"zip": str})
    acs = pd.DataFrame({"zip": acs["zip"], "pop_2023": acs["pop_2023"],
                        "multi5_2023": acs["units_5_19_share_2023"] + acs["units_20plus_share_2023"]})
    ring = meta[meta["dist_cityhall_mi"] >= 20].merge(acs, on="zip", how="left")
    sel_t, sel_f = ring[ring["has_any_zori"]], ring[~ring["has_any_zori"]]
    L.append("\n## Limitation: the rent check is weakest where the gradient question lives\n\n"
             "The plan uses ZORI to separate location preferences from the 2022 mortgage-rate shock: "
             "rents do not depend directly on mortgage financing, so a post-2022 change in the price "
             "gradient that is absent in rents points toward rates. That comparison needs rent data "
             "across the whole range of distances, and ZORI does not provide it.\n\n"
             f"- Only {100 * meta.loc[meta['dist_band'] == '30+ mi', 'has_any_zori'].mean():.0f}% of ZIPs "
             f"30+ miles from the center have any ZORI ({int(out_ring['has_any_zori'].sum())} of "
             f"{len(out_ring)}), against {100 * meta.loc[meta['dist_band'] == '0-10 mi', 'has_any_zori'].mean():.0f}% "
             "within 10 miles.\n"
             "- A rent gradient is therefore estimated almost entirely from the inner and middle metro. "
             "Where it flattens or steepens in the outer ring, which is where the price gradient is most "
             "uncertain, rents say little.\n"
             "- Coverage is also selective, not random: Zillow needs enough rental listings to publish a "
             "ZIP. Among ZIPs 20+ miles out, those with ZORI have a median population of "
             f"{sel_t['pop_2023'].median():,.0f} vs {sel_f['pop_2023'].median():,.0f} for those without, and "
             f"{100 * sel_t['multi5_2023'].median():.1f}% vs {100 * sel_f['multi5_2023'].median():.1f}% of "
             "housing units in 5+ unit buildings (2019-2023 ACS medians). A rent-versus-price gap in the "
             "covered sample may not transfer to the uncovered, smaller, mostly single-family ZIPs.\n"
             "- The comparison should be restricted to ZIPs with ZORI at both ends of the window and "
             "labelled as an inner/middle-metro check, not a metro-wide control. ZIPs with ZORI at both "
             "Dec 2019 and Dec 2025, by distance band:\n\n"
             + fs.astype({"zhvi_zips": int, "zori_both_ends": int}).to_markdown() + "\n\n"
             "Consequence for the write-up: the rent check can support or weaken a rate-shock explanation "
             "for the inner and middle metro only. It cannot rule one out for the outer ring.\n")
    meta.to_csv(CLEAN / "zori_zip_meta.csv", index=False)

    L.append("\n## ZORI rows whose `Metro` column names a target metro but ZIP is not in the ZHVI set\n\n")
    extra = raw[raw["Metro"].isin(inv) & ~raw["RegionName"].isin(zhvi_zips["zip"])]
    L.append(f"{len(extra)} ZIPs" + (":\n\n" + extra[["RegionName", "City", "Metro"]].to_markdown(index=False)
                                      if len(extra) else " (none).") + "\n")

    (LOGS / "zori_coverage_report.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
