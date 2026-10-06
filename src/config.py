"""Shared paths and project constants."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CLEAN = ROOT / "data" / "clean"
LOGS = ROOT / "outputs" / "logs"

# Census API key is read from the environment; never hard-code it.
#   export CENSUS_API_KEY="..."
CENSUS_API_KEY = os.environ.get("CENSUS_API_KEY")

# Metro labels exactly as they appear in the ZHVI `Metro` column.
METROS = {
    "Phoenix": "Phoenix-Mesa-Chandler, AZ",
    "Austin": "Austin-Round Rock-Georgetown, TX",
    "Atlanta": "Atlanta-Sandy Springs-Alpharetta, GA",
    "Dallas": "Dallas-Fort Worth-Arlington, TX",
    "Tampa": "Tampa-St. Petersburg-Clearwater, FL",
    "Charlotte": "Charlotte-Concord-Gastonia, NC-SC",
    "Nashville": "Nashville-Davidson--Murfreesboro--Franklin, TN",
    "Las Vegas": "Las Vegas-Henderson-Paradise, NV",
}

# Analysis window and periods (applied at analysis time; the panel keeps all months).
WINDOW = ("2018-01-31", "2025-12-31")
BASE_MONTH = "2019-12-31"
PERIODS = {"pre-2020": (2018, 2019), "2020-2022": (2020, 2022), "2023-2025": (2023, 2025)}
