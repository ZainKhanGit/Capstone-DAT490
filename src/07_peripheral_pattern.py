"""Step 7: one consolidated finding: data-quality problems concentrate at the periphery.

Pulls the per-ZIP flags from steps 1-5 into one table and tests, for each flag, whether flagged ZIPs sit
farther from the metro center than unflagged ones. Distance is compared pooled (miles) and as a
within-metro percentile (0 = at the center, 1 = farthest ZIP in that metro), so metros with different
footprints do not drive the pooled result.

Outputs
  data/clean/zip_flags.csv                  one row per ZIP, all data-quality flags
  outputs/logs/peripheral_gap_pattern.md    the write-up
"""
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

from config import CLEAN, LOGS

FLAGS = {
    "zhvi_incomplete": ("ZHVI series incomplete 2018-2025 (step 1)", "zhvi_incomplete"),
    "zhvi_late_entry": ("  of which: begins after Jan 2018", "zhvi_late_entry"),
    "metro_col_only": ("Metro column assigns ZIP, county crosswalk does not (step 2)", "metro_col_only"),
    "acs_baseline_missing": ("No 2015-2019 ACS ZCTA row (step 4)", "acs_baseline_missing"),
    "wfh_unreliable": ("2015-2019 WFH share unreliable, MOE/estimate > 0.5 (step 4)", "wfh_unreliable"),
    "zori_missing": ("No ZORI at all, 2018-2025 (step 5)", "zori_missing"),
    "zori_incomplete": ("ZORI present but not for every month 2018-2025 (step 5)", "zori_incomplete"),
}


def main() -> None:
    d = pd.read_csv(CLEAN / "zip_distance.csv", dtype={"zip": str})
    acs = pd.read_csv(CLEAN / "zip_acs.csv", dtype={"zip": str})
    zm = pd.read_csv(CLEAN / "zori_zip_meta.csv", dtype={"zip": str})
    zh = pd.read_csv(CLEAN / "zhvi_zip_meta.csv", dtype={"zip": str})

    f = d[["zip", "metro_short", "city", "dist_cityhall_mi", "dist_nearest_mi", "dist_band"]].copy()
    f = f.merge(zh[["zip", "complete_window", "late_entry", "xwalk_status"]], on="zip")
    f["zhvi_incomplete"] = ~f["complete_window"]
    f["zhvi_late_entry"] = f["late_entry"]
    f["metro_col_only"] = f["xwalk_status"].eq("metro_col_only")
    a = acs[["zip", "in_acs_2019", "wfh_unreliable_2019"]]
    f = f.merge(a, on="zip", how="left")
    f["acs_baseline_missing"] = ~f["in_acs_2019"].astype(bool)
    f["wfh_unreliable"] = f["wfh_unreliable_2019"].fillna(False).astype(bool)
    f = f.merge(zm[["zip", "has_any_zori", "complete_window"]].rename(
        columns={"complete_window": "zori_complete"}), on="zip", how="left")
    f["zori_missing"] = ~f["has_any_zori"]
    f["zori_incomplete"] = f["has_any_zori"] & ~f["zori_complete"]

    # within-metro distance percentile
    f["dist_pct_in_metro"] = f.groupby("metro_short")["dist_cityhall_mi"].rank(pct=True)
    f["n_core_flags"] = f[["zhvi_incomplete", "metro_col_only", "acs_baseline_missing"]].sum(axis=1)
    keep = ["zip", "metro_short", "city", "dist_cityhall_mi", "dist_nearest_mi", "dist_pct_in_metro",
            "dist_band"] + list(FLAGS) + ["n_core_flags"]
    f[keep].to_csv(CLEAN / "zip_flags.csv", index=False)

    rows = []
    for col, (label, _) in FLAGS.items():
        x, y = f.loc[f[col], "dist_cityhall_mi"], f.loc[~f[col], "dist_cityhall_mi"]
        px, py = f.loc[f[col], "dist_pct_in_metro"], f.loc[~f[col], "dist_pct_in_metro"]
        p = mannwhitneyu(px, py, alternative="greater").pvalue if len(x) and len(y) else np.nan
        rows.append((label, int(f[col].sum()), x.median(), y.median(), px.median(), py.median(),
                     100 * (x >= 30).mean() if len(x) else np.nan, p))
    t = pd.DataFrame(rows, columns=["flag", "zips", "median_mi_flagged", "median_mi_rest",
                                    "median_pctile_flagged", "median_pctile_rest",
                                    "pct_flagged_at_30plus_mi", "p_one_sided"]).set_index("flag")
    pct30 = 100 * (f["dist_cityhall_mi"] >= 30).mean()

    L = ["# One pattern across the pipeline: data problems sit at the periphery\n",
         "Most of the data-quality checks so far point the same way: the ZIPs we lose, flag or cannot "
         "match tend to be the ones farthest from the metro center. This section collects them in one "
         "table and also records the two flags that do not follow the pattern.\n",
         "\nFor each flag: how many ZIPs, the median distance (city-hall definition, miles) of flagged vs. "
         "unflagged ZIPs, the same comparison as a within-metro percentile "
         "(0 = at the center, 1 = farthest ZIP in that metro; removes differences in metro size), the "
         f"share of flagged ZIPs that are 30+ miles out (all ZIPs: {pct30:.0f}%), and a one-sided "
         "Mann-Whitney p-value for 'flagged ZIPs have higher within-metro percentile'.\n\n",
         t.round({"median_mi_flagged": 1, "median_mi_rest": 1, "median_pctile_flagged": 2,
                  "median_pctile_rest": 2, "pct_flagged_at_30plus_mi": 0, "p_one_sided": 4})
         .to_markdown() + "\n"]

    L.append("\n## Burden by distance band\n\nShare of ZIPs in each band carrying each flag (%).\n\n")
    show = ["zhvi_incomplete", "metro_col_only", "acs_baseline_missing", "wfh_unreliable",
            "zori_missing", "zori_incomplete"]
    b = (f.groupby("dist_band", observed=True)[show].mean() * 100).round(0)
    b.insert(0, "zips", f.groupby("dist_band", observed=True).size())
    L.append(b.to_markdown() + "\n")

    L.append("\n## Same view by metro (median within-metro percentile of flagged ZIPs)\n\n")
    rows = []
    for k, g in f.groupby("metro_short"):
        rows.append([k] + [g.loc[g[c], "dist_pct_in_metro"].median() if g[c].any() else np.nan
                           for c in show])
    L.append(pd.DataFrame(rows, columns=["metro"] + show).set_index("metro").round(2)
             .to_markdown() + "\n\n(NaN = no ZIPs with that flag in the metro. A value above 0.5 means the "
             "flagged ZIPs are in the outer half of that metro.)\n")

    L.append("\n## Exceptions\n\n"
             "- **No 2015-2019 ACS row (7 ZIPs): not peripheral.** Their within-metro percentile is "
             f"{t.iloc[3]['median_pctile_flagged']:.2f} vs {t.iloc[3]['median_pctile_rest']:.2f} for the rest "
             f"(p = {t.iloc[3]['p_one_sided']:.2f}) and only 1 of the 7 is 30+ miles out. These are "
             "fast-growing suburban ZIPs (Frisco, McKinney, Arlington, Surprise, Las Vegas) that appear to post-date "
             "the 2010 ZCTA vintage, i.e. a growth-related gap rather than a distance-related one. "
             "With 7 ZIPs the test has little power, so this says 'no evidence of a peripheral pattern', "
             "not 'no pattern'.\n"
             "- **ZORI incomplete (present but patchy): not peripheral.** Outer ZIPs mostly have no ZORI at "
             "all, so the ones with partial series are inner and middle ZIPs that entered the rent index "
             "late. The right reading is that ZORI is missing at the periphery and growing in the interior "
             "over time.\n")

    anyc = f["n_core_flags"] > 0
    L.append(f"\n## What it means for the analysis\n\n"
             f"- {int(anyc.sum())} ZIPs ({100 * anyc.mean():.1f}%) carry at least one of the three hard "
             "problems (incomplete ZHVI, Metro/crosswalk disagreement, missing 2015-2019 ACS row); "
             "the first two are strongly peripheral, the third is not, so this pooled figure mixes the two; their "
             f"median distance is {f.loc[anyc, 'dist_cityhall_mi'].median():.1f} mi versus "
             f"{f.loc[~anyc, 'dist_cityhall_mi'].median():.1f} mi for the rest.\n"
             "- Dropping any of these ZIPs trims the outer edge of each metro, which is where the "
             "price-distance gradient is estimated. A gradient fitted on 'clean' ZIPs only describes the "
             "inner metro and can be steeper or flatter than the full-metro gradient.\n"
             "- ZORI coverage is the strongest case (see table): rent-based checks will be representative of "
             "the urban core and inner suburbs, not the outer ring, and the ZORI sample also grows over time, "
             "so rent trends must be computed on a fixed set of ZIPs.\n"
             "- The unreliable-WFH flag is not missingness but noise: the 2015-2019 exposure measure is least "
             "precise in exactly the outer ZIPs. SQ2 plots should show these separately or weight by "
             "precision.\n"
             "- Practical rule for the EDA: keep every ZIP by default, carry the flags in the data, and show "
             "results for the full sample and for the flag-free sample side by side.\n")

    (LOGS / "peripheral_gap_pattern.md").write_text("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
