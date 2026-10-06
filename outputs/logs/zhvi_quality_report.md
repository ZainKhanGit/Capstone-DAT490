# ZHVI data-quality report (step 1)

Source file: `/Users/saikrishnavarshithdanda/Desktop/capstone/data/raw/Zip_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month (1).csv`  

National rows: 26,268. Rows with blank `Metro`: 4,712. Date columns: 320 (2000-01-31 to 2026-08-31).

Window for completeness checks: 2018-01-31 to 2025-12-31 (96 months).


## ZIPs per metro and completeness in the analysis window

| metro_short   |   zips |   complete |   late_entry |   interior_gap |   pct_complete |
|:--------------|-------:|-----------:|-------------:|---------------:|---------------:|
| Atlanta       |    203 |        201 |            1 |              1 |           99   |
| Austin        |     87 |         77 |            4 |              6 |           88.5 |
| Charlotte     |    105 |        104 |            1 |              0 |           99   |
| Dallas        |    254 |        250 |            3 |              1 |           98.4 |
| Las Vegas     |     70 |         67 |            2 |              1 |           95.7 |
| Nashville     |    102 |         98 |            4 |              0 |           96.1 |
| Phoenix       |    149 |        146 |            2 |              1 |           98   |
| Tampa         |    129 |        129 |            0 |              0 |          100   |
| TOTAL         |   1099 |       1072 |           17 |             10 |           97.5 |


`late_entry` = first observation after the window start (leading NaNs). `interior_gap` = NaNs between a ZIP's first and last observation.


## ZIPs observed at key dates

| metro_short   |   2018-01 |   2019-12 |   2022-12 |   2025-12 |
|:--------------|----------:|----------:|----------:|----------:|
| Atlanta       |       202 |       202 |       203 |       203 |
| Austin        |        83 |        84 |        87 |        87 |
| Charlotte     |       104 |       104 |       105 |       105 |
| Dallas        |       251 |       253 |       254 |       254 |
| Las Vegas     |        68 |        68 |        68 |        70 |
| Nashville     |        98 |        98 |       102 |       102 |
| Phoenix       |       147 |       147 |       147 |       149 |
| Tampa         |       129 |       129 |       129 |       129 |


## Incomplete ZIPs (27)

|   zip | metro_short   | city           | county            | first_obs   | last_obs   |   n_obs_window |   n_interior_gaps |   sizerank |
|------:|:--------------|:---------------|:------------------|:------------|:-----------|---------------:|------------------:|-----------:|
| 30185 | Atlanta       | Whitesburg     | Carroll County    | 2018-01     | 2025-12    |             95 |                 1 |      13474 |
| 30177 | Atlanta       | Tate           | Pickens County    | 2021-02     | 2025-12    |             59 |                 0 |      21265 |
| 78613 | Austin        | Cedar Park     | Williamson County | 2018-01     | 2025-12    |             94 |                 2 |         48 |
| 78641 | Austin        | Leander        | Williamson County | 2018-01     | 2025-12    |             94 |                 2 |         28 |
| 78665 | Austin        | Round Rock     | Williamson County | 2018-01     | 2025-12    |             95 |                 1 |        463 |
| 78717 | Austin        | Austin         | Williamson County | 2018-01     | 2025-12    |             94 |                 2 |       2190 |
| 78732 | Austin        | Austin         | Travis County     | 2018-01     | 2025-12    |             95 |                 1 |       6193 |
| 78739 | Austin        | Austin         | Travis County     | 2018-01     | 2025-12    |             95 |                 1 |       6107 |
| 78615 | Austin        | Coupland       | Williamson County | 2019-02     | 2025-12    |             83 |                 0 |      15617 |
| 78622 | Austin        | Luling         | Caldwell County   | 2022-02     | 2025-12    |             47 |                 0 |      32057 |
| 78632 | Austin        | Harwood        | Caldwell County   | 2022-02     | 2025-12    |             47 |                 0 |      21007 |
| 78661 | Austin        | Luling         | Caldwell County   | 2022-02     | 2025-12    |             47 |                 0 |      32290 |
| 29717 | Charlotte     | Hickory Grove  | York County       | 2022-02     | 2025-12    |             47 |                 0 |      20225 |
| 76164 | Dallas        | Fort Worth     | Tarrant County    | 2018-01     | 2025-12    |             94 |                 2 |       8052 |
| 75072 | Dallas        | McKinney       | Collin County     | 2018-02     | 2025-12    |             95 |                 0 |        598 |
| 76066 | Dallas        | Millsap        | Parker County     | 2019-02     | 2025-12    |             83 |                 0 |      12291 |
| 76486 | Dallas        | Perrin         | Jack County       | 2022-02     | 2025-12    |             47 |                 0 |      22461 |
| 89034 | Las Vegas     | Mesquite       | Lincoln County    | 2018-01     | 2025-12    |             94 |                 2 |      17536 |
| 89018 | Las Vegas     | Indian Springs | Clark County      | 2023-02     | 2025-12    |             35 |                 0 |      21343 |
| 89046 | Las Vegas     | Searchlight    | Clark County      | 2023-02     | 2025-12    |             35 |                 0 |      21792 |
| 37057 | Nashville     | Dixon Springs  | Trousdale County  | 2022-02     | 2025-12    |             47 |                 0 |      18523 |
| 37118 | Nashville     | Milton         | Rutherford County | 2022-02     | 2025-12    |             47 |                 0 |      20794 |
| 37151 | Nashville     | Riddleton      | Smith County      | 2022-02     | 2025-12    |             47 |                 0 |      25774 |
| 38552 | Nashville     | Chestnut Mound | Smith County      | 2022-02     | 2025-12    |             47 |                 0 |      27929 |
| 85355 | Phoenix       | Waddell        | Maricopa County   | 2018-01     | 2025-12    |             93 |                 3 |       7506 |
| 85264 | Phoenix       | Fort McDowell  | Maricopa County   | 2023-12     | 2025-12    |             25 |                 0 |      19740 |
| 85322 | Phoenix       | Arlington      | Maricopa County   | 2023-12     | 2025-12    |             25 |                 0 |      19174 |


Where do gaps fall (by first-observed month)?


| first_obs   |   zips |
|:------------|-------:|
| 2018-01     |     10 |
| 2018-02     |      1 |
| 2019-02     |      2 |
| 2021-02     |      1 |
| 2022-02     |      9 |
| 2023-02     |      2 |
| 2023-12     |      2 |


## Name-collision check

Metro labels containing a target-city name that were *not* selected (expected: unrelated places such as Austin MN, Las Vegas NM):


| Metro               |   zips |
|:--------------------|-------:|
| Austin, MN          |     12 |
| Charlottesville, VA |     37 |
| Las Vegas, NM       |      7 |
