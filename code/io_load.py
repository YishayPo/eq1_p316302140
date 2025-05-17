"""
Utility loaders for the provided 2021 GDP & Population CSVs (3.2)
Also saves "before/after sort" previews + describe tables.
"""

import logging, pandas as pd
from pathlib import Path
from paths import (GDP_PER_CAPITA_2021, POPULATION_2021,
    GDP_BEFORE_SORT_CSV, GDP_AFTER_SORT_CSV, POP_BEFORE_SORT_CSV,
    POP_AFTER_SORT_CSV, GDP_DESCRIBE_CSV, POP_DESCRIBE_CSV)
from utils import *
from logging_conf import configure_logging

configure_logging()
log = logging.getLogger("io")

def _verify_columns(df: pd.DataFrame, wanted: list[str], file: Path):
    missing = [c for c in wanted if c not in df.columns]
    if missing:
        raise ValueError(f"{file.name}: missing columns {missing}")

def load_gdp(path: Path) -> pd.DataFrame:
    df = load_df(path=path)
    _verify_columns(df, ["Country", "GDP_per_capita_PPP"], path)
    # added astype(str) because I heard some students had to, it worked for me without it either
    df["GDP_per_capita_PPP"] = pd.to_numeric(df["GDP_per_capita_PPP"].astype(str).str.replace(",", ""), errors="coerce")
    store_head(df, head=5, path=GDP_BEFORE_SORT_CSV)
    store_head(df, head=5, path=GDP_AFTER_SORT_CSV, sorted="Country")
    df.describe().to_csv(GDP_DESCRIBE_CSV)
    return df

def load_pop(path: Path) -> pd.DataFrame:
    log.debug(f'Reading {path.name} file')
    df = pd.read_csv(path, na_values=["None"])
    _verify_columns(df, ["Country", "Population"], path)
    # added astype(str) because I heard some students had to, it worked for me without it either
    df["Population"] = pd.to_numeric(df["Population"].astype(str).str.replace(",",""), errors="coerce")
    store_head(df, head=5, path=POP_BEFORE_SORT_CSV)
    store_head(df, head=5, path=POP_AFTER_SORT_CSV, sorted="Country")
    df.describe().to_csv(POP_DESCRIBE_CSV)
    return df


if __name__ == "__main__":
    gdp_df = load_gdp(GDP_PER_CAPITA_2021)
    log_metadata(name='GDP', df=gdp_df)

    pop_df = load_pop(POPULATION_2021)
    log_metadata(name='Population', df=pop_df)