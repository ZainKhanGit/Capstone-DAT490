"""Step 1: filter ZHVI to the eight metros, reshape to a ZIP-month panel, report missingness.

Outputs
  data/clean/zhvi_panel.parquet        long ZIP-month panel (all months kept, NaN where missing)
  data/clean/zhvi_zip_meta.csv         one row per ZIP (metro, city, county, first/last obs, gaps)
  outputs/logs/zhvi_quality_report.md  data-quality log for the EDA write-up
"""
import glob

import pandas as pd

from config import CLEAN, LOGS, METROS, RAW, WINDOW

ID_COLS = ["RegionID", "SizeRank", "RegionName", "RegionType", "StateName", "State",
           "City", "Metro", "CountyName"]


def load_raw() -> pd.DataFrame:
    paths = glob.glob(str(RAW / "Zip_zhvi_*.csv"))
    if len(paths) != 1:
        raise FileNotFoundError(f"expected exactly one ZHVI csv in {RAW}, found {paths}")
    # ZIPs must stay strings or leading zeros are lost.
    df = pd.read_csv(paths[0], dtype={"RegionName": str, "RegionID": str})
    df["RegionName"] = df["RegionName"].str.zfill(5)
    return df, paths[0]


def to_panel(wide: pd.DataFrame) -> pd.DataFrame:
    month_cols = [c for c in wide.columns if c not in ID_COLS]
    long = wide.melt(id_vars=ID_COLS, value_vars=month_cols, var_name="date", value_name="zhvi")
    long["date"] = pd.to_datetime(long["date"])
    long = long.rename(columns={"RegionName": "zip", "StateName": "state_name",
                                "CountyName": "county"})
    long.columns = [c.lower() if c not in ("zip",) else c for c in long.columns]
    return long.sort_values(["zip", "date"]).reset_index(drop=True)


def gap_stats(panel: pd.DataFrame) -> pd.DataFrame:
    """Per-ZIP first/last observed month and gaps *inside* the observed span vs. leading NaNs."""
    lo, hi = pd.Timestamp(WINDOW[0]), pd.Timestamp(WINDOW[1])
    w = panel[(panel["date"] >= lo) & (panel["date"] <= hi)]
    rows = []
    for z, g in w.groupby("zip"):
        obs = g.loc[g["zhvi"].notna(), "date"]
        n_win = len(g)
        if obs.empty:
            rows.append((z, pd.NaT, pd.NaT, 0, n_win, 0))
            continue
        span = g[(g["date"] >= obs.min()) & (g["date"] <= obs.max())]
        interior = int(span["zhvi"].isna().sum())
        rows.append((z, obs.min(), obs.max(), len(obs), n_win, interior))
    return pd.DataFrame(rows, columns=["zip", "first_obs", "last_obs", "n_obs_window",
                                       "n_months_window", "n_interior_gaps"])


def main() -> None:
    CLEAN.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)

    wide, src = load_raw()
    n_national = len(wide)
    inv = {v: k for k, v in METROS.items()}
    sel = wide[wide["Metro"].isin(inv)].copy()
    sel["metro_short"] = sel["Metro"].map(inv)

    panel = to_panel(sel.drop(columns=["metro_short"]))
    panel["metro_short"] = panel["metro"].map(inv)
    panel = panel[["zip", "metro_short", "metro", "city", "state", "county", "regionid",
                   "sizerank", "date", "zhvi"]].rename(columns={"metro": "metro_cbsa"})
    panel.to_parquet(CLEAN / "zhvi_panel.parquet", index=False)

    gs = gap_stats(panel)
    meta = (panel.drop_duplicates("zip")[["zip", "metro_short", "metro_cbsa", "city", "state",
                                          "county", "regionid", "sizerank"]]
            .merge(gs, on="zip"))
    meta["complete_window"] = meta["n_obs_window"] == meta["n_months_window"]
    meta["late_entry"] = meta["first_obs"] > pd.Timestamp(WINDOW[0])
    meta.to_csv(CLEAN / "zhvi_zip_meta.csv", index=False)

    # ---------------- report ----------------
    L = []
    L.append("# ZHVI data-quality report (step 1)\n")
    L.append(f"Source file: `{src}`  \n")
    L.append(f"National rows: {n_national:,}. Rows with blank `Metro`: "
             f"{int((wide['Metro'].isna() | (wide['Metro'] == '')).sum()):,}. "
             f"Date columns: {panel['date'].nunique()} "
             f"({panel['date'].min().date()} to {panel['date'].max().date()}).\n")
    L.append(f"Window for completeness checks: {WINDOW[0]} to {WINDOW[1]} "
             f"({meta['n_months_window'].iloc[0]} months).\n")

    L.append("\n## ZIPs per metro and completeness in the analysis window\n")
    t = meta.groupby("metro_short").agg(
        zips=("zip", "count"),
        complete=("complete_window", "sum"),
        late_entry=("late_entry", "sum"),
        interior_gap=("n_interior_gaps", lambda s: int((s > 0).sum())),
    )
    t["pct_complete"] = (100 * t["complete"] / t["zips"]).round(1)
    t.loc["TOTAL"] = [t["zips"].sum(), t["complete"].sum(), t["late_entry"].sum(),
                      t["interior_gap"].sum(), round(100 * t["complete"].sum() / t["zips"].sum(), 1)]
    L.append(t.astype({"zips": int, "complete": int, "late_entry": int, "interior_gap": int})
             .to_markdown() + "\n")
    L.append("\n`late_entry` = first observation after the window start (leading NaNs). "
             "`interior_gap` = NaNs between a ZIP's first and last observation.\n")

    L.append("\n## ZIPs observed at key dates\n")
    key = ["2018-01-31", "2019-12-31", "2022-12-31", "2025-12-31"]
    k = (panel[panel["date"].isin(pd.to_datetime(key))]
         .assign(obs=lambda d: d["zhvi"].notna())
         .pivot_table(index="metro_short", columns="date", values="obs", aggfunc="sum"))
    k.columns = [c.strftime("%Y-%m") for c in k.columns]
    L.append(k.astype(int).to_markdown() + "\n")

    inc = meta[~meta["complete_window"]].copy()
    L.append(f"\n## Incomplete ZIPs ({len(inc)})\n")
    if len(inc):
        inc["first_obs"] = inc["first_obs"].dt.strftime("%Y-%m")
        inc["last_obs"] = inc["last_obs"].dt.strftime("%Y-%m")
        L.append(inc[["zip", "metro_short", "city", "county", "first_obs", "last_obs",
                      "n_obs_window", "n_interior_gaps", "sizerank"]]
                 .sort_values(["metro_short", "first_obs"]).to_markdown(index=False) + "\n")
        L.append("\nWhere do gaps fall (by first-observed month)?\n\n")
        L.append(inc["first_obs"].value_counts().sort_index().to_frame("zips").to_markdown() + "\n")

    L.append("\n## Name-collision check\n")
    other = wide[wide["Metro"].fillna("").str.contains("|".join(
        [k for k in METROS]), regex=True) & ~wide["Metro"].isin(inv)]
    L.append("Metro labels containing a target-city name that were *not* selected "
             "(expected: unrelated places such as Austin MN, Las Vegas NM):\n\n")
    L.append(other.groupby("Metro").size().to_frame("zips").to_markdown() + "\n")

    (LOGS / "zhvi_quality_report.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
