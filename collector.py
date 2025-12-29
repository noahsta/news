import re
import os
import zipfile
import requests
from pathlib import Path
from urllib.request import urlretrieve
import pandas as pd

from data_selection import filter_rows, filter_rows_2
from visuals import plot_found_locations

def extract_filenames_from_file(html_filename):
    """
    Read an HTML file located in the same directory and extract all filenames
    appearing inside href="...".
    """
    path = Path(html_filename)

    with path.open("r", encoding="utf-8") as f:
        html_text = f.read()

    pattern = r'\.gkg\.csv\.zip'
    return re.findall(pattern, html_text)


def download_and_filter(filenames, base_url: str=None, include: str="spec"):
    """
    For each filename in the list:
    - download the .zip file
    - open and read the single CSV inside
    - apply columns_is_nice to keep useful columns
    - add a 'source_filename' column with the original filename
    - concatenate everything into one big DataFrame
    """
    dfs = []

    for name in filenames:
        if base_url is not None:
            url = f"{base_url}/{name}"
        else:
            url = name
        print(f"Downloading {url} ...")

        name = url[-29:]  # last 29 characters
        # Download ZIP to local disk
        try:
            urlretrieve(url, name)
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            continue

        print(f"Saved as {name}")

        try:
            # Read ZIP file
            with zipfile.ZipFile(name, "r") as z:
                csv_name = z.namelist()[0]  # single CSV inside

                with z.open(csv_name) as f:
                    df_raw = pd.read_csv(f, header=None, delimiter="\t", lineterminator="\n", on_bad_lines="warn")
            
            df_raw.columns = ["GlobalEventID", "Day", "MonthYear", "Year", "FractionDate", "Actor1Code", "Actor1Name",
                            "Actor1CountryCode", "Actor1KnownGroupCode", "Actor1EthnicCode", "Actor1Religion1Code",
                            "Actor1Religion2Code", "Actor1Type1Code", "Actor1Type2Code", "Actor1Type3Code", "Actor2Code",
                            "Actor2Name", "Actor2CountryCode", "Actor2KnownGroup", "Actor2EthnicCode", "Actor2Religion1Code",
                            "Actor2Religion2Code", "Actor2Type1Code", "Actor2Type2Code", "Actor2Type3Code", "IsRootEvent",
                            "EventCode", "EventBaseCode", "EventRootCode", "QuadClass", "GoldsteinScale", "NumMentions", "NumSources",
                            "NumArticles", "AvgTone", "Actor1Geo_Type", "Actor1Geo_FullName", "Actor1Geo_CountryCode",
                            "Actor1Geo_ADM1Code", "Actor1Geo_ADM2Code", "Actor1Geo_Lat", "Actor1Geo_Long", "Actor1Geo_FeatureID",
                            "Actor2Geo_Type", "Actor2Geo_FullName", "Actor2Geo_CountryCode", "Actor2Geo_ADM1Code", "Actor2Geo_ADM2Code",
                            "Actor2Geo_Lat", "Actor2Geo_Long", "Actor2Geo_FeatureID", "ActionGeo_Type", "ActionGeo_FullName", "ActionGeo_CountryCode",
                            "ActionGeo_ADM1Code", "ActionGeo_ADM2Code", "ActionGeo_Lat", "ActionGeo_Long", "ActionGeo_FeatureID",
                            "DATE", "SOURCEURLS"]
            df_useful = filter_rows_2(df_raw, include)
            df_useful["source_filename"] = name  # original ZIP filename
            
            dfs.append(df_useful)

            os.remove(name)
            print(f"Deleted {name}")
        except:
            print(f"{name} corrupted, skipped")
            continue

    return pd.concat(dfs, ignore_index=True)

def fetch_source_pages(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each row in df, download the page at df['SOURCEURL'] and
    return a new DataFrame with columns:
        DATE, SOURCES, SOURCEURL, PAGE_HTML
    """
    records = []

    for idx, row in df.iterrows():
        url = row.get("SOURCEURLS")

        # skip rows without a URL
        if pd.isna(url) or not isinstance(url, str) or not url.strip():
            continue
        
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            # if request fails, keep html as None (or str(e) if you prefer logging)
            print(e)
            html = None

        records.append(
            {
                "DATE": row["DATE"],
                "SOURCES": row["SOURCES"],
                "SOURCEURLS": url,
                "PAGE_HTML": html,
            }
        )
    return pd.DataFrame.from_records(records)


