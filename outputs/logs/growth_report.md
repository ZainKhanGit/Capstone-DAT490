# Growth measures (step 8)

Year-over-year change (percent), December 2019 as the reference point, periods pre-2020 (2018-19), 2020-2022 and 2023-2025. Nominal dollars. All months are kept in the panel; `in_window` marks 2018-01 to 2025-12.


Panel rows: 351,680 (1,099 ZIPs x 320 months); in window: 105,504. ZORI panel: 120,400 rows, 57,774 observed ZIP-months in window.


## Reference month (Dec 2019)

| metro_short   |   zips |   have_ref |   lack_ref |
|:--------------|-------:|-----------:|-----------:|
| Atlanta       |    203 |        202 |          1 |
| Austin        |     87 |         84 |          3 |
| Charlotte     |    105 |        104 |          1 |
| Dallas        |    254 |        253 |          1 |
| Las Vegas     |     70 |         68 |          2 |
| Nashville     |    102 |         98 |          4 |
| Phoenix       |    149 |        147 |          2 |
| Tampa         |    129 |        129 |          0 |


Check: index at the reference month equals 100 for all 1085 ZIPs with a value: True. ZIPs without a Dec 2019 value cannot be indexed (they are the late entrants flagged in step 1).


Sanity: non-positive values: 0. Largest absolute month-over-month change: 8.6%. ZIP-months with a change above 5%: 287 in the full history, 70 inside the analysis window (by year: {2000: 1, 2001: 1, 2004: 3, 2005: 5, 2008: 76, 2009: 123, 2010: 4, 2011: 2, 2012: 1, 2013: 1, 2018: 1, 2021: 68, 2022: 1}). They cluster in the 2008-09 crash (Phoenix, Las Vegas) and the 2021 boom (Austin, Phoenix), i.e. real market moves, not index artifacts: 0 fall within three months of a ZIP first appearing.


## Median December-to-December growth (%) by metro and year

A sanity check against the known pandemic-era pattern, not an analysis.


| metro_short   |   2018 |   2019 |   2020 |   2021 |   2022 |   2023 |   2024 |   2025 |
|:--------------|-------:|-------:|-------:|-------:|-------:|-------:|-------:|-------:|
| Atlanta       |    8.9 |    5.9 |   11.3 |   20.7 |   13.5 |    3.6 |    1.8 |   -1.9 |
| Austin        |    4.2 |    4.1 |   13.1 |   33.1 |    5.4 |   -7.5 |   -3   |   -5   |
| Charlotte     |    5.8 |    6.3 |   13.2 |   20.1 |   12.6 |    2.7 |    2.5 |   -0.2 |
| Dallas        |    6.9 |    4.3 |    8.2 |   18.8 |   15.1 |   -0.4 |    0.4 |   -3.6 |
| Las Vegas     |   13.3 |    2.5 |    6.2 |   22.3 |    9.3 |   -0.8 |    5.7 |   -1.6 |
| Nashville     |    6.3 |    7.7 |    9.8 |   21.2 |   11.3 |    1.2 |    2.6 |    0.5 |
| Phoenix       |    8.4 |    6.4 |   14.8 |   28.5 |    6.5 |    0   |    0.4 |   -3   |
| Tampa         |    7.1 |    5.4 |   10.7 |   24   |   18.2 |    1.6 |   -1   |   -5.5 |


## Median cumulative growth (%) by metro and period


| metro_short   |   cum_2017_2019 |   cum_2019_2022 |   cum_2022_2025 |   cum_2019_2025 |
|:--------------|----------------:|----------------:|----------------:|----------------:|
| Atlanta       |            15.4 |            52.7 |             3.6 |            58   |
| Austin        |             9.1 |            60.4 |           -14.5 |            35.3 |
| Charlotte     |            12.2 |            54.3 |             4.6 |            62.9 |
| Dallas        |            12.1 |            47.9 |            -3.8 |            42.2 |
| Las Vegas     |            16.5 |            42.7 |             2.5 |            46.2 |
| Nashville     |            14.8 |            47.7 |             4.4 |            54.8 |
| Phoenix       |            15.3 |            56.9 |            -3.1 |            52.8 |
| Tampa         |            12.8 |            62.2 |            -5.3 |            53.6 |


## Work in logs? Skewness of the Dec 2019 level


| metro_short   |   skew_level |   skew_log_level |
|:--------------|-------------:|-----------------:|
| Atlanta       |         2.1  |             0.44 |
| Austin        |         1.64 |             0.66 |
| Charlotte     |         2.87 |             0.15 |
| Dallas        |         3.13 |             0.67 |
| Las Vegas     |         1.52 |             0.4  |
| Nashville     |         1.68 |             0.81 |
| Phoenix       |         3.58 |             0.71 |
| Tampa         |         1.67 |             0.49 |
| ALL (pooled)  |         2.57 |             0.41 |

Levels are right-skewed in most metros and the logs are closer to symmetric, which supports plotting levels on a log scale and estimating growth in logs or percent. Cumulative growth is already a ratio, so it is plotted in percent.


## Preview: rank correlation of growth with distance (sanity check of the columns)

Spearman correlation between city-hall distance and cumulative growth, by metro. This only checks that signs are plausible; the gradient analysis proper belongs to the EDA and the later models. Positive = outer ZIPs grew faster.


| metro     |   cum_2017_2019 |   cum_2019_2022 |   cum_2022_2025 |
|:----------|----------------:|----------------:|----------------:|
| Atlanta   |            0.01 |            0.21 |            0.6  |
| Austin    |           -0.12 |            0.14 |            0.37 |
| Charlotte |           -0.11 |            0    |           -0    |
| Dallas    |            0.04 |            0.08 |           -0.01 |
| Las Vegas |           -0.53 |           -0.37 |           -0.04 |
| Nashville |            0.69 |           -0.21 |            0.61 |
| Phoenix   |            0.04 |           -0.01 |           -0.04 |
| Tampa     |            0.08 |            0.23 |           -0.27 |


## ZORI growth columns

`zori_growth.csv` keeps the 479 ZIPs with ZORI at both Dec 2019 and Dec 2025 (fixed sample, see the ZORI limitation in `zori_coverage_report.md`); growth in a changing sample would mix real rent changes with ZIPs entering the index. Median cumulative rent growth Dec 2019 to Dec 2025 by metro (%):


| metro_short   |   count |   median |
|:--------------|--------:|---------:|
| Atlanta       |      97 |     42.5 |
| Austin        |      40 |     15.5 |
| Charlotte     |      33 |     37   |
| Dallas        |      96 |     29   |
| Las Vegas     |      42 |     36.9 |
| Nashville     |      30 |     33.6 |
| Phoenix       |      91 |     38.5 |
| Tampa         |      50 |     53.1 |
