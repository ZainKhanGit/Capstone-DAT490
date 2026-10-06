"""Step 6: ZCTA boundaries for the ZHVI ZIPs (for choropleths), with sanity checks.

Source: Census cartographic boundary file cb_2020_us_zcta520_500k (generalized 1:500,000, 2020 ZCTAs).

Checks
  - every ZHVI ZIP has a polygon
  - each polygon contains (or is very near) its Gazetteer internal point
  - each city-hall point lies in the ZCTA recorded as its address ZIP (validates the second definition)

Outputs
  data/clean/zcta_boundaries.gpkg      polygons for our ZIPs, with metro and distance attributes
  outputs/logs/boundaries_report.md
"""
import geopandas as gpd
import pandas as pd

from config import CLEAN, LOGS, RAW

SHP = RAW / "zcta_boundaries" / "cb_2020_us_zcta520_500k.shp"
REF = CLEAN.parent / "reference" / "city_centers.csv"


def main() -> None:
    dist = pd.read_csv(CLEAN / "zip_distance.csv", dtype={"zip": str})
    zcta = gpd.read_file(SHP)
    id_col = "ZCTA5CE20" if "ZCTA5CE20" in zcta.columns else "GEOID20"
    zcta = zcta.rename(columns={id_col: "zip"})[["zip", "geometry"]]
    n_national = len(zcta)

    g = zcta.merge(dist, on="zip", how="inner")
    missing = sorted(set(dist["zip"]) - set(g["zip"]))
    g = gpd.GeoDataFrame(g, geometry="geometry", crs=zcta.crs)
    g["valid_geom"] = g.geometry.is_valid
    g["area_sqmi"] = g.to_crs(5070).geometry.area / 2.58999e6  # NAD83 / CONUS Albers

    # Gazetteer internal point inside its own polygon?
    pts = gpd.GeoSeries(gpd.points_from_xy(g["zcta_lon"], g["zcta_lat"]), index=g.index,
                        crs=4269).to_crs(g.crs)
    g["gaz_point_in_poly"] = g.geometry.contains(pts, align=True)
    g.to_file(CLEAN / "zcta_boundaries.gpkg", driver="GPKG")

    # city-hall point in the expected ZCTA?
    ref = pd.read_csv(REF, dtype={"zip_of_address": str})
    rows = []
    for r in ref.itertuples():
        pt = gpd.GeoSeries(gpd.points_from_xy([r.lon], [r.lat]), crs=4326).to_crs(zcta.crs).iloc[0]
        hit = zcta[zcta.geometry.contains(pt)]["zip"].tolist()
        rows.append((r.metro, r.role, r.city, r.zip_of_address, ",".join(hit) or "(none)",
                     r.zip_of_address in hit))
    chk = pd.DataFrame(rows, columns=["metro", "role", "center", "address_zip", "polygon_containing_point",
                                      "match"])

    L = ["# ZCTA boundaries (step 6)\n",
         f"Source: Census cartographic boundary file `{SHP.name}` (generalized 1:500,000, 2020 ZCTAs; "
         f"{n_national:,} national polygons).\n",
         f"\nPolygons found for {len(g):,} of {len(dist):,} ZHVI ZIPs. Missing: "
         f"{', '.join(missing) if missing else 'none'}.\n",
         f"Invalid geometries: {int((~g['valid_geom']).sum())}. Gazetteer internal point inside its "
         f"own polygon: {int(g['gaz_point_in_poly'].sum())} of {len(g)} (internal points of "
         "irregular ZCTAs can fall outside by design).\n",
         "\n## Polygon area (sq mi) by metro\n",
         g.groupby("metro_short")["area_sqmi"].describe(percentiles=[.5]).round(1).to_markdown() + "\n",
         "\n## Do the city-hall points fall in the ZCTA recorded as their address ZIP?\n",
         chk.to_markdown(index=False) + "\n"]
    if not chk["match"].all():
        L.append("\n**Known discrepancy, left as is by decision.** Dallas City Hall (1500 Marilla St) is "
                 "recorded with address ZIP 75201 (Wikipedia), but its coordinate falls in ZCTA 75202 on "
                 "the generalized 2020 boundaries. The two are adjacent downtown ZIPs. The "
                 "ZCTA-centroid robustness distance for Dallas uses 75201 (centroid 0.85 mi from the "
                 "city-hall point, see `distance_report.md`), so the effect is under one mile against ZIP "
                 "distances of tens of miles; the primary (city-hall) distance is unaffected. Any other "
                 "mismatch listed above has the same two possible causes: a wrong recorded ZIP or a point "
                 "near a boundary.\n")
    (LOGS / "boundaries_report.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
