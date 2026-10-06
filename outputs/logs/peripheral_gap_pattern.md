# One pattern across the pipeline: data problems sit at the periphery

Most of the data-quality checks so far point the same way: the ZIPs we lose, flag or cannot match tend to be the ones farthest from the metro center. This section collects them in one table and also records the two flags that do not follow the pattern.


For each flag: how many ZIPs, the median distance (city-hall definition, miles) of flagged vs. unflagged ZIPs, the same comparison as a within-metro percentile (0 = at the center, 1 = farthest ZIP in that metro; removes differences in metro size), the share of flagged ZIPs that are 30+ miles out (all ZIPs: 30%), and a one-sided Mann-Whitney p-value for 'flagged ZIPs have higher within-metro percentile'.


| flag                                                         |   zips |   median_mi_flagged |   median_mi_rest |   median_pctile_flagged |   median_pctile_rest |   pct_flagged_at_30plus_mi |   p_one_sided |
|:-------------------------------------------------------------|-------:|--------------------:|-----------------:|------------------------:|---------------------:|---------------------------:|--------------:|
| ZHVI series incomplete 2018-2025 (step 1)                    |     27 |                37.5 |             20.1 |                    0.84 |                 0.49 |                         67 |        0      |
| of which: begins after Jan 2018                              |     17 |                42.2 |             20.1 |                    0.87 |                 0.5  |                         88 |        0      |
| Metro column assigns ZIP, county crosswalk does not (step 2) |     12 |                49.7 |             20.2 |                    0.92 |                 0.5  |                        100 |        0      |
| No 2015-2019 ACS ZCTA row (step 4)                           |      7 |                25.6 |             20.5 |                    0.56 |                 0.5  |                         14 |        0.394  |
| 2015-2019 WFH share unreliable, MOE/estimate > 0.5 (step 4)  |    248 |                39.1 |             17.4 |                    0.83 |                 0.43 |                         69 |        0      |
| No ZORI at all, 2018-2025 (step 5)                           |    300 |                38   |             16.2 |                    0.82 |                 0.4  |                         69 |        0      |
| ZORI present but not for every month 2018-2025 (step 5)      |    401 |                18.3 |             21.8 |                    0.46 |                 0.54 |                         22 |        0.9999 |


## Burden by distance band

Share of ZIPs in each band carrying each flag (%).


| dist_band   |   zips |   zhvi_incomplete |   metro_col_only |   acs_baseline_missing |   wfh_unreliable |   zori_missing |   zori_incomplete |
|:------------|-------:|------------------:|-----------------:|-----------------------:|-----------------:|---------------:|------------------:|
| 0-10 mi     |    238 |                 0 |                0 |                      0 |               11 |              6 |                36 |
| 10-20 mi    |    299 |                 1 |                0 |                      1 |                8 |             10 |                44 |
| 20-30 mi    |    237 |                 2 |                0 |                      1 |               11 |             20 |                40 |
| 30+ mi      |    325 |                 6 |                4 |                      0 |               53 |             64 |                27 |


## Same view by metro (median within-metro percentile of flagged ZIPs)


| metro     |   zhvi_incomplete |   metro_col_only |   acs_baseline_missing |   wfh_unreliable |   zori_missing |   zori_incomplete |
|:----------|------------------:|-----------------:|-----------------------:|-----------------:|---------------:|------------------:|
| Atlanta   |              0.76 |             0.88 |                 nan    |             0.85 |           0.84 |              0.38 |
| Austin    |              0.64 |             0.89 |                 nan    |             0.9  |           0.83 |              0.52 |
| Charlotte |              0.84 |           nan    |                 nan    |             0.81 |           0.76 |              0.46 |
| Dallas    |              0.84 |             0.95 |                   0.57 |             0.78 |           0.83 |              0.43 |
| Las Vegas |              0.93 |             0.97 |                   0.56 |             0.86 |           0.89 |              0.31 |
| Nashville |              0.84 |             0.93 |                 nan    |             0.78 |           0.7  |              0.29 |
| Phoenix   |              0.85 |           nan    |                   0.56 |             0.92 |           0.89 |              0.49 |
| Tampa     |            nan    |           nan    |                 nan    |             0.88 |           0.81 |              0.53 |

(NaN = no ZIPs with that flag in the metro. A value above 0.5 means the flagged ZIPs are in the outer half of that metro.)


## Exceptions

- **No 2015-2019 ACS row (7 ZIPs): not peripheral.** Their within-metro percentile is 0.56 vs 0.50 for the rest (p = 0.39) and only 1 of the 7 is 30+ miles out. These are fast-growing suburban ZIPs (Frisco, McKinney, Arlington, Surprise, Las Vegas) that appear to post-date the 2010 ZCTA vintage, i.e. a growth-related gap rather than a distance-related one. With 7 ZIPs the test has little power, so this says 'no evidence of a peripheral pattern', not 'no pattern'.
- **ZORI incomplete (present but patchy): not peripheral.** Outer ZIPs mostly have no ZORI at all, so the ones with partial series are inner and middle ZIPs that entered the rent index late. The right reading is that ZORI is missing at the periphery and growing in the interior over time.


## What it means for the analysis

- 42 ZIPs (3.8%) carry at least one of the three hard problems (incomplete ZHVI, Metro/crosswalk disagreement, missing 2015-2019 ACS row); the first two are strongly peripheral, the third is not, so this pooled figure mixes the two; their median distance is 38.5 mi versus 20.0 mi for the rest.
- Dropping any of these ZIPs trims the outer edge of each metro, which is where the price-distance gradient is estimated. A gradient fitted on 'clean' ZIPs only describes the inner metro and can be steeper or flatter than the full-metro gradient.
- ZORI coverage is the strongest case (see table): rent-based checks will be representative of the urban core and inner suburbs, not the outer ring, and the ZORI sample also grows over time, so rent trends must be computed on a fixed set of ZIPs.
- The unreliable-WFH flag is not missingness but noise: the 2015-2019 exposure measure is least precise in exactly the outer ZIPs. SQ2 plots should show these separately or weight by precision.
- Practical rule for the EDA: keep every ZIP by default, carry the flags in the data, and show results for the full sample and for the flag-free sample side by side.
