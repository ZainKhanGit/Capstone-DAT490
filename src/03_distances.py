"""Step 3: ZCTA centroids (Census Gazetteer) and distance to each metro's center.

Center definitions, all kept as columns:
  cityhall : hand-compiled city-hall coordinates, first-named city (data/reference/city_centers.csv)  [primary]
  nearest  : distance to the nearer of the primary center and, for the two-center metros
             (Dallas-Fort Worth, Tampa-St. Petersburg), the second center       [polycentric test]
  zctactr  : Gazetteer centroid of the ZCTA matching the ZIP of the city-hall address [robustness]

Outputs
  data/clean/zip_distance.csv          one row per ZIP in the panel
  outputs/logs/distance_report.md
"""
import numpy as np
import pandas as pd

from config import CLEAN, LOGS, RAW

REF = CLEAN.parent / "reference" / "city_centers.csv"
GAZ = RAW / "2024_Gaz_zcta_national.txt"
BANDS = [0, 10, 20, 30, np.inf]
BAND_LABELS = ["0-10 mi", "10-20 mi", "20-30 mi", "30+ mi"]


def haversine_mi(lat1, lon1, lat2, lon2):
    r = 3958.7613
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = (np.sin((p2 - p1) / 2) ** 2
         + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2)
    return 2 * r * np.arcsin(np.sqrt(a))


def main() -> None:
    meta = pd.read_csv(CLEAN / "zhvi_zip_meta.csv", dtype={"zip": str})
    allc = pd.read_csv(REF, dtype={"zip_of_address": str})
    ref = allc[allc["role"] == "primary"].reset_index(drop=True)
    sec = allc[allc["role"] == "second_center"].reset_index(drop=True)
    gaz = pd.read_csv(GAZ, sep="\t", dtype={"GEOID": str})
    gaz.columns = gaz.columns.str.strip()
    gaz = gaz.rename(columns={"GEOID": "zip", "INTPTLAT": "zcta_lat", "INTPTLONG": "zcta_lon"})
    gaz = gaz[["zip", "zcta_lat", "zcta_lon"]]

    # secondary center: centroid of the ZCTA whose code equals the city-hall address ZIP
    ref = ref.merge(gaz.rename(columns={"zip": "zip_of_address", "zcta_lat": "ctr2_lat",
                                        "zcta_lon": "ctr2_lon"}), on="zip_of_address", how="left")
    if ref[["ctr2_lat", "ctr2_lon"]].isna().any().any():
        raise ValueError("a city-hall ZIP has no ZCTA in the Gazetteer")
    ref["center_gap_mi"] = haversine_mi(ref["lat"], ref["lon"], ref["ctr2_lat"], ref["ctr2_lon"])

    d = (meta[["zip", "metro_short", "city", "county", "sizerank", "complete_window",
               "late_entry", "xwalk_status"]]
         .merge(gaz, on="zip", how="left")
         .merge(ref[["metro", "city", "lat", "lon", "ctr2_lat", "ctr2_lon"]]
                .rename(columns={"metro": "metro_short", "city": "primary_city"}),
                on="metro_short", how="left"))
    d["zcta_matched"] = d["zcta_lat"].notna()
    d["dist_cityhall_mi"] = haversine_mi(d["zcta_lat"], d["zcta_lon"], d["lat"], d["lon"])
    d["dist_zctactr_mi"] = haversine_mi(d["zcta_lat"], d["zcta_lon"], d["ctr2_lat"], d["ctr2_lon"])
    d["dist_band"] = pd.cut(d["dist_cityhall_mi"], BANDS, labels=BAND_LABELS, right=False)
    d["flag_metro_col_only"] = d["xwalk_status"].eq("metro_col_only")
    d = d.merge(sec[["metro", "city", "lat", "lon"]]
                .rename(columns={"metro": "metro_short", "city": "second_city",
                                 "lat": "s_lat", "lon": "s_lon"}), on="metro_short", how="left")
    d["dist_second_mi"] = haversine_mi(d["zcta_lat"], d["zcta_lon"], d["s_lat"], d["s_lon"])
    d["dist_nearest_mi"] = d[["dist_cityhall_mi", "dist_second_mi"]].min(axis=1)
    d["nearest_center"] = np.where(d["dist_second_mi"] < d["dist_cityhall_mi"],
                                   d["second_city"], d["primary_city"])
    d["dist_band_nearest"] = pd.cut(d["dist_nearest_mi"], BANDS, labels=BAND_LABELS, right=False)
    d = d.drop(columns=["lat", "lon", "ctr2_lat", "ctr2_lon", "s_lat", "s_lon", "second_city", "primary_city"])
    d.to_csv(CLEAN / "zip_distance.csv", index=False)

    # ---------------- report ----------------
    L = ["# Distance to center (step 3)\n",
         f"Gazetteer: `{GAZ.name}` (Census 2024 ZCTA internal points); centers: "
         "`data/reference/city_centers.csv`.\n",
         "\n## City-hall coordinates and sources\n",
         allc[["metro", "role", "building", "address", "lat", "lon", "source"]]
         .to_markdown(index=False) + "\n",
         "\n**Two-center metros.** Dallas-Fort Worth and Tampa-St. Petersburg each have two "
         "historic centers; the first-named city is used for both, per project decision. This links "
         "to the polycentric argument in the lit review and should be revisited when we map the "
         "gradients. Charlotte's coordinates come from OpenStreetMap, the other seven from Wikipedia; "
         "an OSM geocode of the address agrees with the Wikipedia point to under 0.1 mi for Phoenix, "
         "Austin, Dallas and Las Vegas (Atlanta differs by ~0.25 mi; Tampa and Nashville could not be "
         "geocoded by OSM). The two second centers, Fort Worth and St. Petersburg, are both from OSM "
         "address lookups; for St. Petersburg a Living New Deal entry is within ~0.1 mi.\n",
         "\n## Second definition: ZCTA centroid of the city-hall ZIP\n",
         "The city-hall ZIP codes for Austin and Dallas are on the cited Wikipedia pages; Charlotte's "
         "and Nashville's came from web-search summaries of their addresses; the other four were "
         "filled in from the street addresses. All eight are sanity-checked below by the distance "
         "from the ZCTA centroid to the city-hall point.\n\n",
         ref[["metro", "zip_of_address", "center_gap_mi"]].round(2)
         .rename(columns={"center_gap_mi": "city hall to ZCTA centroid (mi)"})
         .to_markdown(index=False) + "\n",
         "\n## ZIP-to-ZCTA match (Gazetteer, all 1,099 ZHVI ZIPs)\n"]
    m = d.groupby("metro_short").agg(zips=("zip", "count"), matched=("zcta_matched", "sum"))
    m["unmatched"] = m["zips"] - m["matched"]
    m.loc["TOTAL"] = m.sum()
    m["pct_matched"] = (100 * m["matched"] / m["zips"]).round(1)
    L.append(m.astype({"zips": int, "matched": int, "unmatched": int}).to_markdown() + "\n")
    un = d[~d["zcta_matched"]]
    if len(un):
        L.append("\nUnmatched ZIPs:\n\n")
        L.append(un[["zip", "metro_short", "city", "sizerank"]].to_markdown(index=False) + "\n")

    L.append("\n## Distance summary (miles, matched ZIPs)\n")
    s = d[d["zcta_matched"]].groupby("metro_short")[["dist_cityhall_mi", "dist_zctactr_mi"]] \
        .describe(percentiles=[.5]).round(1)
    L.append(d[d["zcta_matched"]].groupby("metro_short")["dist_cityhall_mi"]
             .agg(["count", "min", "median", "mean", "max"]).round(1).to_markdown() + "\n")

    L.append("\n## Sensitivity of distance to the center definition\n\n"
             "Spearman rank correlation between the two distance measures within each metro, and the "
             "mean/max absolute difference in miles.\n\n")
    rows = []
    for k, g in d[d["zcta_matched"]].groupby("metro_short"):
        diff = (g["dist_cityhall_mi"] - g["dist_zctactr_mi"]).abs()
        rows.append((k, g["dist_cityhall_mi"].corr(g["dist_zctactr_mi"], method="spearman"),
                     diff.mean(), diff.max()))
    L.append(pd.DataFrame(rows, columns=["metro", "spearman", "mean_abs_diff_mi", "max_abs_diff_mi"])
             .set_index("metro").round(3).to_markdown() + "\n")

    L.append("\n## Polycentric test: nearest-center distance (Dallas-Fort Worth, Tampa-St. Petersburg)\n\n"
             "Distance to the nearer of the two centers versus distance to the first-named city alone.\n\n")
    rows = []
    for k in ["Dallas", "Tampa"]:
        g = d[(d["metro_short"] == k) & d["zcta_matched"]]
        moved = g["dist_nearest_mi"] < g["dist_cityhall_mi"]
        rows.append((k, len(g), int(moved.sum()), g["dist_cityhall_mi"].corr(g["dist_nearest_mi"], method="spearman"),
                     (g["dist_cityhall_mi"] - g["dist_nearest_mi"]).mean(),
                     (g["dist_cityhall_mi"] - g["dist_nearest_mi"]).max(),
                     g["dist_cityhall_mi"].median(), g["dist_nearest_mi"].median(),
                     int((g["dist_band"] != g["dist_band_nearest"]).sum())))
    L.append(pd.DataFrame(rows, columns=["metro", "zips", "closer_to_second", "spearman",
                                         "mean_shift_mi", "max_shift_mi", "median_primary_mi",
                                         "median_nearest_mi", "changed_band"])
             .set_index("metro").round(3).to_markdown() + "\n")
    L.append("\n## Do gaps and non-matches sit at the periphery?\n\n"
             "Median city-hall distance (miles) by ZHVI completeness, and by crosswalk flag.\n\n")
    mm = d[d["zcta_matched"]]
    L.append(mm.groupby("complete_window")["dist_cityhall_mi"].agg(["count", "median", "mean"])
             .round(1).to_markdown() + "\n\n")
    L.append(mm.groupby("flag_metro_col_only")["dist_cityhall_mi"].agg(["count", "median", "mean"])
             .round(1).to_markdown() + "\n")

    L.append("\n## ZIPs per distance band\n")
    L.append(pd.crosstab(mm["metro_short"], mm["dist_band"]).to_markdown() + "\n")
    L.append("\nSame, using distance to the nearest center:\n\n")
    L.append(pd.crosstab(mm["metro_short"], mm["dist_band_nearest"]).to_markdown() + "\n")

    (LOGS / "distance_report.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
