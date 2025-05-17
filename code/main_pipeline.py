"""
One-stop driver:  python -m code.main_pipeline
It:
1. Crawls demographics  (§3.1)
2. Loads GDP & Population CSVs (§3.2)
3. Cleans each dataset  (§4)
4. Engineers features & X.npy (§5)
Outputs mandated CSVs/PDF (PDF left as TODO).
"""

import logging, argparse, pandas as pd
from pathlib import Path
import cleaning, feature_engineering as fe
from logging_conf import configure_logging
from crawl_demographics import crawl_demographics
from io_load import load_gdp, load_pop
from utils import *
from paths import (GDP_PER_CAPITA_2021, POPULATION_2021,
                   DEMOGRAPHICS_RAW_CSV)

configure_logging()
log = logging.getLogger("pipeline")

def run(gdp_csv: Path, pop_csv: Path, force_crawl=False):
    # 1  Crawl (or read existing)
    demo = crawl_demographics() if force_crawl or not DEMOGRAPHICS_RAW_CSV.exists() \
        else pd.read_csv(DEMOGRAPHICS_RAW_CSV)

    # 2  Load given CSVs
    gdp = load_gdp(gdp_csv)
    pop = load_pop(pop_csv)

    # 3  Clean
    demo_clean = cleaning.clean_demographics(demo)
    gdp_clean  = cleaning.clean_gdp(gdp)
    pop_clean  = cleaning.clean_population(pop)

    # 4  Feature engineering
    X, merged = fe.build_features(demo_clean, gdp_clean, pop_clean)

    log_metadata("Table after feature engineering", df=merged)

    log.info("Pipeline completed")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gdp_csv", required=False, default=GDP_PER_CAPITA_2021,
                    help=f"Path to {GDP_PER_CAPITA_2021.name}")
    ap.add_argument("--pop_csv", required=False, default=POPULATION_2021,
                    help=f"Path to {POPULATION_2021.name}")
    ap.add_argument("--force-crawl", action="store_true",
                    help=f"Ignore cached demographics_data.csv")
    run(**vars(ap.parse_args()))
