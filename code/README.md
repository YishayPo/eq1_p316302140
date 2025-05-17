
# Exercise #1 – Data Science Pipeline

**Course:** 67978 · *A Needle in a Data Haystack*

## **Practical Part Repo**

---

## Directory Layout

```text
.
├── code/                           # all Python modules (crawler, cleaning, etc.)
│   ├── crawl_demographics.py       # crawl the data and creates demographics csv files
│   ├── io_load.py                  # loads gdp and pop datasets
│   ├── cleaning.py                 # cleans the data
│   ├── feature_engineering.py      # add the required features
│   ├── main_pipeline.py            # runs the main pipeline from crawl to final merged dataset
│   ├── logging_conf.py             # helper for configuring logger
│   ├── paths.py                    # header-like file with constant paths to files
│   └── utils.py                    # helper I/O utilities (CSV to DataFrame, etc.)
├── input/                          # **raw** input CSVs supplied by course staff
│   ├── gdp_per_capita_2021.csv
│   └── population_2021.csv
├── output/                         # *all* generated artefacts land here
│   ├── demographics_data.csv
│   ├── *_before_sort.csv
│   ├── *_after_sort.csv
│   ├── *_describe.csv
│   ├── name_mismatches.csv
│   ├── dropped_gdp.csv
│   ├── lost_countries.csv
│   ├── cleaning_summary.pdf
│   └── X.npy
└── README.md

```

# Quick Start

# 1 – (optional) activate venv

python -m venv .venv && source .venv/bin/activate

# 2 – install deps

pip install -r requirements.txt

# 3 – run the complete pipeline

```
python -m code.main_pipeline \
       --gdp_csv input/gdp_per_capita_2021.csv \
       --pop_csv input/population_2021.csv \
       --force-crawl
```

Default is to load the data and not crawl every time it runs <br>

## Running Individual Steps

Each file can run on it own except for the feature_engineering which depends on cleaning.

* ```python -m code.crawl_demographics``` (--reload to reload data instead of crawl, run with help to see other options)
* ```python -m code.io_load```
* ```python -m code.feature_engineering```

# What happens:

Crawler (crawl_demographics.py) scans Worldometer and builds
output/demographics_data.csv + two 10-row preview CSVs.

Loader (io_load.py) ingests the supplied GDP & Population CSVs,

writing:
before / after sort previews

describe() tables

Cleaner (cleaning.py) fixes types, names, duplicates, Tukey outliers.

Feature Engineering (feature_engineering.py)

TotalGDP, log-transforms, z-score scaling

inner-joins on Country

saves final matrix X.npy ( *N × 3 *) + lost_countries.csv.