"""
Centralized relative-path definitions.
Change ROOT to move the whole project elsewhere.
"""
from pathlib import Path

ROOT      = Path(__file__).resolve().parent.parent
CODE_DIR  = ROOT / "code"
OUT_DIR   = ROOT / "output"
INPUT_DIR = ROOT / "input"

# single source of truth for all mandated output files -----------------------
DEMOGRAPHICS_RAW_CSV          = OUT_DIR / "demographics_data.csv"
DEMOGRAPHICS_BEFORE_SORT_CSV  = OUT_DIR / "demographics_before_sort.csv"
DEMOGRAPHICS_AFTER_SORT_CSV   = OUT_DIR / "demographics_after_sort.csv"
GDP_BEFORE_SORT_CSV           = OUT_DIR / "gdp_before_sort.csv"
GDP_AFTER_SORT_CSV            = OUT_DIR / "gdp_after_sort.csv"
POP_BEFORE_SORT_CSV           = OUT_DIR / "pop_before_sort.csv"
POP_AFTER_SORT_CSV            = OUT_DIR / "pop_after_sort.csv"
GDP_DESCRIBE_CSV              = OUT_DIR / "gdp_describe.csv"
POP_DESCRIBE_CSV              = OUT_DIR / "pop_describe.csv"
NAME_MISMATCHES_CSV           = OUT_DIR / "name_mismatches.csv"
DROPPED_GDP_CSV               = OUT_DIR / "dropped_gdp.csv"
LOST_COUNTRIES_CSV            = OUT_DIR / "lost_countries.csv"
CLEANING_PDF                  = OUT_DIR / "cleaning_summary.pdf"
X_NPY                          = OUT_DIR / "X.npy"
# source for input files: change to relevant paths
GDP_PER_CAPITA_2021            = INPUT_DIR / "gdp_per_capita_2021.csv"
POPULATION_2021                = INPUT_DIR / "population_2021.csv"

# ---------------------------------------------------------------------------
for p in (OUT_DIR,):
    p.mkdir(parents=True, exist_ok=True)
