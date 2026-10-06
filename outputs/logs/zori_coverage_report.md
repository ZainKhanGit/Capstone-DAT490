# ZORI coverage report (step 5)

Source file: `/Users/saikrishnavarshithdanda/Desktop/capstone/data/raw/Zip_zori_uc_sfrcondomfr_sm_month.csv`  

National rows: 8,459; date columns: 140 (2015-01-31 to 2026-08-31). Window for completeness: 2018-01-31 to 2025-12-31 (96 months). Rows selected: ZIPs in the ZHVI panel.


## Coverage by metro (denominator: the ZHVI ZIPs)

| metro_short   |   zhvi_zips |   in_zori_file |   any_zori |   complete |   late_entry |   interior_gap |   pct_any |   pct_complete |
|:--------------|------------:|---------------:|-----------:|-----------:|-------------:|---------------:|----------:|---------------:|
| Atlanta       |         203 |            153 |        143 |         81 |           58 |              9 |      70.4 |           39.9 |
| Austin        |          87 |             69 |         64 |         33 |           29 |              9 |      73.6 |           37.9 |
| Charlotte     |         105 |             68 |         62 |         29 |           32 |              6 |      59   |           27.6 |
| Dallas        |         254 |            215 |        196 |         71 |          118 |             23 |      77.2 |           28   |
| Las Vegas     |          70 |             59 |         58 |         40 |           17 |              2 |      82.9 |           57.1 |
| Nashville     |         102 |             49 |         44 |         20 |           24 |              4 |      43.1 |           19.6 |
| Phoenix       |         149 |            126 |        121 |         79 |           36 |             12 |      81.2 |           53   |
| Tampa         |         129 |            121 |        111 |         45 |           62 |             15 |      86   |           34.9 |
| TOTAL         |        1099 |            860 |        799 |        398 |          376 |             80 |      72.7 |           36.2 |


`any_zori` = at least one observation in the window; `complete` = every month in the window; `late_entry` = first observation after the window start.


## ZIPs with a ZORI value at key dates

| metro_short   |   2018-01 |   2019-12 |   2022-12 |   2025-12 |
|:--------------|----------:|----------:|----------:|----------:|
| Atlanta       |        85 |        97 |       130 |       143 |
| Austin        |        35 |        40 |        52 |        64 |
| Charlotte     |        30 |        33 |        50 |        61 |
| Dallas        |        78 |        96 |       158 |       196 |
| Las Vegas     |        41 |        42 |        54 |        58 |
| Nashville     |        20 |        30 |        34 |        42 |
| Phoenix       |        85 |        91 |       107 |       120 |
| Tampa         |        49 |        50 |        93 |       111 |


## Does ZORI coverage depend on distance from the center?

Share of ZHVI ZIPs that have ZORI, by city-hall distance band, pooled and by metro.


| dist_band   |   zips |   with_zori |   share |
|:------------|-------:|------------:|--------:|
| 0-10 mi     |    238 |         224 |   0.941 |
| 10-20 mi    |    299 |         268 |   0.896 |
| 20-30 mi    |    237 |         189 |   0.797 |
| 30+ mi      |    325 |         118 |   0.363 |


| metro_short   |   0-10 mi |   10-20 mi |   20-30 mi |   30+ mi |
|:--------------|----------:|-----------:|-----------:|---------:|
| Atlanta       |        92 |         96 |         90 |       35 |
| Austin        |        90 |         83 |         73 |       33 |
| Charlotte     |       100 |         75 |         70 |       17 |
| Dallas        |        86 |         92 |         87 |       56 |
| Las Vegas     |        97 |         88 |         75 |       20 |
| Nashville     |        89 |         74 |         40 |       11 |
| Phoenix       |       100 |         92 |         93 |       35 |
| Tampa         |       100 |         94 |         76 |       62 |


(percent of ZIPs in each band with any ZORI.)


Median city-hall distance (miles): with ZORI 16.2, without 38.0.


## Limitation: the rent check is weakest where the gradient question lives

The plan uses ZORI to separate location preferences from the 2022 mortgage-rate shock: rents do not depend directly on mortgage financing, so a post-2022 change in the price gradient that is absent in rents points toward rates. That comparison needs rent data across the whole range of distances, and ZORI does not provide it.

- Only 36% of ZIPs 30+ miles from the center have any ZORI (118 of 325), against 94% within 10 miles.
- A rent gradient is therefore estimated almost entirely from the inner and middle metro. Where it flattens or steepens in the outer ring, which is where the price gradient is most uncertain, rents say little.
- Coverage is also selective, not random: Zillow needs enough rental listings to publish a ZIP. Among ZIPs 20+ miles out, those with ZORI have a median population of 35,786 vs 4,872 for those without, and 9.0% vs 0.3% of housing units in 5+ unit buildings (2019-2023 ACS medians). A rent-versus-price gap in the covered sample may not transfer to the uncovered, smaller, mostly single-family ZIPs.
- The comparison should be restricted to ZIPs with ZORI at both ends of the window and labelled as an inner/middle-metro check, not a metro-wide control. ZIPs with ZORI at both Dec 2019 and Dec 2025, by distance band:

| dist_band   |   zhvi_zips |   zori_both_ends |   pct |
|:------------|------------:|-----------------:|------:|
| 0-10 mi     |         238 |              163 |    68 |
| 10-20 mi    |         299 |              164 |    55 |
| 20-30 mi    |         237 |              111 |    47 |
| 30+ mi      |         325 |               41 |    13 |
| ALL         |        1099 |              479 |    44 |

Consequence for the write-up: the rent check can support or weaken a rate-shock explanation for the inner and middle metro only. It cannot rule one out for the outer ring.


## ZORI rows whose `Metro` column names a target metro but ZIP is not in the ZHVI set


7 ZIPs:

|   RegionName | City        | Metro                                          |
|-------------:|:------------|:-----------------------------------------------|
|        85144 | Queen Creek | Phoenix-Mesa-Chandler, AZ                      |
|        85288 | Tempe       | Phoenix-Mesa-Chandler, AZ                      |
|        75207 | Dallas      | Dallas-Fort Worth-Arlington, TX                |
|        76155 | Fort Worth  | Dallas-Fort Worth-Arlington, TX                |
|        75251 | Dallas      | Dallas-Fort Worth-Arlington, TX                |
|        37228 | Nashville   | Nashville-Davidson--Murfreesboro--Franklin, TN |
|        75247 | Dallas      | Dallas-Fort Worth-Arlington, TX                |
