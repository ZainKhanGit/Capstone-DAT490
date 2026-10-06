"""Step 4: pull ACS 5-year tables at ZCTA level for two vintages and join to the ZHVI ZIPs.

Vintages
  2019 release = 2015-2019 estimates (pre-pandemic baseline; 2010-based ZCTAs)
  2023 release = 2019-2023 estimates (current composition, description only; 2020-based ZCTAs)

Tables: B08006 (means of transportation to work, incl. worked from home), C24010 (occupation by sex),
B19013 (median household income), B25024 (units in structure), B01003 (total population).

Needs the CENSUS_API_KEY environment variable. Raw API responses are cached in data/raw/acs/.

Outputs
  data/raw/acs/acs5_{year}_{group}.csv   cached national ZCTA responses (E and M columns only)
  data/clean/acs_features_{year}.csv     ZIP-level features for our ZHVI ZIPs
  data/clean/zip_acs.csv                 both vintages side by side (suffix _2019, _2023)
  data/clean/acs_occupation_codes.csv    C24010 code -> label (for the later occupation index)
  outputs/logs/acs_report.md
"""
import re

import numpy as np
import pandas as pd
import requests

from config import CENSUS_API_KEY, CLEAN, LOGS, RAW

VINTAGES = {2019: "2015-2019", 2023: "2019-2023"}
GROUPS = ["B08006", "C24010", "B25024", "B19013", "B01003"]
ACS_DIR = RAW / "acs"
# Reliability of the work-from-home share is judged by its margin of error relative to the estimate.
# Census publishes MOEs at 90% confidence, so CV = (MOE / 1.645) / estimate; CV > 0.30 is the common
# "low reliability" cut, i.e. MOE / estimate > 0.49. We flag at 0.5. A zero estimate is flagged.
REL_MOE_MAX = 0.5
SMALL_N = 100  # kept as a separate, informational column only


def fetch_group(year: int, group: str) -> pd.DataFrame:
    path = ACS_DIR / f"acs5_{year}_{group}.csv"
    if path.exists():
        return pd.read_csv(path, dtype={"zcta": str})
    if not CENSUS_API_KEY:
        raise RuntimeError("CENSUS_API_KEY is not set in the environment")
    url = f"https://api.census.gov/data/{year}/acs/acs5"
    params = {"get": f"group({group})", "for": "zip code tabulation area:*", "key": CENSUS_API_KEY}
    try:
        r = requests.get(url, params=params, timeout=300)
        r.raise_for_status()
    except requests.RequestException as e:  # never let the key leak through an error message
        raise RuntimeError(str(e).replace(CENSUS_API_KEY, "***")) from None
    rows = r.json()
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df = df.rename(columns={"zip code tabulation area": "zcta"})
    keep = ["zcta"] + [c for c in df.columns if re.fullmatch(rf"{group}_\d+[EM]", c)]
    df = df[keep]
    ACS_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return df


def numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Convert to numbers; Census sentinel codes (large negatives) become NaN."""
    out = df.copy()
    for c in out.columns:
        if c != "zcta":
            out[c] = pd.to_numeric(out[c], errors="coerce")
            out.loc[out[c] <= -111111111, c] = np.nan
    return out


def prop_moe(num, num_moe, den, den_moe):
    """Census-recommended MOE for a proportion num/den (num a subset of den)."""
    p = num / den
    rad = num_moe ** 2 - (p ** 2) * den_moe ** 2
    ratio = np.sqrt(num_moe ** 2 + (p ** 2) * den_moe ** 2) / den
    return np.where(rad >= 0, np.sqrt(rad.clip(lower=0)) / den, ratio)


def build_features(year: int) -> pd.DataFrame:
    t = {g: numeric(fetch_group(year, g)) for g in GROUPS}
    f = t["B01003"][["zcta", "B01003_001E"]].rename(columns={"B01003_001E": "pop"})

    b = t["B08006"]
    w = b["B08006_001E"]
    f = f.merge(pd.DataFrame({
        "zcta": b["zcta"], "workers": w, "wfh_n": b["B08006_017E"],
        "wfh_share": b["B08006_017E"] / w,
        "wfh_share_moe": prop_moe(b["B08006_017E"], b["B08006_017M"], w, b["B08006_001M"]),
        "drive_alone_share": b["B08006_003E"] / w,
        "transit_share": b["B08006_008E"] / w,
        "walk_bike_share": (b["B08006_014E"] + b["B08006_015E"]) / w,
    }), on="zcta", how="left")
    f["wfh_rel_moe"] = np.where(f["wfh_share"] > 0, f["wfh_share_moe"] / f["wfh_share"], np.nan)
    f["wfh_unreliable"] = f["wfh_share"].notna() & ~(f["wfh_rel_moe"] <= REL_MOE_MAX)
    f["workers_lt100"] = f["workers"].notna() & (f["workers"] < SMALL_N)

    c = t["C24010"]
    occ = pd.DataFrame({"zcta": c["zcta"], "occ_workers": c["C24010_001E"]})
    for i in range(3, 38):  # male code i, female code i + 36; sum for both sexes
        occ[f"occ_{i:03d}"] = c[f"C24010_{i:03d}E"] + c[f"C24010_{i + 36:03d}E"]
    top = {"occ_mgmt_biz_sci_arts_share": 3, "occ_service_share": 19, "occ_sales_office_share": 27,
           "occ_natres_constr_maint_share": 30, "occ_prod_transport_share": 34}
    for name, i in top.items():
        occ[name] = occ[f"occ_{i:03d}"] / occ["occ_workers"]
    f = f.merge(occ, on="zcta", how="left")

    h = t["B25024"]
    tot = h["B25024_001E"]
    f = f.merge(pd.DataFrame({
        "zcta": h["zcta"], "housing_units": tot,
        "sf_detached_share": h["B25024_002E"] / tot,
        "sf_attached_share": h["B25024_003E"] / tot,
        "units_2_4_share": (h["B25024_004E"] + h["B25024_005E"]) / tot,
        "units_5_19_share": (h["B25024_006E"] + h["B25024_007E"]) / tot,
        "units_20plus_share": (h["B25024_008E"] + h["B25024_009E"]) / tot,
        "mobile_other_share": (h["B25024_010E"] + h["B25024_011E"]) / tot,
    }), on="zcta", how="left")

    inc = t["B19013"]
    f = f.merge(pd.DataFrame({"zcta": inc["zcta"], "median_hh_income": inc["B19013_001E"],
                              "median_hh_income_moe": inc["B19013_001M"]}), on="zcta", how="left")
    return f


def occupation_codes() -> pd.DataFrame:
    v = requests.get("https://api.census.gov/data/2023/acs/acs5/groups/C24010.json", timeout=60).json()
    rows = []
    for i in range(3, 38):
        lab = v["variables"][f"C24010_{i:03d}E"]["label"].split("!!Male:!!")[-1]
        rows.append((f"occ_{i:03d}", lab, f"C24010_{i:03d}E", f"C24010_{i + 36:03d}E"))
    return pd.DataFrame(rows, columns=["column", "label", "male_code", "female_code"])


def main() -> None:
    CLEAN.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    dist = pd.read_csv(CLEAN / "zip_distance.csv", dtype={"zip": str})
    zips = dist[["zip", "metro_short", "city", "sizerank", "dist_cityhall_mi", "dist_band",
                 "complete_window", "flag_metro_col_only"]]
    occupation_codes().to_csv(CLEAN / "acs_occupation_codes.csv", index=False)

    feats = {}
    for y in VINTAGES:
        f = build_features(y)
        feats[y] = f
        j = zips.merge(f, left_on="zip", right_on="zcta", how="left").drop(columns="zcta")
        j["in_acs"] = j["workers"].notna() | j["pop"].notna()
        for c in ("wfh_unreliable", "workers_lt100"):  # NaN after the left join -> not flagged
            j[c] = j[c].fillna(False).astype(bool)
        j.drop(columns=["metro_short", "city", "sizerank", "dist_cityhall_mi", "dist_band",
                        "complete_window", "flag_metro_col_only"]).to_csv(
            CLEAN / f"acs_features_{y}.csv", index=False)
        feats[y] = j

    both = zips.copy()
    for y, j in feats.items():
        cols = [c for c in j.columns if c not in zips.columns]
        both = both.merge(j[["zip"] + cols].rename(columns={c: f"{c}_{y}" for c in cols}),
                          on="zip", how="left")
    both.to_csv(CLEAN / "zip_acs.csv", index=False)

    # ---------------- report ----------------
    L = ["# ACS pull and ZIP-to-ZCTA match (step 4)\n",
         "Source: Census Data API, ACS 5-year detailed tables at ZIP Code Tabulation Area level. "
         "Tables: B08006, C24010, B19013, B25024, B01003. Estimates with Census sentinel codes "
         "(suppressed / not computable) are set to missing. ZIPs are joined to ZCTAs by identical "
         "5-digit code.\n"]
    for y, label in VINTAGES.items():
        j = feats[y]
        L.append(f"\n## {y} release ({label})\n")
        t = j.groupby("metro_short").agg(
            zips=("zip", "count"),
            matched=("in_acs", "sum"),
            workers_missing=("workers", lambda s: int(s.isna().sum())),
            wfh_unreliable=("wfh_unreliable", "sum"),
            workers_lt100=("workers_lt100", "sum"),
            income_missing=("median_hh_income", lambda s: int(s.isna().sum())),
        )
        t.loc["TOTAL"] = t.sum()
        t["pct_matched"] = (100 * t["matched"] / t["zips"]).round(1)
        L.append(t.astype({c: int for c in t.columns if c != "pct_matched"}).to_markdown() + "\n")
        un = j[~j["in_acs"]]
        L.append(f"\nZIPs with no ACS ZCTA row in the {y} release: {len(un)}.\n")
        if len(un):
            L.append("\n" + un[["zip", "metro_short", "city", "sizerank", "dist_cityhall_mi",
                                "complete_window"]].round(1).to_markdown(index=False) + "\n")

    L.append("\n## Do non-matches / missing data cluster anywhere?\n\n"
             "Median city-hall distance (miles) and median `sizerank` by whether a ZIP has a usable "
             "work-from-home share in each release.\n")
    rows = []
    for y, j in feats.items():
        for ok, g in j.groupby(j["wfh_share"].notna()):
            rows.append((y, "usable" if ok else "missing", len(g),
                         g["dist_cityhall_mi"].median(), g["sizerank"].median()))
    L.append("\n" + pd.DataFrame(rows, columns=["release", "wfh_share", "zips", "median_dist_mi",
                                                  "median_sizerank"]).round(1)
             .to_markdown(index=False) + "\n")

    L.append("\n## Pre-pandemic work-from-home share, 2015-2019 release (primary SQ2 exposure)\n\n"
             "Share of workers 16+ who worked from home; usable ZCTAs only.\n\n")
    j = feats[2019]
    ok = j[j["wfh_share"].notna()]
    L.append(ok.groupby("metro_short")["wfh_share"].describe(percentiles=[.25, .5, .75])
             .round(3).to_markdown() + "\n")
    L.append("\nPrecision: median margin of error on the share (percentage points), median MOE "
             "relative to the estimate, and the percentage of ZCTAs flagged `wfh_unreliable` "
             f"(MOE / estimate > {REL_MOE_MAX}, equivalent to CV > 0.30; a zero share counts as "
             "unreliable). The continuous `wfh_rel_moe` column is kept so plots can choose a "
             "different cut.\n\n")
    prec = ok.groupby("metro_short").apply(lambda g: pd.Series({
        "median_moe_pp": 100 * g["wfh_share_moe"].median(),
        "median_rel_moe": g["wfh_rel_moe"].median(),
        "pct_unreliable": 100 * g["wfh_unreliable"].mean()}), include_groups=False).round(2)
    L.append(prec.to_markdown() + "\n")
    flagged = ok[ok["wfh_unreliable"]]
    L.append(f"\nFlagged overall: {len(flagged)} of {len(ok)} ZIPs "
             f"({100 * len(flagged) / len(ok):.1f}%); median city-hall distance "
             f"{flagged['dist_cityhall_mi'].median():.1f} mi vs "
             f"{ok.loc[~ok['wfh_unreliable'], 'dist_cityhall_mi'].median():.1f} mi for the rest. "
             "ZIP 34681 (Tampa; 82% WFH share on 260 workers, MOE 17 points) is flagged; the old "
             "fewer-than-100-workers rule missed it.\n")

    L.append("\n## Change between releases (same ZIPs, both usable)\n\n")
    m = feats[2019][["zip", "wfh_share", "median_hh_income"]].merge(
        feats[2023][["zip", "wfh_share", "median_hh_income"]], on="zip", suffixes=("_2019", "_2023")).dropna()
    L.append(f"ZIPs usable in both: {len(m)}. Median WFH share {m['wfh_share_2019'].median():.3f} "
             f"(2015-2019) vs {m['wfh_share_2023'].median():.3f} (2019-2023). Correlation of the two "
             f"shares: {m['wfh_share_2019'].corr(m['wfh_share_2023']):.2f}. The 2019-2023 release mixes "
             "pre- and post-2020 responses and uses 2020-based ZCTAs, so it is used for description only.\n")

    (LOGS / "acs_report.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
