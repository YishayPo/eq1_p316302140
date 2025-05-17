"""
provides util functions to handle stat logs, loading dataframes and such.
"""
from __future__ import annotations
import pandas as pd
import logging
from pathlib import Path
from logging_conf import configure_logging

configure_logging()
log = logging.getLogger("utils")


def load_df(path: Path) -> pd.DataFrame:
    log.debug(f'Reading {path.name} file')
    df = pd.read_csv(path, na_values=["None"])
    return df

def log_metadata(name: str, df: pd.DataFrame) -> None:
    log.info(f"{name} columns: {df.columns.tolist()}")
    log.info(f"{name} shape  : {df.shape}")


def store_head(df: pd.DataFrame, head: int, path: Path, sorted: str|None = None) -> None:
    if sorted:
        df = df.sort_values(sorted)
    df.head(head).to_csv(path, index=False)
    log.info(f"Saved {head} first rows {'sorted' if sorted else ''} to {path.name}")


def stats_for_numeric_fields(df: pd.DataFrame, ignore_cols: list[str]) -> pd.DataFrame:
    ### Convert all numeric fields to float for analysis
    numeric_cols = [col for col in df.columns if col not in ignore_cols]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    ### Compute and log required stats
    stats = df[numeric_cols].agg(['mean', 'std', 'min', 'max', 'median']).transpose()
    stats["missing"] = df[numeric_cols].isna().sum()

    return stats

def pearson_correlation(df: pd.DataFrame, colA_name: str, colB_name: str) -> pd.DataFrame:
    ### Pearson correlation
    if df[colA_name].notna().any() and df[colB_name].notna().any():
        corr = df[colA_name].corr(df[colB_name])
        return corr
    else:
        log.warning("Could not compute correlation: one or both columns contain only NaNs")
        return pd.DataFrame()