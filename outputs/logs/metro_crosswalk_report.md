# Metro membership: `Metro` column vs. county crosswalk (step 2)

Crosswalk: Census CBSA delineation file, July 2023 vintage (`list1_2023.xlsx`), matched on state abbreviation + county name.


Counties in the eight CBSAs: 77. Five CBSA titles matched the ZHVI labels exactly; Atlanta, Austin and Las Vegas are titled differently in the July 2023 delineation (Atlanta-Sandy Springs-Roswell, Austin-Round Rock-San Marcos, Las Vegas-Henderson-North Las Vegas) and were matched by CBSA code (12060, 12420, 29820). The ZHVI labels appear to follow an earlier OMB delineation; that vintage gap is the likely reason for the county-level disagreements below (e.g. Lamar County GA is in the ZHVI Atlanta metro but not in the 2023 Atlanta CBSA, while Lumpkin County GA is the reverse). We did not obtain the earlier delineation to confirm this.


## Overall agreement (national ZIP file, ZIPs in either method's target set)

| status         |   zips |
|:---------------|-------:|
| both_agree     |   1087 |
| metro_col_only |     12 |
| xwalk_only     |      5 |


A ZIP is counted for each metro by the method that assigned it. `metro_col_only` = Metro column says target metro but its county is not in that CBSA; `xwalk_only` = county is in the CBSA but the Metro column is blank or another metro.


## By metro

| metro     |   Metro column |   county crosswalk |   both |   column only |   crosswalk only |
|:----------|---------------:|-------------------:|-------:|--------------:|-----------------:|
| Phoenix   |            149 |                149 |    149 |             0 |                0 |
| Austin    |             87 |                 86 |     86 |             1 |                0 |
| Atlanta   |            203 |                202 |    201 |             2 |                1 |
| Dallas    |            254 |                250 |    250 |             4 |                0 |
| Tampa     |            129 |                129 |    129 |             0 |                0 |
| Charlotte |            105 |                105 |    105 |             0 |                0 |
| Nashville |            102 |                102 |     98 |             4 |                4 |
| Las Vegas |             70 |                 69 |     69 |             1 |                0 |
| TOTAL     |           1099 |               1092 |   1087 |            12 |                5 |


## Crosswalk-only ZIPs (county in CBSA, but Metro column does not assign it) (5)

| metro_xwalk   |   zip | City        | CountyName     | State   | metro_col_label   |
|:--------------|------:|:------------|:---------------|:--------|:------------------|
| Atlanta       | 30533 | Dahlonega   | Lumpkin County | GA      | (blank)           |
| Nashville     | 37033 | Centerville | Hickman County | TN      | (blank)           |
| Nashville     | 37098 | Lyles       | Hickman County | TN      | (blank)           |
| Nashville     | 37137 | Nunnelly    | Hickman County | TN      | (blank)           |
| Nashville     | 38454 | Duck River  | Hickman County | TN      | (blank)           |


## Metro-column-only ZIPs (column says target metro, county not in that CBSA) (12)

| metro_col   |   zip | City         | CountyName       | State   |
|:------------|------:|:-------------|:-----------------|:--------|
| Atlanta     | 30204 | Barnesville  | Lamar County     | GA      |
| Atlanta     | 30257 | Milner       | Lamar County     | GA      |
| Austin      | 78654 | Marble Falls | Burnet County    | TX      |
| Dallas      | 75147 | Mabank       | Van Zandt County | TX      |
| Dallas      | 75169 | Wills Point  | Van Zandt County | TX      |
| Dallas      | 76270 | Alvord       | Montague County  | TX      |
| Dallas      | 76486 | Perrin       | Jack County      | TX      |
| Las Vegas   | 89034 | Mesquite     | Lincoln County   | NV      |
| Nashville   | 37012 | Alexandria   | Dekalb County    | TN      |
| Nashville   | 37095 | Liberty      | Dekalb County    | TN      |
| Nashville   | 38461 | Hampshire    | Lewis County     | TN      |
| Nashville   | 38569 | Lancaster    | Dekalb County    | TN      |


## Disagreements (both assign, to different metros) (0)
