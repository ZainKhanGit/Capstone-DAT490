# ZCTA boundaries (step 6)

Source: Census cartographic boundary file `cb_2020_us_zcta520_500k.shp` (generalized 1:500,000, 2020 ZCTAs; 33,791 national polygons).


Polygons found for 1,099 of 1,099 ZHVI ZIPs. Missing: none.

Invalid geometries: 0. Gazetteer internal point inside its own polygon: 1098 of 1099 (internal points of irregular ZCTAs can fall outside by design).


## Polygon area (sq mi) by metro

| metro_short   |   count |   mean |   std |   min |   50% |   max |
|:--------------|--------:|-------:|------:|------:|------:|------:|
| Atlanta       |     203 |   43.7 |  44.6 |   0.1 |  31.1 | 259.8 |
| Austin        |      87 |   54   |  57.8 |   1.4 |  23.7 | 211.4 |
| Charlotte     |     105 |   54.4 |  54.1 |   0.5 |  36.8 | 289   |
| Dallas        |     254 |   37.1 |  47.8 |   0.5 |  15   | 315   |
| Las Vegas     |      70 |   64.5 | 175.5 |   0.2 |   9.8 | 934.1 |
| Nashville     |     102 |   59.2 |  50.4 |   0.2 |  45.4 | 298.7 |
| Phoenix       |     149 |   65.2 | 124.4 |   1.5 |  12.7 | 715.7 |
| Tampa         |     129 |   19.9 |  25.5 |   0.9 |  10.1 | 167.9 |


## Do the city-hall points fall in the ZCTA recorded as their address ZIP?

| metro     | role          | center         |   address_zip |   polygon_containing_point | match   |
|:----------|:--------------|:---------------|--------------:|---------------------------:|:--------|
| Phoenix   | primary       | Phoenix        |         85003 |                      85003 | True    |
| Austin    | primary       | Austin         |         78701 |                      78701 | True    |
| Atlanta   | primary       | Atlanta        |         30303 |                      30303 | True    |
| Dallas    | primary       | Dallas         |         75201 |                      75202 | False   |
| Tampa     | primary       | Tampa          |         33602 |                      33602 | True    |
| Charlotte | primary       | Charlotte      |         28202 |                      28202 | True    |
| Nashville | primary       | Nashville      |         37201 |                      37201 | True    |
| Las Vegas | primary       | Las Vegas      |         89101 |                      89101 | True    |
| Dallas    | second_center | Fort Worth     |         76102 |                      76102 | True    |
| Tampa     | second_center | St. Petersburg |         33701 |                      33701 | True    |


**Known discrepancy, left as is by decision.** Dallas City Hall (1500 Marilla St) is recorded with address ZIP 75201 (Wikipedia), but its coordinate falls in ZCTA 75202 on the generalized 2020 boundaries. The two are adjacent downtown ZIPs. The ZCTA-centroid robustness distance for Dallas uses 75201 (centroid 0.85 mi from the city-hall point, see `distance_report.md`), so the effect is under one mile against ZIP distances of tens of miles; the primary (city-hall) distance is unaffected. Any other mismatch listed above has the same two possible causes: a wrong recorded ZIP or a point near a boundary.
