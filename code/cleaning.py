"""
Rigorous cleaning steps (Q4) for demographics, GDP, population.
Outputs name_mismatches.csv, dropped_gdp.csv, etc.
"""

from __future__ import annotations
import re, logging, pandas as pd, numpy as np
from utils import *
from paths import (NAME_MISMATCHES_CSV, DROPPED_GDP_CSV,
                    DEMOGRAPHICS_RAW_CSV,
                    GDP_PER_CAPITA_2021, POPULATION_2021)
from logging_conf import configure_logging

configure_logging()
log = logging.getLogger("clean")

# --------------------------------------------------------------------------- #
#  Common helpers
# --------------------------------------------------------------------------- #

def _standardize_country(col: pd.Series, store_mismatches=False) -> tuple[pd.Series, pd.DataFrame]:
    orig = col.copy()
    new  = (orig.str.strip()
                .str.replace(r"^the\s+", "", regex=True, flags=re.IGNORECASE)
                .str.title())
    mism = pd.DataFrame({"Original": orig, "Standardized": new})
    mism = mism[mism["Original"] != mism["Standardized"]]
    if not mism.empty and store_mismatches:
        mism.to_csv(NAME_MISMATCHES_CSV, index=False)
        log.info("Saved %s with %d corrected names", NAME_MISMATCHES_CSV.name, len(mism))
    return new, mism

def _tukey_outliers(s: pd.Series) -> pd.Series:
    q1, q3 = s.quantile([0.25, 0.75])
    iqr    = q3 - q1
    lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
    return (s < lower) | (s > upper)

# --------------------------------------------------------------------------- #
#  Dataset-specific cleaners
# --------------------------------------------------------------------------- #

def clean_demographics(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Cleaning demographics dataset...")

    numeric_cols = [c for c in df.columns if c != "Country"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")

    # Log non-numeric conversion issues
    non_numeric_counts = df[numeric_cols].isna().sum()
    for col, cnt in non_numeric_counts.items():
        if cnt > 0:
            log.info("Non-numeric values in %s: %d", col, cnt)

    df["Country"], mismatches = _standardize_country(df["Country"], store_mismatches=True)
    if not mismatches.empty:
        log.info("Country name mismatches corrected: %d", len(mismatches))


    before = len(df)
    df = df[df["LifeExpectancy_Both"].between(40, 100)]
    after = len(df)
    log.info("Dropped %d rows with invalid LifeExpectancy (kept %d of %d)", before-after, after, before)

    df = df.set_index("Country", drop=True)
    return df


def clean_gdp(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Cleaning GDP dataset...")

    df["Country"], mismatches = _standardize_country(df["Country"])
    if not mismatches.empty:
        log.info("Country name mismatches corrected in GDP: %d", len(mismatches))

    total_before = len(df)
    missing = df["GDP_per_capita_PPP"].isna().sum()
    log.info("Missing GDP per capita entries: %d", missing)
    mask_missing = df["GDP_per_capita_PPP"].isna()
    df.loc[mask_missing].to_csv(DROPPED_GDP_CSV, index=False)
    df = df[~mask_missing]

    outliers = _tukey_outliers(df["GDP_per_capita_PPP"])
    log.info("GDP outliers detected (Tukey): %d (not dropped)", outliers.sum())

    df = df.drop_duplicates(subset="Country")
    total_after = len(df)
    log.info("Dropped %d duplicate rows based on country (final count: %d)", total_before - total_after - missing, total_after)

    df = df.set_index("Country")
    return df


def clean_population(df: pd.DataFrame) -> pd.DataFrame:
    log.info("Cleaning population dataset...")

    df["Country"], mismatches = _standardize_country(df["Country"])
    if not mismatches.empty:
        log.info("Country name mismatches corrected in population: %d", len(mismatches))

    total_before = len(df)
    missing_pop = df["Population"].isna().sum()
    log.info("Missing population values: %d", missing_pop)
    df = df[~df["Population"].isna()]

    df["LogPop"] = np.log10(df["Population"])
    out = _tukey_outliers(df["LogPop"])
    log.info("Population outliers detected: %d (not dropped)", out.sum())

    df = df.drop(columns="LogPop").drop_duplicates(subset="Country")
    total_after = len(df)
    log.info("Dropped %d duplicate countries (final count: %d)", total_before - total_after - missing_pop, total_after)

    df = df.set_index("Country")
    return df


if __name__ == "__main__":
    demographics_df = load_df(DEMOGRAPHICS_RAW_CSV)
    clean_demographics(demographics_df)

    gdp_df = load_df(GDP_PER_CAPITA_2021)
    clean_gdp(gdp_df)

    pop_df = load_df(POPULATION_2021)
    clean_population(pop_df)