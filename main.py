import re
import os
import zipfile
import requests
from pathlib import Path
from urllib.request import urlretrieve
import pandas as pd
import matplotlib.pyplot as plt

from data_selection import filter_rows, remove_duplicate_sourceurls
from visuals import plot_found_locations
from new_collector import extract_txt, fetch_html
import collector
import treatment
from treatment import longest_text

from bs4 import BeautifulSoup

if __name__=="__main__":
    # Example usage:
    file_path = 'titlepage_2.txt'  # Replace with the full path if needed
    start_time = '20200310000000'  # Example: February 18, 2015, 00:00:00
    end_time = '20200310010000'    # Example: February 18, 2015, 23:59:59

    #or define loop over different times
    #for (start_time, end_time) in [('20200310000000', '20200310120000'), etc.]:
    filtered_urls = extract_txt(file_path, start_time, end_time)
    data = collector.download_and_filter(filtered_urls, include="no ukr")
    #include = "spec", "no ukr", "no syr"
    data.to_csv(start_time[:8]+"_"+end_time[:8]+"_test.csv", index=False)
    

