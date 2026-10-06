# Distance to center (step 3)

Gazetteer: `2024_Gaz_zcta_national.txt` (Census 2024 ZCTA internal points); centers: `data/reference/city_centers.csv`.


## City-hall coordinates and sources

| metro     | role          | building                                                            | address                            |     lat |       lon | source                                                                                           |
|:----------|:--------------|:--------------------------------------------------------------------|:-----------------------------------|--------:|----------:|:-------------------------------------------------------------------------------------------------|
| Phoenix   | primary       | Phoenix City Hall                                                   | 200 West Washington Street         | 33.4489 | -112.077  | Wikipedia: Phoenix City Hall                                                                     |
| Austin    | primary       | Austin City Hall                                                    | 301 West 2nd Street                | 30.2649 |  -97.7472 | Wikipedia: Austin City Hall (Austin, Texas)                                                      |
| Atlanta   | primary       | Atlanta City Hall                                                   | 68 Mitchell Street                 | 33.7489 |  -84.3903 | Wikipedia: Atlanta City Hall                                                                     |
| Dallas    | primary       | Dallas City Hall                                                    | 1500 Marilla Street                | 32.7762 |  -96.7968 | Wikipedia: Dallas City Hall                                                                      |
| Tampa     | primary       | Tampa City Hall                                                     | 315 East John F. Kennedy Boulevard | 27.9472 |  -82.4575 | Wikipedia: Tampa City Hall                                                                       |
| Charlotte | primary       | Charlotte-Mecklenburg Government Center (seat of City Council)      | 600 East 4th Street                | 35.2213 |  -80.8396 | OpenStreetMap Nominatim lookup of the address (no Wikipedia coordinates exist for this building) |
| Nashville | primary       | Davidson County Courthouse / Metro Courthouse (Nashville City Hall) | 1 Public Square                    | 36.1672 |  -86.7786 | Wikipedia: Davidson County Courthouse - Nashville City Hall                                      |
| Las Vegas | primary       | Las Vegas City Hall                                                 | 495 South Main Street              | 36.1673 | -115.148  | Wikipedia: Las Vegas City Hall                                                                   |
| Dallas    | second_center | Fort Worth City Hall (Old City Hall)                                | 200 Texas Street                   | 32.7493 |  -97.3307 | OpenStreetMap Nominatim lookup of the address                                                    |
| Tampa     | second_center | St. Petersburg City Hall                                            | 175 5th Street North               | 27.7746 |  -82.6403 | OpenStreetMap Nominatim lookup of the address                                                    |


**Two-center metros.** Dallas-Fort Worth and Tampa-St. Petersburg each have two historic centers; the first-named city is used for both, per project decision. This links to the polycentric argument in the lit review and should be revisited when we map the gradients. Charlotte's coordinates come from OpenStreetMap, the other seven from Wikipedia; an OSM geocode of the address agrees with the Wikipedia point to under 0.1 mi for Phoenix, Austin, Dallas and Las Vegas (Atlanta differs by ~0.25 mi; Tampa and Nashville could not be geocoded by OSM). The two second centers, Fort Worth and St. Petersburg, are both from OSM address lookups; for St. Petersburg a Living New Deal entry is within ~0.1 mi.


## Second definition: ZCTA centroid of the city-hall ZIP

The city-hall ZIP codes for Austin and Dallas are on the cited Wikipedia pages; Charlotte's and Nashville's came from web-search summaries of their addresses; the other four were filled in from the street addresses. All eight are sanity-checked below by the distance from the ZCTA centroid to the city-hall point.


| metro     |   zip_of_address |   city hall to ZCTA centroid (mi) |
|:----------|-----------------:|----------------------------------:|
| Phoenix   |            85003 |                              0.13 |
| Austin    |            78701 |                              0.48 |
| Atlanta   |            30303 |                              0.27 |
| Dallas    |            75201 |                              0.85 |
| Tampa     |            33602 |                              0.45 |
| Charlotte |            28202 |                              0.49 |
| Nashville |            37201 |                              0.02 |
| Las Vegas |            89101 |                              1.5  |


## ZIP-to-ZCTA match (Gazetteer, all 1,099 ZHVI ZIPs)

| metro_short   |   zips |   matched |   unmatched |   pct_matched |
|:--------------|-------:|----------:|------------:|--------------:|
| Atlanta       |    203 |       203 |           0 |           100 |
| Austin        |     87 |        87 |           0 |           100 |
| Charlotte     |    105 |       105 |           0 |           100 |
| Dallas        |    254 |       254 |           0 |           100 |
| Las Vegas     |     70 |        70 |           0 |           100 |
| Nashville     |    102 |       102 |           0 |           100 |
| Phoenix       |    149 |       149 |           0 |           100 |
| Tampa         |    129 |       129 |           0 |           100 |
| TOTAL         |   1099 |      1099 |           0 |           100 |


## Distance summary (miles, matched ZIPs)

| metro_short   |   count |   min |   median |   mean |   max |
|:--------------|--------:|------:|---------:|-------:|------:|
| Atlanta       |     203 |   0.3 |     23.8 |   26.2 |  62.8 |
| Austin        |      87 |   0.5 |     14.4 |   17.9 |  43.3 |
| Charlotte     |     105 |   0.5 |     22.1 |   23.7 |  57   |
| Dallas        |     254 |   0.4 |     23.9 |   26.1 |  74.7 |
| Las Vegas     |      70 |   1.3 |      9.4 |   15.5 |  76.8 |
| Nashville     |     102 |   0   |     27   |   26.5 |  59.8 |
| Phoenix       |     149 |   0.1 |     17.2 |   22.7 | 106.3 |
| Tampa         |     129 |   0.5 |     18.6 |   18.9 |  48.4 |


## Sensitivity of distance to the center definition

Spearman rank correlation between the two distance measures within each metro, and the mean/max absolute difference in miles.


| metro     |   spearman |   mean_abs_diff_mi |   max_abs_diff_mi |
|:----------|-----------:|-------------------:|------------------:|
| Atlanta   |      1     |              0.18  |             0.273 |
| Austin    |      0.999 |              0.332 |             0.479 |
| Charlotte |      0.999 |              0.318 |             0.49  |
| Dallas    |      0.999 |              0.484 |             0.849 |
| Las Vegas |      0.986 |              0.944 |             1.503 |
| Nashville |      1     |              0.014 |             0.023 |
| Phoenix   |      1     |              0.097 |             0.133 |
| Tampa     |      0.999 |              0.283 |             0.454 |


## Polycentric test: nearest-center distance (Dallas-Fort Worth, Tampa-St. Petersburg)

Distance to the nearer of the two centers versus distance to the first-named city alone.


| metro   |   zips |   closer_to_second |   spearman |   mean_shift_mi |   max_shift_mi |   median_primary_mi |   median_nearest_mi |   changed_band |
|:--------|-------:|-------------------:|-----------:|----------------:|---------------:|--------------------:|--------------------:|---------------:|
| Dallas  |    254 |                103 |      0.676 |           6.947 |          31.07 |              23.909 |              15.247 |             70 |
| Tampa   |    129 |                 39 |      0.797 |           2.822 |          16.32 |              18.613 |              14.566 |             29 |


## Do gaps and non-matches sit at the periphery?

Median city-hall distance (miles) by ZHVI completeness, and by crosswalk flag.


| complete_window   |   count |   median |   mean |
|:------------------|--------:|---------:|-------:|
| False             |      27 |     37.5 |   37.5 |
| True              |    1072 |     20.1 |   22.9 |


| flag_metro_col_only   |   count |   median |   mean |
|:----------------------|--------:|---------:|-------:|
| False                 |    1087 |     20.2 |     23 |
| True                  |      12 |     49.7 |     53 |


## ZIPs per distance band

| metro_short   |   0-10 mi |   10-20 mi |   20-30 mi |   30+ mi |
|:--------------|----------:|-----------:|-----------:|---------:|
| Atlanta       |        37 |         46 |         41 |       79 |
| Austin        |        30 |         24 |         15 |       18 |
| Charlotte     |        22 |         24 |         23 |       36 |
| Dallas        |        36 |         65 |         62 |       91 |
| Las Vegas     |        39 |         17 |          4 |       10 |
| Nashville     |        19 |         19 |         20 |       44 |
| Phoenix       |        33 |         52 |         30 |       34 |
| Tampa         |        22 |         52 |         42 |       13 |


Same, using distance to the nearest center:


| metro_short   |   0-10 mi |   10-20 mi |   20-30 mi |   30+ mi |
|:--------------|----------:|-----------:|-----------:|---------:|
| Atlanta       |        37 |         46 |         41 |       79 |
| Austin        |        30 |         24 |         15 |       18 |
| Charlotte     |        22 |         24 |         23 |       36 |
| Dallas        |        65 |         94 |         43 |       52 |
| Las Vegas     |        39 |         17 |          4 |       10 |
| Nashville     |        19 |         19 |         20 |       44 |
| Phoenix       |        33 |         52 |         30 |       34 |
| Tampa         |        41 |         47 |         28 |       13 |
