# ACS pull and ZIP-to-ZCTA match (step 4)

Source: Census Data API, ACS 5-year detailed tables at ZIP Code Tabulation Area level. Tables: B08006, C24010, B19013, B25024, B01003. Estimates with Census sentinel codes (suppressed / not computable) are set to missing. ZIPs are joined to ZCTAs by identical 5-digit code.


## 2019 release (2015-2019)

| metro_short   |   zips |   matched |   workers_missing |   wfh_unreliable |   workers_lt100 |   income_missing |   pct_matched |
|:--------------|-------:|----------:|------------------:|-----------------:|----------------:|-----------------:|--------------:|
| Atlanta       |    203 |       203 |                 0 |               53 |               1 |                1 |         100   |
| Austin        |     87 |        87 |                 0 |               19 |               0 |                0 |         100   |
| Charlotte     |    105 |       105 |                 0 |               36 |               0 |                0 |         100   |
| Dallas        |    254 |       250 |                 4 |               59 |               0 |                4 |          98.4 |
| Las Vegas     |     70 |        68 |                 2 |               14 |               0 |                2 |          97.1 |
| Nashville     |    102 |       102 |                 0 |               44 |               2 |                1 |         100   |
| Phoenix       |    149 |       148 |                 1 |               18 |               0 |                1 |          99.3 |
| Tampa         |    129 |       129 |                 0 |                5 |               1 |                1 |         100   |
| TOTAL         |   1099 |      1092 |                 7 |              248 |               4 |               10 |          99.4 |


ZIPs with no ACS ZCTA row in the 2019 release: 7.


|   zip | metro_short   | city      |   sizerank |   dist_cityhall_mi | complete_window   |
|------:|:--------------|:----------|-----------:|-------------------:|:------------------|
| 75033 | Dallas        | Frisco    |        552 |               28.4 | True              |
| 75036 | Dallas        | Frisco    |       2917 |               25.6 | True              |
| 75072 | Dallas        | McKinney  |        598 |               29   | False             |
| 76005 | Dallas        | Arlington |      33010 |               16.3 | True              |
| 85378 | Phoenix       | Surprise  |      10085 |               19.4 | True              |
| 89034 | Las Vegas     | Mesquite  |      17536 |               71   | False             |
| 89158 | Las Vegas     | Las Vegas |      30164 |                4.6 | True              |


## 2023 release (2019-2023)

| metro_short   |   zips |   matched |   workers_missing |   wfh_unreliable |   workers_lt100 |   income_missing |   pct_matched |
|:--------------|-------:|----------:|------------------:|-----------------:|----------------:|-----------------:|--------------:|
| Atlanta       |    203 |       203 |                 0 |               32 |               0 |                2 |           100 |
| Austin        |     87 |        87 |                 0 |               14 |               0 |                0 |           100 |
| Charlotte     |    105 |       105 |                 0 |               25 |               0 |                0 |           100 |
| Dallas        |    254 |       254 |                 0 |               19 |               0 |                0 |           100 |
| Las Vegas     |     70 |        70 |                 0 |               11 |               0 |                1 |           100 |
| Nashville     |    102 |       102 |                 0 |               30 |               1 |                1 |           100 |
| Phoenix       |    149 |       149 |                 0 |               12 |               0 |                0 |           100 |
| Tampa         |    129 |       129 |                 0 |                1 |               1 |                2 |           100 |
| TOTAL         |   1099 |      1099 |                 0 |              144 |               2 |                6 |           100 |


ZIPs with no ACS ZCTA row in the 2023 release: 0.


## Do non-matches / missing data cluster anywhere?

Median city-hall distance (miles) and median `sizerank` by whether a ZIP has a usable work-from-home share in each release.


|   release | wfh_share   |   zips |   median_dist_mi |   median_sizerank |
|----------:|:------------|-------:|-----------------:|------------------:|
|      2019 | missing     |      7 |             25.6 |             10085 |
|      2019 | usable      |   1092 |             20.5 |              4531 |
|      2023 | usable      |   1099 |             20.5 |              4537 |


## Pre-pandemic work-from-home share, 2015-2019 release (primary SQ2 exposure)

Share of workers 16+ who worked from home; usable ZCTAs only.


| metro_short   |   count |   mean |   std |   min |   25% |   50% |   75% |   max |
|:--------------|--------:|-------:|------:|------:|------:|------:|------:|------:|
| Atlanta       |     203 |  0.065 | 0.03  | 0     | 0.041 | 0.063 | 0.086 | 0.151 |
| Austin        |      87 |  0.089 | 0.056 | 0     | 0.049 | 0.073 | 0.119 | 0.252 |
| Charlotte     |     105 |  0.053 | 0.034 | 0     | 0.027 | 0.046 | 0.078 | 0.13  |
| Dallas        |     250 |  0.055 | 0.03  | 0.002 | 0.03  | 0.05  | 0.072 | 0.167 |
| Las Vegas     |      68 |  0.047 | 0.038 | 0     | 0.023 | 0.039 | 0.062 | 0.256 |
| Nashville     |     102 |  0.056 | 0.032 | 0     | 0.036 | 0.054 | 0.073 | 0.146 |
| Phoenix       |     148 |  0.078 | 0.042 | 0.009 | 0.045 | 0.071 | 0.102 | 0.223 |
| Tampa         |     129 |  0.084 | 0.073 | 0     | 0.055 | 0.074 | 0.097 | 0.819 |


Precision: median margin of error on the share (percentage points), median MOE relative to the estimate, and the percentage of ZCTAs flagged `wfh_unreliable` (MOE / estimate > 0.5, equivalent to CV > 0.30; a zero share counts as unreliable). The continuous `wfh_rel_moe` column is kept so plots can choose a different cut.


| metro_short   |   median_moe_pp |   median_rel_moe |   pct_unreliable |
|:--------------|----------------:|-----------------:|-----------------:|
| Atlanta       |            1.75 |             0.29 |            26.11 |
| Austin        |            2.32 |             0.26 |            21.84 |
| Charlotte     |            1.39 |             0.32 |            34.29 |
| Dallas        |            1.44 |             0.33 |            23.6  |
| Las Vegas     |            1.29 |             0.3  |            20.59 |
| Nashville     |            2.4  |             0.4  |            43.14 |
| Phoenix       |            1.59 |             0.25 |            12.16 |
| Tampa         |            1.88 |             0.27 |             3.88 |


Flagged overall: 248 of 1092 ZIPs (22.7%); median city-hall distance 39.1 mi vs 17.4 mi for the rest. ZIP 34681 (Tampa; 82% WFH share on 260 workers, MOE 17 points) is flagged; the old fewer-than-100-workers rule missed it.


## Change between releases (same ZIPs, both usable)


ZIPs usable in both: 1085. Median WFH share 0.059 (2015-2019) vs 0.148 (2019-2023). Correlation of the two shares: 0.76. The 2019-2023 release mixes pre- and post-2020 responses and uses 2020-based ZCTAs, so it is used for description only.
