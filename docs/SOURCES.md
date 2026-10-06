# Data sources and provenance

Every file the pipeline reads, where it came from, and what it is used for. "Retrieved" is the date the file
was obtained for this project (2026-10-06 for everything below). Sizes are the byte counts of the files on
disk. Raw files live in `data/raw/`; hand-compiled inputs live in `data/reference/`.

Files marked **placed by hand** are not fetched by the pipeline; `src/run_pipeline.py` checks that they exist.
Only ACS (step 4) calls an API, using the `CENSUS_API_KEY` environment variable; the key is never written to
any file.

## 1. Zillow Home Value Index (ZHVI)

| | |
|---|---|
| File | `Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month (1).csv` (placed by hand; the `(1)` is a browser-download artifact, the pipeline matches `Zip_zhvi_*.csv`) |
| Publisher / page | Zillow Group, Zillow Research data: https://www.zillow.com/research/data/ |
| Series | ZHVI, all homes (single-family + condo), middle tier (35th–65th percentile), smoothed, seasonally adjusted, monthly, ZIP code |
| Coverage | 26,268 ZIP codes; 320 monthly columns, 2000-01-31 to 2026-08-31; nominal dollars |
| Size / retrieved | 123,559,595 bytes; 2026-10-06 |
| Used for | Primary outcome (steps 1, 8) |
| Notes | Built from Zillow's valuation models and smoothed, so month-to-month timing is blurred. The `Metro` column is blank for 4,712 ZIPs. |

## 2. Zillow Observed Rent Index (ZORI)

| | |
|---|---|
| File | `Zip_zori_uc_sfrcondomfr_sm_month.csv` |
| URL | https://files.zillowstatic.com/research/public_csvs/zori/Zip_zori_uc_sfrcondomfr_sm_month.csv (Zillow Research data page above) |
| Series | ZORI, all homes plus multifamily, smoothed, monthly, ZIP code |
| Coverage | 8,459 ZIP codes; 140 monthly columns, 2015-01-31 to 2026-08-31 |
| Size / retrieved | 10,023,480 bytes (server `Last-Modified` 2026-09-16); 2026-10-06 |
| Used for | Secondary outcome / rent check (steps 5, 8) |
| Notes | Coverage thins with distance from the center; see the limitation in `outputs/logs/zori_coverage_report.md`. |

## 3. American Community Survey (ACS) 5-year estimates

| | |
|---|---|
| Publisher | U.S. Census Bureau, Census Data API: https://www.census.gov/data/developers/data-sets/acs-5year.html |
| Endpoints | `https://api.census.gov/data/2019/acs/acs5` (2015–2019 estimates) and `https://api.census.gov/data/2023/acs/acs5` (2019–2023 estimates), `for=zip code tabulation area:*` |
| Tables | B08006 (means of transportation to work, incl. worked from home), C24010 (occupation by sex), B19013 (median household income), B25024 (units in structure), B01003 (total population); estimates and margins of error |
| Geography | ZIP Code Tabulation Areas (2010-based in the 2019 release, 2020-based in the 2023 release) |
| Cached as | `data/raw/acs/acs5_{2019,2023}_{group}.csv` (10 files, about 55 MB); retrieved 2026-10-06 |
| Used for | Pre-pandemic work-from-home exposure (2015–2019, primary), current composition (2019–2023, descriptive only) (step 4) |
| Notes | Sentinel codes (large negatives) are set to missing. ZIPs are joined to ZCTAs by identical 5-digit code; match rates are in `outputs/logs/acs_report.md`. |

## 4. Census Gazetteer, ZCTA

| | |
|---|---|
| File | `2024_Gaz_zcta_national.zip` → `2024_Gaz_zcta_national.txt` |
| URL | https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_zcta_national.zip (index: https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html) |
| Size / retrieved | 1,013,803 bytes (zip), 6,792,182 bytes (txt); 2026-10-06 |
| Used for | ZCTA internal points (latitude/longitude) for distance calculations (step 3) |

## 5. Census CBSA delineation

| | |
|---|---|
| File | `cbsa_delineation_list1_2023.xlsx` |
| URL | https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xlsx |
| Vintage | "List 1 … July 2023", based on OMB Bulletin 23-01 |
| Size / retrieved | 143,798 bytes; 2026-10-06 |
| Used for | County-based check of metro membership (step 2) |
| Notes | Three metros are titled differently from the ZHVI labels and were matched by CBSA code; see `outputs/logs/metro_crosswalk_report.md`. |

## 6. Census cartographic boundaries, ZCTA

| | |
|---|---|
| File | `cb_2020_us_zcta520_500k.zip` → `zcta_boundaries/` (shapefile) |
| URL | https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip |
| Product | Cartographic Boundary File, 2020 ZCTAs, generalized 1:500,000 (derived from TIGER/Line) |
| Size / retrieved | 66,655,314 bytes; 2026-10-06 |
| Used for | Choropleth maps (step 6) |
| Notes | The full-resolution TIGER/Line ZCTA file (about 529 MB) was not used. |

## 7. City-hall coordinates (hand-compiled)

File: `data/reference/city_centers.csv`, one row per center, with the source, URL, an independent
cross-check where one exists, and retrieval date (2026-10-06). Coordinates were read from the sources below
and recorded as given; they were not geocoded.

| Metro | Center | Source |
|---|---|---|
| Phoenix | Phoenix City Hall, 200 W Washington St | Wikipedia, "Phoenix City Hall" |
| Austin | Austin City Hall, 301 W 2nd St | Wikipedia, "Austin City Hall (Austin, Texas)" |
| Atlanta | Atlanta City Hall, 68 Mitchell St | Wikipedia, "Atlanta City Hall" |
| Dallas | Dallas City Hall, 1500 Marilla St | Wikipedia, "Dallas City Hall" |
| Dallas (second) | Fort Worth City Hall (Old City Hall), 200 Texas St | OpenStreetMap Nominatim address lookup |
| Tampa | Tampa City Hall, 315 E John F. Kennedy Blvd | Wikipedia, "Tampa City Hall" |
| Tampa (second) | St. Petersburg City Hall, 175 5th St N | OpenStreetMap Nominatim address lookup; Living New Deal entry within about 0.1 mi |
| Charlotte | Charlotte-Mecklenburg Government Center, 600 E 4th St | OpenStreetMap Nominatim address lookup (no Wikipedia coordinates exist for this building) |
| Nashville | Davidson County Courthouse / Metro Courthouse, 1 Public Square | Wikipedia, "Davidson County Courthouse – Nashville City Hall" |
| Las Vegas | Las Vegas City Hall, 495 S Main St | Wikipedia, "Las Vegas City Hall" |

Wikipedia pages are under `https://en.wikipedia.org/wiki/`. OSM address lookups were also run for Phoenix, Austin,
Atlanta, Dallas and Las Vegas as an independent check (agreement within about 0.25 mi). Map data © OpenStreetMap
contributors, available under the Open Database License (https://www.openstreetmap.org/copyright). Living New
Deal entry: https://livingnewdeal.org/sites/st-petersburg-city-hall-st-petersburg-fl/.

## Reference list (data sources, in the format used in the EDA)

1. Zillow Group. Zillow Home Value Index (ZHVI), ZIP code, all homes, mid-tier, smoothed, seasonally adjusted. Zillow Research, data through August 2026. https://www.zillow.com/research/data/ (retrieved 6 Oct 2026).
2. Zillow Group. Zillow Observed Rent Index (ZORI), ZIP code, all homes plus multifamily, smoothed. Zillow Research, data through August 2026. https://www.zillow.com/research/data/ (retrieved 6 Oct 2026).
3. U.S. Census Bureau. American Community Survey 5-Year Estimates, 2015–2019, tables B08006, C24010, B19013, B25024, B01003, ZIP Code Tabulation Areas. Census Data API. https://www.census.gov/data/developers/data-sets/acs-5year.html (retrieved 6 Oct 2026).
4. U.S. Census Bureau. American Community Survey 5-Year Estimates, 2019–2023, same tables and geography. Census Data API (retrieved 6 Oct 2026).
5. U.S. Census Bureau. 2024 Gazetteer Files, ZIP Code Tabulation Areas. https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html (retrieved 6 Oct 2026).
6. U.S. Census Bureau. Core Based Statistical Areas, Metropolitan Divisions, and Combined Statistical Areas, July 2023 (List 1). https://www2.census.gov/programs-surveys/metro-micro/geographies/reference-files/2023/delineation-files/list1_2023.xlsx (retrieved 6 Oct 2026).
7. U.S. Census Bureau. Cartographic Boundary File, 2020 ZIP Code Tabulation Areas, 1:500,000. https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_us_zcta520_500k.zip (retrieved 6 Oct 2026).
8. Wikipedia contributors. City hall articles for Phoenix, Austin, Atlanta, Dallas, Tampa, Nashville (Davidson County Courthouse) and Las Vegas, for building coordinates. https://en.wikipedia.org (retrieved 6 Oct 2026).
9. OpenStreetMap contributors. Nominatim address search, for the Charlotte, Fort Worth and St. Petersburg city-hall points and for coordinate cross-checks. https://nominatim.openstreetmap.org (retrieved 6 Oct 2026).
