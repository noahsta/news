import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd
import glob
import numpy as np
import os
import re

def plot_found_locations(df: pd.DataFrame, col):
    """
    Given a dataframe containing a column FOUND_LOCATIONS,
    where each entry is a list of matched location-words,
    compute total frequencies and plot a bar chart with matplotlib.
    """

    # Flatten list-of-lists into one list
    all_words = []
    for lst in df[col]:
        if isinstance(lst, list):
            all_words.extend(lst)
        elif isinstance(lst, str):
            all_words.append(lst)

    # Count frequencies
    counts = Counter(all_words)

    words = list(counts.keys())
    values = list(counts.values())

    # Bar plot
    plt.figure(figsize=(8, 4))
    plt.bar(words, values)
    plt.xlabel("Found Location Terms")
    plt.ylabel("Frequency")
    plt.title("Frequency of Found Location Keywords")
    plt.tight_layout()
    plt.show()

def length_hist(year: int, regions: set={"uk", "ch", "de", "ca"}, DATA_DIR: str= "./"):
    PATTERN = f"FULLTEXT{str(year)}*.csv"
    region_data = {r: [] for r in regions}

    files = glob.glob(os.path.join(DATA_DIR, PATTERN))
    if not files:
        raise FileNotFoundError(f"No files matching pattern {PATTERN!r} found.")

    # filename format: FULLTEXTYYYYMMDD_YYYYMMDD_region.csv
    region_regex = re.compile(r"_([a-zA-Z]{2})\.csv$")

    for f in files:
        m = region_regex.search(os.path.basename(f))
        if not m:
            continue

        region = m.group(1).lower()
        if region not in regions:
            continue

        df = pd.read_csv(f)

        if "LEN" not in df.columns:
            raise ValueError(f"'LEN' column missing in {f}")

        region_data[region].extend(df["LEN"].dropna().tolist())

    # ---- shared axis scale: global max over all regions ----
    all_lengths = [x for r in regions for x in region_data[r]]
    if not all_lengths:
        raise ValueError("No LEN data found for any region.")

    max_len = max(all_lengths)

    # define common bin edges using global max
    n_bins = 50
    bin_edges = np.linspace(0, max_len, n_bins + 1)

    # ---- Plot histograms ----
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.flatten()

    for ax, region in zip(axes, sorted(regions)):
        data = region_data[region]
        if len(data) == 0:
            ax.set_title(region.upper() + " (no data)")
            ax.axis("off")
            continue

        ax.hist(data, bins=bin_edges)
        ax.set_title(f"Histogram of LEN – {region.upper()}")
        ax.set_xlabel("Text length")
        ax.set_ylabel("Frequency")
        ax.grid(True)

        # enforce shared x-axis scale
        ax.set_xlim(0, max_len)

    plt.tight_layout()
    plt.show()



if __name__=="__main__":
    length_hist(year=2015)