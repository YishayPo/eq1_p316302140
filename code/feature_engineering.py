"""
Creates TotalGDP, log transforms, z-score scaling, join & X.npy Q5
"""

import logging, numpy as np, pandas as pd
from sklearn.preprocessing import StandardScaler
from paths import (X_NPY, LOST_COUNTRIES_CSV,
                    DEMOGRAPHICS_RAW_CSV,
                    GDP_PER_CAPITA_2021, POPULATION_2021)
from utils import *
from logging_conf import configure_logging

configure_logging()
log = logging.getLogger("features")

SELECTED = ["LifeExpectancy_Both", "LogGDPperCapita", "LogPopulation"]

def build_features(demo: pd.DataFrame, gdp: pd.DataFrame,
                    pop: pd.DataFrame) -> np.ndarray:
    # check country is set as index for all dfs
    for df in [demo, gdp, pop]:
        if df.index.name != "Country":
            raise ValueError("Expected 'Country' as index in all DataFrames")
    # 5.1 Total GDP ----------------------------------------------------------
    if pop["Population"].max() < 1e3:
        raise ValueError("Population values appear to be in millions, expected absolute numbers")
    gdp["TotalGDP"] = gdp["GDP_per_capita_PPP"] * pop["Population"]

    # 5.2 log10 transforms ---------------------------------------------------
    if (gdp["GDP_per_capita_PPP"] <= 0).any():
        raise ValueError("GDP per capita contains non-positive values")
    if (pop["Population"] <= 0).any():
        raise ValueError("Population contains non-positive values")
    gdp["LogGDPperCapita"] = np.log10(gdp["GDP_per_capita_PPP"])
    pop["LogPopulation"]   = np.log10(pop["Population"])

    # 5.4 inner join ---------------------------------------------------------
    df = demo.join(gdp, how="inner").join(pop, how="inner")
    lost = (set(demo.index) | set(gdp.index) | set(pop.index)) - set(df.index)
    pd.Series(sorted(lost)).to_csv(LOST_COUNTRIES_CSV, index=False, header=["Country"])
    log.info("Inner join retained %d countries, lost %d", len(df), len(lost))

    # 5.2 handle missing after join -----------------------------------------
    num_cols = df.select_dtypes("number").columns
    df[num_cols] = df[num_cols].astype("float64")  # to accept mean value which is float64
    df[num_cols] = df[num_cols].fillna(df[num_cols].mean())

    # 5.3 scaling ------------------------------------------------------------
    scaler = StandardScaler()
    df = df.sort_index()  # make sure X.npy remains the same throughout different runs
    X = scaler.fit_transform(df[SELECTED])
    np.save(X_NPY, X)
    log.info("Saved feature matrix to %s shape=%s", X_NPY.name, X.shape)
    return X, df


if __name__ == "__main__":
    demographics_df = load_df(DEMOGRAPHICS_RAW_CSV)
    gdp_df = load_df(GDP_PER_CAPITA_2021)
    pop_df = load_df(POPULATION_2021)

    X, merged = build_features(demo=demographics_df, gdp=gdp_df, pop=pop_df)
