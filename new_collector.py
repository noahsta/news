import re
import os
import zipfile
import requests
from pathlib import Path
from urllib.request import urlretrieve
import pandas as pd

def extract_txt(file_path, start_time=None, end_time=None):
    """
    Extracts URLs from a document and filters them based on a time range.

    Args:
        file_path (str): Path to the document.
        start_time (str, optional): Start time in 'YYYYMMDDHHMMSS' format.
        end_time (str, optional): End time in 'YYYYMMDDHHMMSS' format.

    Returns:
        list: Filtered URLs.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    urls = []
    for line in lines:
        # Extract the URL from each line
        match = re.search(r'http[s]?://\S+', line)
        if match:
            url = match.group(0)
            # Extract the timestamp from the URL
            timestamp_match = re.search(r'(\d{14})\.export\.CSV\.zip', url)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                urls.append((timestamp, url))

    # Filter URLs based on the time range
    filtered_urls = []
    for timestamp, url in urls:
        if start_time and timestamp < start_time:
            continue
        if end_time and timestamp > end_time:
            continue
        filtered_urls.append(url)

    return filtered_urls

def fetch_html(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each row in df, download the page at df['SOURCEURL'] and
    return a new DataFrame with columns:
        DATE, SOURCES, SOURCEURL, PAGE_HTML
    """
    records = []

    for idx, row in df.iterrows():
        url = row.get("SOURCEURLS")
        success = False
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            html = resp.text
            success = True
        except Exception as e:
            # if request fails, keep html as None (or str(e) if you prefer logging)
            print(e)
            html = None

        records.append(
            {
                "DATE": row["Day"],
                "SOURCEURLS": url,
                "PAGE_HTML": html,
                "REGION": row["RegionTopic"]
            }
        )
        if success:
            print("downloaded: " + url)
        else:
            print("failed to download: " + url)
    return pd.DataFrame.from_records(records)
