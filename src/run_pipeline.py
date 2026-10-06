"""Run the whole data pipeline, or part of it, in order.

    python src/run_pipeline.py                 # all steps
    python src/run_pipeline.py --from 4        # steps 4 onward
    python src/run_pipeline.py --only 3 8      # just these steps
    python src/run_pipeline.py --list          # show the steps and what each needs

Each step is a standalone script that reads data/raw/ or data/clean/ and writes data/clean/ plus a
report in outputs/logs/. Steps never download anything except step 4, which calls the Census API
(needs CENSUS_API_KEY unless the responses are already cached in data/raw/acs/).

Raw inputs that must be placed by hand (see docs/SOURCES.md for where each comes from) are checked
before anything runs.
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
RAW = ROOT / "data" / "raw"

STEPS = {
    1: ("01_zhvi_panel.py", "ZHVI -> metro filter, ZIP-month panel, missingness"),
    2: ("02_metro_crosswalk_check.py", "Metro column vs county crosswalk"),
    3: ("03_distances.py", "ZCTA centroids, distance to city hall / nearest center"),
    4: ("04_acs.py", "ACS 2015-2019 and 2019-2023 at ZCTA level, match + reliability"),
    5: ("05_zori_panel.py", "ZORI panel and coverage"),
    6: ("06_boundaries.py", "ZCTA polygons for the ZHVI ZIPs"),
    7: ("07_peripheral_pattern.py", "consolidated data-quality flags"),
    8: ("08_growth.py", "YoY growth, Dec 2019 index, periods"),
}

# raw files that must exist before the pipeline can run (glob patterns inside data/raw/)
REQUIRED_RAW = {
    "ZHVI csv": "Zip_zhvi_*.csv",
    "ZORI csv": "Zip_zori_*.csv",
    "CBSA delineation": "cbsa_delineation_list1_2023.xlsx",
    "Gazetteer ZCTA": "2024_Gaz_zcta_national.txt",
    "ZCTA boundaries": "zcta_boundaries/cb_2020_us_zcta520_500k.shp",
}


def check_inputs(steps: list[int]) -> list[str]:
    problems = [f"missing raw input: {name} ({pat}) in {RAW}"
                for name, pat in REQUIRED_RAW.items() if not list(RAW.glob(pat))]
    if 4 in steps:
        cached = len(list((RAW / "acs").glob("acs5_*.csv"))) if (RAW / "acs").exists() else 0
        if cached < 10 and not os.environ.get("CENSUS_API_KEY"):
            problems.append("step 4 needs CENSUS_API_KEY (ACS responses are not all cached yet)")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="start", type=int, default=1)
    ap.add_argument("--only", type=int, nargs="+")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    if a.list:
        for n, (f, d) in STEPS.items():
            print(f"{n}  {f:<28} {d}")
        return 0

    steps = a.only if a.only else [n for n in STEPS if n >= a.start]
    unknown = [n for n in steps if n not in STEPS]
    if unknown:
        print(f"unknown step(s): {unknown}")
        return 2
    problems = check_inputs(steps)
    if problems:
        print("\n".join(problems))
        return 2

    for n in steps:
        script, desc = STEPS[n]
        print(f"\n=== step {n}: {desc} ({script}) ===", flush=True)
        t0 = time.time()
        r = subprocess.run([sys.executable, str(SRC / script)], cwd=SRC, stdout=subprocess.DEVNULL)
        if r.returncode != 0:
            print(f"step {n} FAILED (exit {r.returncode}); rerun it alone to see the traceback: "
                  f"python src/{script}")
            return r.returncode
        print(f"step {n} ok in {time.time() - t0:.0f}s; report in outputs/logs/", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
