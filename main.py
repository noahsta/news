import re
import os
import zipfile
import requests
from pathlib import Path
from urllib.request import urlretrieve
import pandas as pd

from data_selection import filter_rows
from visuals import plot_found_locations
from new_collector import extract_txt
import collector

if __name__=="__main__":
        # Example usage:
    file_path = 'titlepage_2.txt'  # Replace with the full path if needed
    start_time = '20200310000000'  # Example: February 18, 2015, 00:00:00
    end_time = '20200320235959'    # Example: February 18, 2015, 23:59:59
    filtered_urls = extract_txt(file_path, start_time, end_time)

    data = collector.download_and_filter(filtered_urls)
    plot_found_locations(data, col="DOMAIN_EXT")
    data.to_csv(start_time[:8]+"_"+end_time[:8]+".csv", index=False)