---
title: "Interpretation audit of Sections 2.2 to 2.6"
subtitle: "Team 10 EDA report, version dated October 11, 2026"
---

> Historical project record: this audit was prepared for the earlier EDA report. The current capstone rough draft incorporates later formal models, corrected distance definitions, and additional robustness checks. Use `report/Team10_Rough_Draft.pdf` and `docs/STATUS.md` for the current conclusions.

# Status

**All proposals in this list were applied to the report (version dated October 11, 2026), plus the two-center price-level fix.** The list below is kept as the record of what each sentence rested on and what changed. After applying it, the report's numbers were re-checked by `src/check_report_numbers.py` (267 checks: each number is recomputed from the data and confirmed to appear in the report text).

Three further corrections turned up while applying the edits, none of them wording:

- The median Dec 2019 value of unflagged ZIP codes is **$269k**, not $268k (an earlier printout truncated instead of rounding). The Phoenix unflagged median is $297k, not $296k.
- Austin's level R-squared runs **0.15 to 0.24**, not 0.15 to 0.25 (the maximum is 0.2449).
- The 16 Phoenix ZIP codes with an unreliable work-from-home share have a median distance of **56 miles** (I had first typed 53, from a slightly different group of 18).

# How to read this

Every interpretive claim in Sections 2.2 to 2.6 is listed with (1) the exact sentence, (2) the computed number it rests on, and (3) a classification:

- **Description**: says what a figure or table shows, and the number checks out.
- **Inference**: a reasonable step beyond the number (an explanation, a "which means"). Not wrong, but not shown by the data.
- **Stronger than supported**: does more work than the number behind it. A weaker wording is proposed.

Several claims rested only on figures I looked at. For those I ran extra checks for this audit (the script is `src/audit_checks.py`; tables are in `outputs/tables/audit_*.csv`). **These extra checks are not in the report.** Where they change a claim, the proposed wording uses them.

The "exact sentence" quoted in each entry is the wording before the edits.

## Where a claim does more work than its number (the short list)

| # | Claim | Problem |
|---|---|---|
| 5 | "clearest signs of a donut" (includes Tampa) | Tampa's inner and outer bands both gained on the middle bands; that is not a donut. Atlanta's inner decline also began before 2020. |
| 8 | "wedge ... northwest of Las Vegas's" | The Las Vegas top fifth points southwest and is not directional (p = 0.08). Wedges are significant in 5 of 8 metros, not in Tampa, Charlotte or Las Vegas. |
| 9 | "it is why one distance variable fits poorly" | Causal wording. Austin and Nashville have wedges and still fit moderately well. |
| 12 | "close to being the same ZIP codes" | Rank correlation 0.66 shares about 44% of the rank variance. Strong overlap, not identity. |
| 14 | "uninterpretable as an exposure effect" | Wording too strong, but the extra check supports the substance: with pre-2020 growth controlled the later slopes are +0.03 and +0.13. |
| 15 | "consistent with the hypothesis" | The timing is opposite to the plan's (positive only in 2023-25, not 2021-22), and the later slopes fall to about zero once pre-2020 growth is controlled. |
| 18b | "which the measure tracks closely" (education, housing type) | We have no education measure, and the correlation with housing type is only +0.15. |
| 20 | groups "follow metro and housing type" | Metro: supported (Cramer's V 0.60). Housing type: only the 48-ZIP Group 4 differs. |
| 22, 41 | groups "only moderately distinct" / "real types" | Silhouette 0.36 is weak structure by convention; one principal component explains 71% of path variance (a continuum). The report does not claim real types, but Section 3's wording is generous. |
| 24b, 24d | Austin "flattens only in 2023-25"; Phoenix level slope "steepens" | Intervals overlap in both; Phoenix's gradient depends on far-out ZIPs. |
| 25 | "the others are not distinguishable from no change" | Inconsistent: by the sentence's own rule Austin qualifies. |
| 29, 42 | "The two cores sit at different price levels" | True for Dallas-Fort Worth ($221k vs $183k), not Tampa-St. Petersburg ($220k vs $227k). Section 3 repeats it for both. |
| 31 | "A city hall is not where the jobs are" | No data behind it in this project. |
| 35a | "stronger in 2020-22" (Atlanta flag-free) | Intervals overlap. |
| 35b | "turns clearly negative" (Dallas flag-free) | A selected subsample; with all ZIPs the slope is -0.03. |
| 37 | "the pattern the plan said would point toward interest rates" | The plan did not name that pattern. Rents are smoothed and lag prices. |
| 40 | "four metros show none" / "Phoenix ... show nothing" | Inconsistent with Section 2.2, which says Phoenix goes the other way. |

# Part A. Donut and wedge language

## A1. Donut language (Section 2.5)

**1.** "In Atlanta the innermost band (0-10 miles) fell to 85% of the metro's median index by December 2022 and 83% by December 2025 while the 30-plus-mile band rose to about 105%."

- *Rests on:* band medians of each ZIP's index divided by its metro's median. Atlanta 0-10 mi: 85.1 (Dec 2022) and 83.0 (Dec 2025), bootstrap 95% interval 80.5 to 87.2 for 2025. Atlanta 30+ mi: 100.3 and 104.8, interval 103.6 to 106.2. Bands have 37 and 77 ZIPs.
- *Type:* **Description.** Checks out and survives resampling.

**2.** "In Tampa the 30-plus-mile band jumped to about 106% by December 2022 and stayed there, though the inner band also recovered to about 106% by 2025."

- *Rests on:* Tampa 30+ mi: 106.5 (2022), 106.7 (2025), 13 ZIPs, interval 101.9 to 110.6 for 2025. Tampa 0-10 mi: 105.8, interval 102.5 to 107.9, 22 ZIPs.
- *Type:* **Description**, except "recovered": the inner band never fell, it rose (from the Dec 2019 base). Use "also rose".

**3.** "In Austin and Las Vegas the outer band swings (Austin's dipped to about 92% in 2022 and recovered; Las Vegas's, with only 7 ZIP codes, fell to about 94% in 2022 and ended near 96%)."

- *Rests on:* Austin 30+ mi minimum 92.0 (15 ZIPs); Las Vegas 30+ mi minimum 93.5, end 95.6 (7 ZIPs).
- *Type:* **Description.** Small groups, already flagged in the text.

**4.** "Every metro followed the same broad shape ... Within most metros the distance bands move together: in Phoenix, Dallas and Charlotte each band's median stays within about 4% of the metro as a whole throughout."

- *Rests on:* maximum deviation of any band median from the metro: Phoenix 3.7%, Dallas 4.0%, Charlotte 3.6%. Metro median Dec 2022 index 143 to 162.
- *Type:* **Description.**

**5.** "The exceptions are the clearest signs of a donut."

- *Rests on:* the band medians above, with extra bootstrap intervals and the pre-2020 starting values.

  | Metro | Inner band index at Jan 2018, Dec 2019, Dec 2022, Dec 2025 | Outer band index at Dec 2019, Dec 2025 |
  |---|---|---|
  | Atlanta | 103.3, 100, 85.1, 83.0 | 100, 104.8 |
  | Nashville | 107.2, 100, 102.9, 97.1 | 100, 102.5 |
  | Austin | 99.5, 100, 98.1, 95.6 | 100, 101.4 |
  | Tampa | 97.4, 100, 101.7, 105.8 | 100, 106.7 |

- *Type:* **Stronger than supported.** Three problems.
  1. *Tampa is not a donut.* A donut means a weak center and a strong ring. In Tampa both the inner band and the outer band gained on the middle bands (the 10-20 and 20-30 mile bands are 97.7 and 98.8 in Dec 2025).
  2. *Atlanta's inner decline started before 2020.* The inner band was already falling relative to the metro (103.3 in Jan 2018 to 100 at Dec 2019). The post-2020 fall (15 points in three years) is much steeper than the earlier one (3.3 points in two years), so it is not just a continuation, but it is not new either. Nashville's inner decline was larger before 2020 (107.2 to 100) and then reversed in 2022, so Nashville does not show a post-2020 donut.
  3. *"Donut" is a label from the literature* (Ramani and Bloom), where it describes demand shifting to lower-density suburbs, measured with moves, rents and prices. Our evidence is relative price indexes of distance bands only.
- *Proposed wording:* "In Atlanta the inner band's price index fell relative to the metro (to 83% by December 2025, bootstrap interval 80.5 to 87.2) while the outer band rose (to 104.8%, interval 103.6 to 106.2), the pattern the literature calls a donut; the inner-band decline had begun before 2020 (103.3% in January 2018). Nashville and Austin show weaker versions. In Tampa the inner and outer bands both gained on the middle bands, which is not a donut."

**6.** "In Phoenix and Las Vegas the smooth curves are humped, with values peaking 10 to 25 miles from city hall and falling beyond (Figure 6 for Phoenix), which a straight line flattens into a near-zero or mildly negative slope." (Section 2.2)

- *Rests on:* LOWESS peak at 23.5 miles (Phoenix) and 15.2 miles (Las Vegas). A quadratic term in log value on distance is negative and significant (robust errors): Phoenix p = 0.015 (Dec 2019) and 0.004 (Dec 2025); Las Vegas p < 0.001. Not significant in Austin, Dallas, Tampa or Charlotte.
- *Type:* **Description**, now supported by a number. Caveat that the text omits: the Phoenix hump rests on sparse far ZIPs. Dropping the 20 ZIPs beyond 40 miles gives a level slope of **+8.1%** per 10 miles (interval +1.4 to +15.1): inside 40 miles values *rise* with distance, so Phoenix's negative gradient comes from the far tail. Atlanta also shows a significant curved term by 2025 (peak at 24.5 miles, p = 0.008).

## A2. Wedge descriptions (Section 2.3)

**7.** (extra check, applies to claim 8.) I tested whether each metro's top fifth of Dec 2019 values is concentrated in one direction from the center, by comparing its compass-bearing concentration (R, 0 = all directions, 1 = one direction) with random fifths of the same ZIPs (5,000 permutations).

| Metro | Mean direction of top fifth | R | Permutation p | % within 60 deg of mean direction |
|---|---|---|---|---|
| Phoenix | NE | 0.66 | < 0.001 | 76 |
| Austin | NW | 0.72 | 0.0004 | 76 |
| Atlanta | N | 0.77 | < 0.001 | 90 |
| Dallas (from midpoint of the two halls) | NE | 0.73 | < 0.001 | 88 |
| Nashville | S | 0.63 | 0.002 | 74 |
| Tampa | NW | 0.42 | 0.77 | 58 |
| Charlotte | S | 0.27 | 0.15 | 57 |
| Las Vegas | **SW** | 0.47 | 0.08 | 57 |

**8.** "In most metros the highest-value ZIP codes form a wedge on one side of the center: north and northeast of Phoenix's city hall, west and northwest of Austin's, north of Atlanta's, northwest of Las Vegas's, and in a band north of both city halls in Dallas-Fort Worth, where both cores sit in lower fifths."

- *Rests on:* the maps (looked at) plus the test above, and for the Dallas clause: 63% of the 65 ZIPs within 10 miles of either hall are in the bottom two fifths (40% expected if no pattern).
- *Type:* **Description** for Phoenix, Austin, Atlanta, Dallas (directions match the test) and for "most metros" (5 of 8, counting Nashville). **Stronger than supported for Las Vegas**: its top fifth points southwest, not northwest, and is not significantly directional (p = 0.08); the dark northwest area on the map is a few very large ZIPs. Tampa and Charlotte show no wedge either.
- *Proposed wording:* "In five of the eight metros (Phoenix, Austin, Atlanta, Dallas-Fort Worth and Nashville) the highest-value ZIP codes are concentrated on one side of the center (a permutation test on direction gives p < 0.01 in each): northeast of Phoenix, northwest of Austin, north of Atlanta, northeast of the two Dallas-Fort Worth halls, south of Nashville. Tampa, Charlotte and Las Vegas show no clear direction (p = 0.77, 0.15, 0.08). In Dallas-Fort Worth both cores sit in the lower fifths (63% of ZIPs within 10 miles of either hall are in the bottom two fifths)."

**9.** "A wedge is not the shape the monocentric model predicts, and it is why one distance variable fits poorly in Section 2.2."

- *Rests on:* theory (the model makes value depend on distance only, i.e. rings), plus R-squared of the distance fits: Phoenix 0.05 to 0.07, Dallas 0.005. But Austin (0.15 to 0.24) and Nashville (0.26 to 0.37) have significant wedges and moderate fits; Charlotte has no wedge and the best fit (about 0.5).
- *Type:* first half **Inference from theory**; "it is why" is **stronger than supported** (a causal claim; the pattern fits Phoenix and Dallas but not all metros).
- *Proposed wording:* "... which would help explain why one distance variable fits poorly in the metros where the wedge is strongest (Phoenix, Dallas)."

**10.** "In Atlanta, Austin and Nashville the ZIP codes around the center grew more slowly than the metro in 2023-25 and the outer ones faster, which matches their positive 2023-25 slopes."

- *Rests on:* median growth relative to the metro, inside 10 miles vs beyond 30 miles, 2023-25 (points per year): Atlanta -2.90 vs +1.50; Austin -1.32 vs +0.43; Nashville -1.70 vs +0.84. Group sizes (inner/outer ZIPs) 37/79, 30/18, 19/44; outer vs inner differs with p < 0.001 (Atlanta), 0.003 (Austin), < 0.001 (Nashville), Mann-Whitney. Growth slopes +1.03, +0.63, +0.72.
- *Type:* **Description.** Checks out.

**11a.** "Charlotte has a similarly slow core, but its far-south ZIP codes are also slow, which is why its slope is near zero."

- *Rests on:* Charlotte inside 10 miles -0.74 (22 ZIPs), beyond 30 miles +0.22 (36 ZIPs), a difference that is **not significant** (p = 0.96); far-south (30+ miles, 135 to 225 deg) -0.71 (10 ZIPs) vs +0.57 elsewhere beyond 30 miles (26 ZIPs).
- *Type:* "similarly slow core" is weaker than in Atlanta, Austin and Nashville (inner -0.74 is small and the inner-outer difference is not significant), and "which is why" is an **inference** from 10 ZIPs. Use "Charlotte's core is only mildly slow, and its far-south ZIP codes are also slow, which may be why its slope is near zero".

**11b.** "Before 2020 ... Atlanta's ZIP codes north of city hall were slow and those south and southeast fast; the Dallas and Fort Worth cores grew faster than their surroundings, with the northern suburbs slower; Phoenix's inner core and far southeast were fastest."

- *Rests on:* Atlanta pre-2020 sector medians (relative growth): N -3.69 (33 ZIPs), NE -1.80, SE +2.22 (17), S +1.08. Dallas-Fort Worth: within 10 miles of either hall +2.44 (65) vs -0.54 beyond (186); beyond 10 miles north -3.53 (62) vs south +1.43 (29). Phoenix: inside 10 miles +0.93 (33); beyond 30 miles southeast +2.63 (20) vs +0.74 elsewhere.
- *Type:* **Description** for Atlanta and Dallas. For Phoenix, "inner core ... fastest" is **stronger than supported**: the inner core is only +0.9 above the metro median, while inner cores in Dallas (+2.2), Tampa (+1.7) and Charlotte (+1.4) are higher. Say "Phoenix's far southeast was fastest (+2.6 points a year above the metro median)".

**11c.** "In seven of eight metros (all but Austin) growth varied more across ZIP codes before 2020 than in 2020-22 (the standard deviation of annualized growth was 4.9 against 3.5 points a year in Atlanta and 4.2 against 1.9 in Dallas), so the post-2020 maps are, if anything, quieter than the pre-2020 ones."

- *Rests on:* within-metro SD of annualized growth, pre-2020 vs 2020-22: Phoenix 2.76/1.76, Atlanta 4.93/3.53, Dallas 4.24/1.89, Tampa 2.56/1.61, Charlotte 2.96/2.11, Nashville 2.23/2.06, Las Vegas 2.38/2.14; Austin 1.64/2.22.
- *Type:* **Description**, but the comparison is partly mechanical: the pre-2020 window is two years and the others three, and annualized growth over a shorter window is noisier. Add: "(the pre-2020 window is two years long, which by itself inflates annualized dispersion)".

# Part B. The hypothesis wording (Section 2.4)

**12.** "The first thing to know is that high-work-from-home and high-income ZIP codes are close to being the same ZIP codes ... the work-from-home share has a rank correlation of +0.66 with income, +0.74 with home value and +0.74 with the share of management and professional workers."

- *Rests on:* within-metro rank correlations (1,076 ZIPs): +0.66, +0.74, +0.74. A rank correlation of 0.66 shares about 44% of the rank variance.
- *Type:* the numbers are **Description**; "close to being the same ZIP codes" is **stronger than supported**.
- *Proposed wording:* "High-work-from-home and high-income ZIP codes overlap strongly (rank correlation +0.66 with income, +0.74 with home value)." The same fix applies to the Summary ("tracks income so closely").

**13a.** "Expensive ZIP codes were already growing slowest before 2020 (growth against December 2019 value, -0.72)."

- *Rests on:* within-metro rank correlation -0.72.
- *Type:* **Stronger than supported** in "slowest" (a correlation says "tended to"). A competing explanation is catch-up by cheaper ZIPs, which the data cannot separate. *Proposed:* "More expensive ZIP codes tended to grow more slowly before 2020 (rank correlation -0.72)."

**13b.** "So the pre-2020 relationship between exposure and growth is strongly negative (-1.48 points a year per +5 percentage points of work-from-home share, R-squared 0.13) ... before remote work could matter, affluent ZIP codes were on a slower path."

- *Rests on:* slope -1.48 (interval -1.71 to -1.25), R-squared 0.128, rank correlation -0.56; income vs pre-2020 growth -0.69.
- *Type:* **Description** (number), with the "affluent ZIP codes were on a slower path" part an **inference** (same caveat as above). "Strongly" is fine for the slope, but R-squared 0.13 is modest; "clearly negative" is safer.

**14.** "That pre-trend makes the levels of the later slopes uninterpretable as an exposure effect."

- *Rests on:* extra check, within-metro regressions of growth on work-from-home share with controls (slope per +5 pp, robust 95% interval):

  | Outcome | Work-from-home share only | + pre-2020 growth | + pre-2020 growth + income |
  |---|---|---|---|
  | 2020-22 growth | -0.27 [-0.49, -0.05] | +0.03 [-0.13, +0.20] | -0.15 [-0.36, +0.06] |
  | 2023-25 growth | +0.39 [+0.12, +0.67] | +0.13 [-0.03, +0.30] | -0.00 [-0.15, +0.15] |

- *Type:* **Stronger than supported** in wording ("uninterpretable"), but the extra check supports the substance: the later slopes are mostly accounted for by the pre-2020 trend.
- *Proposed wording:* "Controlling for pre-2020 growth reduces the later slopes to +0.03 and +0.13 (intervals include zero), so they mostly reflect the earlier trend."

**15.** "The direction of travel (-1.48 to -0.30 to +0.40) is consistent with the hypothesis, but with this starting point it is not evidence for it."

- *Rests on:* three within-metro slopes (-1.48 [-1.71, -1.25], -0.30 [-0.46, -0.14], +0.40 [+0.26, +0.55]). The plan predicted a positive relationship strongest in 2021-22 and weakening after (Section 2.4's own first paragraph). Pooled across metros: +0.17 [-0.01, +0.35] in 2020-22 and -0.10 [-0.28, +0.09] in 2023-25.
- *Type:* **Stronger than supported.** (1) The timing is the opposite of the prediction: the only positive within-metro slope is in 2023-25, not 2021-22. (2) With pre-2020 growth controlled, the later slopes are about zero (claim 14). "Consistent with the hypothesis" is true only of the bare fact that the slope rises over time.
- *Proposed wording:* "The slope rises across the three periods, but its only positive value is in 2023-25 (the plan expected the strongest relationship in 2021-22), and it falls to about zero once pre-2020 growth is controlled (+0.03 and +0.13). We do not read it as support for the hypothesis." The Summary and Section 3 should be checked against whichever wording you choose.

**16.** "A slope that is less negative than before could reflect exposure, or simply the same affluent ZIP codes flattening out, or anything else that hit expensive homes differently, such as the 2022 rate shock."

- *Rests on:* no number; a list of alternatives. The extra check in claim 14 favors the second.
- *Type:* **Inference** (a hedge). Fine as written.

**17.** "The strongest relationship in the figure is the pre-2020 placebo, and the plan's predicted positive relationship in 2020-22 does not appear within metros."

- *Rests on:* R-squared 0.128 (pre-2020) vs 0.013 and 0.028; within-metro 2020-22 slope -0.30 [-0.46, -0.14]. Note: the pooled version, which includes differences between metros and is closest to the plan's design, is +0.17 [-0.01, +0.35], borderline positive.
- *Type:* **Description**, accurate because it says "within metros".

**18a.** "Dropping the 233 ZIP codes in this sample with an unreliable estimate ... barely changes the slopes (-1.41, -0.26, +0.52), though those ZIP codes scatter much more widely."

- *Rests on:* slopes verified. Scatter: residual SD of growth after the work-from-home fit, unreliable vs reliable ZIPs: 3.47 vs 3.21 (pre-2020), 2.51 vs 2.22 (2020-22), 2.35 vs 1.89 (2023-25), i.e. 8% to 24% larger.
- *Type:* slopes **Description**. "Much more widely" is **stronger than supported**; use "somewhat more widely (8% to 24% larger residual spread)".

**18b.** "Nothing here separates exposure from income, education and housing type, which the measure tracks closely, and nothing controls for them."

- *Rests on:* correlations: income +0.66, management/professional share +0.74, single-family share +0.15, 20-plus-unit share +0.12. **We have no education variable.**
- *Type:* **Stronger than supported** for education (not measured) and for housing type ("tracks closely" is false at +0.15). Also, "nothing controls for them" is true of the report but not of the extra check in claim 14.
- *Proposed wording:* "Nothing in the report separates exposure from income and occupation mix, which it tracks closely (rank correlations +0.66 and +0.74); we have no education measure."

# Part C. The clusters (Section 2.5)

Extra checks on the four-group k-means solution (1,072 ZIPs):

- Stability to the starting point: adjusted Rand index vs the reported solution is 0.99 to 1.00 across 10 random starts (stable).
- Stability to resampling: 40 bootstrap resamples, recluster, label all ZIPs: median adjusted Rand 0.85, but 5th percentile 0.45 (unstable in some resamples).
- Silhouette by group: 0.41, 0.35, 0.31, 0.26; 25% of ZIPs have a silhouette below 0.25. Conventional guidance puts 0.26 to 0.50 at "weak structure that may be artificial".
- Principal components of the paths: the first explains 70.6% of the variance, the next two 15.5% and 7.5%. One dominant dimension (overall amplitude) is what a continuum looks like.
- Agreement with labels: adjusted Rand with metro 0.17, with distance band 0.01. Cramer's V: cluster by metro 0.60, cluster by distance band 0.18. Distance explained by cluster (Kruskal-Wallis epsilon-squared) 0.058; single-family share 0.092.

**19.** "Group 3 (89 ZIP codes, 74% of them in Austin) shows a boom and a correction, ending about 33% above December 2019 after a peak near 169. Group 4 (48 ZIP codes, median 4 miles from city hall, 18% single-family detached homes, mostly Atlanta and Dallas) rose least, peaking near 128. Groups 1 and 2 (520 and 415 ZIP codes) differ mainly in amplitude."

- *Rests on:* group means and the profile table; PCA above supports "mainly amplitude".
- *Type:* **Description.** One caution: Group 3 is mostly Austin, so describing it as a path shape and describing it as "Austin's pattern" are the same thing.

**20.** "The groups follow metro and housing type more than distance: median distances are 22, 20, 15 and 4 miles, so only the small urban-core group is distinctively central."

- *Rests on:* median distances; Cramer's V 0.60 (metro) vs 0.18 (distance band); epsilon-squared 0.058 (distance) and 0.092 (single-family share).
- *Type:* "metro more than distance" is **Description** (supported). "Housing type" is **stronger than supported**: the single-family share differs only for the 48-ZIP Group 4 (18% vs 65% to 71%).
- *Proposed wording:* "The groups follow metro more than distance (Cramer's V 0.60 vs 0.18); housing type separates only the small Group 4."

**21.** "The plan expected three to five groups including delayed appreciation and stagnation; we find a boom-and-correction group and a low-appreciation group but no delayed-appreciation group."

- *Rests on:* group mean paths.
- *Type:* **Description**, but with a method caveat the text omits: k-means on the log index is dominated by amplitude (first principal component 71%), so shape types such as delayed appreciation may simply not separate. We did not try shape-only clustering. Add: "(clustering on the log index is dominated by overall amplitude; we did not test shape-only clustering)".

**22.** "The silhouette width is modest (0.22 to 0.38 across two to eight groups; 0.36 at four, no better than 0.375 at two), so we cannot say that four is the right number of groups or that the groups are real types and not a partition of a continuum."

- *Rests on:* silhouette values (verified) and the extra checks above.
- *Type:* **Description / appropriate hedge.** This sentence already says the groups are not shown to be real types. The extra checks support going one step further: the first principal component alone explains 71% of path variance, which points to one continuous dimension. Proposed addition: "...a partition of a continuum; consistent with that, one dimension (overall amplitude) accounts for 71% of the variation in the paths."
- *Where the wording drifts above this sentence:* the figure and Table 5 call the clusters "Group 1 to 4", which is fine, but nothing in the report calls them "types" except Section 3's "moderately distinct".

# Part D. Other interpretive claims in 2.2 to 2.6

**23.** "Home values fall with distance in six of the eight metros, but the strength varies (Table 3, Figure 4)."

- *Rests on:* level slopes with 95% intervals excluding zero in Phoenix, Austin, Atlanta, Tampa, Charlotte, Nashville (Atlanta's Dec 2025 interval touches zero: -3.0 [-6.0, +0.1]); Dallas and Las Vegas intervals include zero. *Type:* **Description.**

**24a.** "Only Atlanta follows it and keeps going: its level slope moves from -7.7% to -6.0% to -3.0% and its growth slope from -0.44 to +0.69 to +1.03 points per year per 10 miles."

- *Rests on:* Table 3. The growth-slope shift is clear (pre-2020 -0.44 [-0.87, -0.01] vs 2020-22 +0.69 [+0.39, +0.99]); the level-slope intervals at the three dates overlap (-7.7 [-10.6, -4.7] vs -3.0 [-6.0, +0.1]) and we did not test the change. *Type:* **Description** of point estimates; add "(the level-slope intervals overlap)".

**24b.** "Austin flattens only in 2023-25 (growth slope +0.63)."

- *Rests on:* +0.63 [+0.33, +0.94] vs 2020-22 +0.21 [-0.22, +0.64] (overlapping). *Type:* **Stronger than supported** ("flattens only"). *Proposed:* "Austin's growth slope is positive only in 2023-25 (+0.63), though it is not clearly different from its 2020-22 value (+0.21, interval -0.22 to +0.64)."

**24c.** "Tampa flattens in 2020-22 (+0.57) and then turns negative (-0.32), which contradicts 'holds'."

- *Rests on:* +0.57 [+0.29, +0.84] then -0.32 [-0.68, +0.03]. *Type:* **Inference**: the 2023-25 interval includes zero, so "turns negative" is a point estimate; "did not hold" is supported because the two intervals do not overlap.

**24d.** > "Phoenix goes the other way: its growth slope falls from +0.46 to -0.30 and its level slope steepens from -4.3% to -5.6%."

- *Rests on:* growth slopes +0.46 [+0.23, +0.69] and -0.30 [-0.47, -0.13] (clear). Level slopes -4.25 [-7.12, -1.29] and -5.56 [-8.69, -2.32] overlap heavily. *Type:* growth slope **Description**; "steepens" is **stronger than supported**, and the whole Phoenix gradient depends on far-out ZIPs (claims 6 and 34).
- *Proposed wording:* "Phoenix's growth slope falls from +0.46 to -0.30; its level slope is -4.3% to -5.6% with overlapping intervals, and the gradient disappears when 16 far-out ZIP codes with unreliable exposure estimates are dropped (Section 2.6)."

**24e.** > "Charlotte shows no change, and Nashville's outer ZIP codes were already outgrowing the center before 2020 (+1.02)."

- *Rests on:* Charlotte level slopes -18.1, -17.9, -18.4; growth slopes -0.38, +0.09, -0.21 (all intervals include zero or touch it). Nashville +1.02 [+0.81, +1.23]. *Type:* **Description.**

**25.** "The shifts in growth slopes for Atlanta, Tampa, Phoenix and Nashville are larger than the width of their own intervals (even if those are too narrow); the others are not distinguishable from no change."

- *Rests on:* a rough rule, largest shift between periods vs mean interval width: Atlanta 1.47 vs 0.61; Nashville 1.21 vs 0.44; Tampa 0.89 vs 0.72; Phoenix 0.76 vs 0.37; **Austin 0.76 vs 0.71**; Charlotte 0.47 vs 0.62; Dallas 0.11 vs 0.44; Las Vegas 0.20 vs 0.57.
- *Type:* **Inference** by a rough rule, not a test. It is also **inconsistent**: by its own rule Austin qualifies (marginally), and the report says Austin flattens. *Proposed:* "By a rough rule (the largest shift between periods exceeds the width of one interval), the growth slopes of Atlanta, Nashville, Tampa, Phoenix and, marginally, Austin shifted; Charlotte, Dallas and Las Vegas did not. This is a comparison, not a test."

**26a.** "Level slopes move little between December 2019 and December 2025 (within about 1.5 points everywhere except Atlanta, +4.7, and Austin, +2.2), which is arithmetic: a growth slope of +1 point per year per 10 miles adds only about 3 points to the level slope over three years."

- *Rests on:* slope differences verified (all others within 1.5); arithmetic: 1.01 cubed is about 1.03. *Type:* **Description + arithmetic.** Correct.

**26b.** "We also cannot compare with dense metros, because none are in our sample, so the plan's expectation that flattening is smaller here is untested."

- *Rests on:* no number; a logical statement. *Type:* **Description** (true).

**27.** "This does not recover a monocentric gradient (Figures 9 and 10). For Dallas, R-squared for home values stays at about 0.005 either way and the slope changes sign (-1.9% to +1.5% per 10 miles) with both intervals spanning zero. For Tampa, R-squared rises a little (0.065 to 0.080). For growth the nearest-center version helps most in 2020-22 (R-squared 0.004 to 0.019 in Dallas, 0.117 to 0.163 in Tampa)."

- *Rests on:* two_center_fits table. Note these R-squared values for levels are averages of the three dates (Tampa 0.071, 0.056, 0.067 vs 0.097, 0.076, 0.067); the text does not say so. *Type:* **Description.** Add "averaged over the three dates" for the level R-squared.

**28.** "Fitting each center's ZIP codes separately shows why a pooled line fails: Fort Worth ZIP codes rise in value with distance from Fort Worth's city hall by about +8% to +10% per 10 miles (R-squared about 0.10) while Dallas ZIP codes are flat or slightly negative."

- *Rests on:* Fort Worth group (101 ZIPs): +9.1%, +8.3%, +9.5% [about +3.2 to +15.4], R-squared 0.10 to 0.11; Dallas group: -2.7%, -1.5%, -2.2%, intervals spanning zero. *Type:* numbers **Description**; "shows why a pooled line fails" is an **Inference** (a mechanism read off two fits). Use "is consistent with a pooled line failing because...".

**29.** "The two cores sit at different price levels." and (Section 3) "the two-center metros have centers at different price levels"

- *Rests on:* median Dec 2019 value within 10 miles of each city hall: Dallas $221k (36 ZIPs) vs Fort Worth $183k (29 ZIPs); Tampa $220k (22) vs St. Petersburg $227k (20). Not tested for significance.
- *Type:* **Description for Dallas-Fort Worth; stronger than supported for Tampa-St. Petersburg**, where the two cores are at the same level. Section 3's plural wording is wrong for Tampa.
- *Proposed wording:* "In Dallas-Fort Worth the two cores sit at different price levels (median $221k within 10 miles of Dallas City Hall, $183k around Fort Worth's); in Tampa-St. Petersburg they do not ($220k and $227k)." Section 3: "Dallas and Fort Worth have cores at different price levels."

**30.** "This shows a second center matters for the price level, not that two city halls explain the gradient."

- *Type:* **Inference**, true only for Dallas-Fort Worth (claim 29). For Tampa the second center changes little (R-squared 0.065 to 0.080).

**31.** "A city hall is not where the jobs are, and suburban job centers are not in the test."

- *Rests on:* nothing in this project; no job-location data. The second clause is true. *Type:* first clause **stronger than supported**. *Proposed:* "A city hall is only a proxy for the center of employment, and we have no job-location data."

**32.** "The per-center growth slopes also move in opposite directions (Dallas from +0.47 in 2020-22 to -0.25 in 2023-25, Fort Worth from -0.29 to +0.37), an exploratory observation from small groups."

- *Rests on:* Dallas +0.47 [+0.23, +0.72] then -0.25 [-0.52, +0.02]; Fort Worth -0.29 [-0.54, -0.03] then +0.37 [+0.11, +0.62]. *Type:* **Description**, already labeled exploratory. Fine.

**33.** "Level slopes move by up to about 6 points per 10 miles (flatter on average by about 2 points), because the flagged ZIP codes are mostly cheap, outer ones."

- *Rests on:* largest change +5.83, mean +2.25; flagged ZIPs median Dec 2019 value $213k vs $269k, and median distance 39 mi vs 17 mi. *Type:* numbers **Description**; "because" is an **Inference** well supported by the medians. Fine; "consistent with" is the safer verb.

**34.** "Phoenix is the case that matters: with the flagged ZIP codes removed its level slope goes from -4.3% to +0.5% per 10 miles and all three growth slopes are near zero (+0.09, +0.03, -0.09), so its earlier results come from far-out ZIP codes."

- *Rests on:* extra check, Phoenix Dec 2019 level slope under exclusions: all ZIPs -4.3% [-7.1, -1.3] (147); dropping the 16 unreliable-WFH ZIPs +0.5% [-3.7, +4.8]; dropping the other three flags (1 ZIP each) changes nothing; dropping ZIPs beyond 60 miles (8) -1.8% [-6.1, +2.8]; beyond 40 miles (20) **+8.1%** [+1.4, +15.1]. Phoenix's flagged ZIPs (any flag) have a median distance of 51 miles and median value of $221k, against 17 miles and $297k for the rest; 16 of the 147 sample ZIPs have the work-from-home flag.
- *Type:* **Inference, well supported.** Only the work-from-home reliability flag matters. The text could say so, and note the sign flip inside 40 miles.

**35a.** "Atlanta's pattern survives and is stronger in 2020-22 (+1.25)."

- *Rests on:* flag-free +1.25 [+0.82, +1.68] vs all ZIPs +0.69 [+0.39, +0.99] (overlapping). *Type:* **Stronger than supported** ("stronger"). *Proposed:* "survives (+1.25 in 2020-22, against +0.69 with all ZIPs; the intervals overlap)."

**35b.** "Nashville's and Tampa's growth slopes hold up; Dallas turns clearly negative in 2023-25 (-0.35)."

- *Rests on:* Tampa +0.53 and -0.35 vs +0.57 and -0.32; Nashville +1.02, -0.37, +0.63 vs +1.02, -0.19, +0.72; Dallas flag-free -0.35 [-0.57, -0.12] vs all ZIPs -0.03 [-0.19, +0.13] (flag-free sample is 190 of 251 ZIPs).
- *Type:* Nashville and Tampa **Description**. "Clearly" in the Dallas clause is **stronger than supported**: it is a selected subsample. *Proposed:* "Dallas's 2023-25 slope is -0.35 (interval -0.57 to -0.12) when flagged ZIPs are dropped, against -0.03 with all ZIPs, so the Dallas result depends on the sample."

**36.** "On the 478 ZIP codes with rents at both ends, price growth rose with distance in 2020-22 (+0.83 points per year per 10 miles) and rents did too (+0.41). In 2023-25 price growth no longer rose with distance (-0.07) while rent growth still did (+0.33)."

- *Rests on:* +0.83 [+0.60, +1.05]; +0.41 [+0.25, +0.57]; -0.07 [-0.25, +0.12]; +0.33 [+0.19, +0.47]. Same 478 ZIPs in both. *Type:* **Description.**

**37.** "That is the pattern the plan said would point toward interest rates rather than location preferences, but it is a pattern, not proof: the sample is selective, ZORI is smoothed, and the comparison uses the same simple distance fits as above."

- *Rests on:* claim 36. The plan says only that rents "do not depend directly on mortgage financing, so comparing rent trends against price trends is a useful check"; it does not name this pattern.
- *Type:* **Stronger than supported** in attributing the pattern to the plan, and in leaving out the obvious alternative: ZORI is smoothed and lags prices, so rents may simply still be adjusting to the 2020-22 shift.
- *Proposed wording:* "This is the kind of contrast the rent check was designed to look for, since rents do not depend directly on mortgage financing. It is not proof: rents are smoothed and lag prices, so they may still be adjusting to the 2020-22 shift, the sample is selective, and the comparison uses the same simple distance fits as above."

# Part E. Repeats outside 2.2 to 2.6 (Summary and Section 3)

**38.** Summary: "Pre-pandemic work-from-home share tracks income so closely, and expensive ZIP codes were already growing slowest before 2020, that the later relationship with growth cannot be read as an exposure effect." Same issues as claims 12, 13a, 14 ("so closely", "slowest", "cannot be read"). Weaker: "overlaps strongly with income, expensive ZIP codes tended to grow more slowly before 2020, and the later relationship largely disappears once pre-2020 growth is controlled".

**39.** Summary: "Expensive ZIP codes form wedges, not rings, and a single distance-to-downtown variable fits poorly." Claim 8 and 9: wedges in 5 of 8 metros, and "fits poorly" holds for Phoenix and Dallas but not Charlotte (R-squared about 0.5), Austin or Nashville.

**40.** Summary and Section 3: "four metros show none" / "Phoenix, Charlotte, Dallas and Las Vegas show nothing". **Inconsistent with Section 2.2**, which says "Phoenix goes the other way" (growth slope +0.46 to -0.30). Weaker and consistent: "no flattening (Phoenix's gradient even steepens, but only because of far-out ZIPs)".

**41.** Section 3: "Sub-question 3's groups are only moderately distinct and track metro and housing type more than distance." Claims 19 to 22: "weakly separated", and housing type only for Group 4.

**42.** Section 3: "the two-center metros have centers at different price levels" is wrong for Tampa-St. Petersburg (claim 29).

# What I computed for this audit

All new numbers come from `src/audit_checks.py` (run `.venv/bin/python src/audit_checks.py`), with tables in `outputs/tables/audit_*.csv`: directional test of the top fifth (`audit_wedge`), inner vs outer growth (`audit_inner_outer_growth`), band medians with bootstrap intervals (`audit_band_bootstrap`), quadratic terms and LOWESS peaks (`audit_hump`), exposure with controls (`audit_exposure_controls`). The cluster stability numbers, Phoenix exclusion results, and core price medians are printed by the script and are quoted above. Nothing in the report was recomputed from these; they are checks on the wording.

The notebook has a few extra map sentences of the same kind that are not in the PDF (Tampa's northern fringe and southwest coast; Las Vegas readability). They have not been checked with numbers.
