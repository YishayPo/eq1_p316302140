"""
Scrapes https://www.worldometers.info/demographics/ per spec 3.1
Produces `demographics_data.csv` and two 10-row preview CSVs.
Logs stats and Pearson correlation for the crawled data.
"""

from __future__ import annotations
import re, time, logging, requests
from bs4 import Tag, BeautifulSoup as BS
import pandas as pd
from pathlib import Path
from paths import (DEMOGRAPHICS_RAW_CSV,
                    DEMOGRAPHICS_BEFORE_SORT_CSV,
                    DEMOGRAPHICS_AFTER_SORT_CSV)
from utils import *
from logging_conf import configure_logging

configure_logging()
log = logging.getLogger("crawler")

BASE = "https://www.worldometers.info"


def _get(url: str, sleep=0.8, **kwargs) -> BS:
    """HTTP GET with polite delay; returns BeautifulSoup tree."""
    log.debug("GET %s", url)
    time.sleep(sleep)
    r = requests.get(url, timeout=15, **kwargs)
    r.raise_for_status()
    return BS(r.text, "html.parser")


def _extract_country_links(soup: BS) -> dict[str, str]:
    """
    Return {country: absolute_href} for every anchor that appears in the
    section headed 'Demographics of Countries'.
    Works with the new UL/LI markup Worldometer introduced (May 2025).
    """
    # locate the <h2>
    heading = soup.find(
        lambda tag: tag.name in ("h2", "h3")
        and "Demographics of Countries" in tag.get_text(strip=True)
    )
    if heading is None:
        raise RuntimeError("Could not find the 'Demographics of Countries' heading")

    # walk sibling nodes until next heading, grab every <a>
    links: dict[str, str] = {}
    for sib in heading.next_siblings:
        if isinstance(sib, Tag) and sib.name in ("h1", "h2", "h3"):   # stop at next section
            break
        for a in (sib.find_all("a", href=True) if isinstance(sib, Tag) else []):  # safe call
            href = a["href"].strip()
            text = a.get_text(strip=True)
            # only country pages:  /demographics/<something>-demographics/
            if "/demographics/" in href and href.endswith("-demographics/"):
                links[text] = href if href.startswith("http") else BASE + href

    if not links:
        raise RuntimeError("No country links detected - page structure may have changed")

    log.info("Found %d country pages", len(links))
    return links


FLAGS = re.I | re.S      # ignore-case + let “.” cross new-lines

FIELD_PATTERNS = {
    "LifeExpectancy_Both":
        re.compile(r"Life\s*Expectancy.*?Both\s*Sexes.*?(\d+(?:\.\d+)?)", FLAGS),
    "LifeExpectancy_Female":
        re.compile(r"Life\s*Expectancy.*?Females?.*?(\d+(?:\.\d+)?)", FLAGS),
    "LifeExpectancy_Male":
        re.compile(r"Life\s*Expectancy.*?Males?.*?(\d+(?:\.\d+)?)", FLAGS),

    "UrbanPopulation_Percentage":
        re.compile(r"Urban\s+Population.*?(\d+(?:\.\d+)?)\s*%", FLAGS),
    "UrbanPopulation_Absolute":
        re.compile(r"Urban\s+Population.*?\(([\d,]+)\s*people", FLAGS),

    "PopulationDensity":
        re.compile(r"Population\s+Density.*?is\s*([\d\.]+)\s*people", FLAGS),
}


def _parse_country_page(html: str) -> dict[str, str | None]:
    """
    Extract the six required numbers from raw HTML **robustly**:
    * join all visible text with spaces so regex can span tags/line-breaks
    * apply the updated FIELD_PATTERNS above
    """
    text = BS(html, "html.parser").get_text(" ", strip=True)
    out  = {k: None for k in FIELD_PATTERNS}
    for k, patt in FIELD_PATTERNS.items():
        m = patt.search(text)
        if m:
            out[k] = m.group(1).replace(",", "")
    return out


def crawl_demographics() -> pd.DataFrame:
    home = _get(f"{BASE}/demographics/")
    countries = _extract_country_links(home)
    records = []
    for c, href in countries.items():
        try:
            page = _get(href, sleep=0.3)
            rec = _parse_country_page(page.text)
            rec["Country"] = c
            records.append(rec)
        except Exception as e:
            log.warning("Failed %s : %s", c, e)
    df = pd.DataFrame.from_records(records).astype("string")
    df.to_csv(DEMOGRAPHICS_RAW_CSV, index=False)
    log.info("Saved %s", DEMOGRAPHICS_RAW_CSV.name)

    # 10-row previews
    store_head(df, head=10, path=DEMOGRAPHICS_BEFORE_SORT_CSV)
    store_head(df, head=10, path=DEMOGRAPHICS_AFTER_SORT_CSV, sorted="Country")

    return df


def reload_crawled_data(path: Path) -> pd.DataFrame:
    log.debug(f'Reading already crawled data from {path.name} file')
    df = pd.read_csv(path, na_values=["None"])

    return df


def arg_parser():
    import argparse
    ap = argparse.ArgumentParser(
        description="Scrapes https://www.worldometers.info/demographics/ per spec §3.1"
                    "Produces `demographics_data.csv` and two 10-row preview CSVs."
                    "Logs stats and Pearson correlation for the crawled data.")
    ap.add_argument("--reload", action='store_true',
                    help="Shortens time by reloading already stored data from previous crawling: for stats and corr")
    ap.add_argument('--metadata', action='store_true',
                    help="Logs columns and shape of the demographics dataframe")
    ap.add_argument('--stats', action='store_true',
                    help="Produces stats mean, standard deviation, minimum, maximum, median, and count of missing values for numeric columns")
    ap.add_argument("--corr", action='store_true',
                    help="Logs Pearson Correlation between LifeExpectancy_Both and PopulationDensity")
    args = ap.parse_args()

    return args


if __name__ == "__main__":
    args = arg_parser()

    if args.reload:
        df = reload_crawled_data(DEMOGRAPHICS_RAW_CSV)
    else:
        df = crawl_demographics()

    if args.metadata:
        log_metadata(name='demographics', df=df)

    if args.stats:
        stats = stats_for_numeric_fields(df, ignore_cols=["Country"])
        stats.to_csv('stats.csv')
        log.info("Summary statistics per field:\n%s", stats)

    if args.corr:
        corr = pearson_correlation(df, colA_name="LifeExpectancy_Both", colB_name="PopulationDensity")
        log.info("Pearson correlation between LifeExpectancy_Both and PopulationDensity: %.4f", corr)
