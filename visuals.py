import matplotlib.pyplot as plt
from collections import Counter
import pandas as pd

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