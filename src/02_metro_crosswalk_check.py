"""Step 2: compare ZHVI `Metro`-column membership with a county-based CBSA crosswalk.

Method A: ZHVI `Metro` column equals one of the eight target CBSA labels.
Method B: the ZIP's (State, CountyName) in ZHVI belongs to a county of one of the eight CBSAs
          in the Census 2023 CBSA delineation file (list1_2023.xlsx).

Outputs
  data/clean/zip_metro_xwalk.csv       every national ZIP with both assignments and an agreement flag
  outputs/logs/metro_crosswalk_report.md
"""
import glob

import pandas as pd

from config import CLEAN, LOGS, METROS, RAW

STATE_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
    "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
    "Puerto Rico": "PR",
}


# The July 2023 Census delineation titles three of the metros differently from the ZHVI `Metro` labels
# (Zillow's labels look like an earlier OMB delineation). Match these three by title alias, i.e. by
# CBSA (codes 12060, 12420, 29820), and say so. The vintage difference may also explain some of the
# county-level disagreements reported below.
TITLE_ALIASES = {
    "Atlanta-Sandy Springs-Roswell, GA": "Atlanta",
    "Austin-Round Rock-San Marcos, TX": "Austin",
    "Las Vegas-Henderson-North Las Vegas, NV": "Las Vegas",
}


def load_delineation() -> pd.DataFrame:
    d = pd.read_excel(RAW / "cbsa_delineation_list1_2023.xlsx", header=2, dtype=str)
    d = d[d["CBSA Code"].fillna("").str.fullmatch(r"\d{5}")].copy()
    d["state"] = d["State Name"].map(STATE_ABBR)
    d["county"] = d["County/County Equivalent"]
    return d


def main() -> None:
    inv = {v: k for k, v in METROS.items()}
    d = load_delineation()
    title_map = {**inv, **TITLE_ALIASES}
    t = d[d["CBSA Title"].isin(title_map)].copy()
    missing_titles = set(METROS) - set(t["CBSA Title"].map(title_map))
    if missing_titles:
        raise ValueError(f"metros not found in delineation file: {missing_titles}")
    t["metro_xwalk"] = t["CBSA Title"].map(title_map)
    # Case-insensitive county match: ZHVI writes "Dekalb County", Census writes "DeKalb County".
    county_to_metro = {(r.state, r.county.lower()): r.metro_xwalk for r in t.itertuples()}

    path = glob.glob(str(RAW / "Zip_zhvi_*.csv"))[0]
    z = pd.read_csv(path, usecols=["RegionName", "State", "City", "Metro", "CountyName"],
                    dtype={"RegionName": str})
    z["zip"] = z["RegionName"].str.zfill(5)
    z["metro_col"] = z["Metro"].map(inv)  # NaN if blank or not a target metro
    z["metro_xwalk"] = [county_to_metro.get((s, str(c).lower())) for s, c in zip(z["State"], z["CountyName"])]

    def status(r):
        a, b = r.metro_col, r.metro_xwalk
        if pd.isna(a) and pd.isna(b):
            return "neither"
        if pd.notna(a) and pd.notna(b):
            return "both_agree" if a == b else "both_disagree"
        return "metro_col_only" if pd.notna(a) else "xwalk_only"

    z["status"] = z.apply(status, axis=1)
    out = z[["zip", "State", "City", "CountyName", "Metro", "metro_col", "metro_xwalk", "status"]]
    out.to_csv(CLEAN / "zip_metro_xwalk.csv", index=False)

    tg = z[z["status"] != "neither"]
    L = ["# Metro membership: `Metro` column vs. county crosswalk (step 2)\n",
         "Crosswalk: Census CBSA delineation file, July 2023 vintage "
         "(`list1_2023.xlsx`), matched on state abbreviation + county name.\n",
         f"\nCounties in the eight CBSAs: {len(t)}. Five CBSA titles matched the ZHVI labels exactly; Atlanta, Austin and Las Vegas are titled "
         "differently in the July 2023 delineation (Atlanta-Sandy Springs-Roswell, Austin-Round Rock-San Marcos, "
         "Las Vegas-Henderson-North Las Vegas) and were matched by CBSA code (12060, 12420, 29820). The ZHVI "
         "labels appear to follow an earlier OMB delineation; that vintage gap is the likely reason for the "
         "county-level disagreements below (e.g. Lamar County GA is in the ZHVI Atlanta metro but not in the "
         "2023 Atlanta CBSA, while Lumpkin County GA is the reverse). We did not obtain the earlier delineation "
         "to confirm this.\n",
         "\n## Overall agreement (national ZIP file, ZIPs in either method's target set)\n",
         tg["status"].value_counts().to_frame("zips").to_markdown() + "\n",
         "\nA ZIP is counted for each metro by the method that assigned it. "
         "`metro_col_only` = Metro column says target metro but its county is not in that CBSA; "
         "`xwalk_only` = county is in the CBSA but the Metro column is blank or another metro.\n",
         "\n## By metro\n"]
    rows = []
    for m in METROS:
        a = set(z.loc[z["metro_col"] == m, "zip"])
        b = set(z.loc[z["metro_xwalk"] == m, "zip"])
        rows.append((m, len(a), len(b), len(a & b), len(a - b), len(b - a)))
    bm = pd.DataFrame(rows, columns=["metro", "Metro column", "county crosswalk", "both",
                                     "column only", "crosswalk only"]).set_index("metro")
    bm.loc["TOTAL"] = bm.sum()
    L.append(bm.to_markdown() + "\n")

    def listing(title, df, cols):
        L.append(f"\n## {title} ({len(df)})\n")
        if len(df):
            L.append(df[cols].sort_values(cols[:2]).to_markdown(index=False) + "\n")

    listing("Crosswalk-only ZIPs (county in CBSA, but Metro column does not assign it)",
            z[z["status"] == "xwalk_only"].assign(metro_col_label=lambda d: d["Metro"].fillna("(blank)")),
            ["metro_xwalk", "zip", "City", "CountyName", "State", "metro_col_label"])
    listing("Metro-column-only ZIPs (column says target metro, county not in that CBSA)",
            z[z["status"] == "metro_col_only"],
            ["metro_col", "zip", "City", "CountyName", "State"])
    listing("Disagreements (both assign, to different metros)",
            z[z["status"] == "both_disagree"],
            ["metro_col", "metro_xwalk", "zip", "City", "CountyName"])

    # Non-destructive: tag the step-1 ZIP metadata with the crosswalk status (panel unchanged).
    meta_path = CLEAN / "zhvi_zip_meta.csv"
    meta = pd.read_csv(meta_path, dtype={"zip": str})
    meta = meta.drop(columns=[c for c in ("xwalk_status", "metro_xwalk") if c in meta], errors="ignore")
    meta = meta.merge(z[["zip", "status", "metro_xwalk"]].rename(columns={"status": "xwalk_status"}),
                      on="zip", how="left")
    meta.to_csv(meta_path, index=False)

    (LOGS / "metro_crosswalk_report.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
