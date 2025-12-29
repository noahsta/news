import re
from collections import Counter

import pandas as pd
import matplotlib.pyplot as plt

from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0  # make language detection deterministic

import nltk
from nltk.corpus import stopwords

try:
    nltk.find("corpus/stopwords.zip")
except:
    nltk.download("stopwords")


data = pd.read_csv("FULLTEXT20230301_20230930_ch.csv")

stop_en = set(stopwords.words("english"))
stop_de = set(stopwords.words("german"))

# --- Helper: language detection wrapper ---

def detect_lang_safe(text: str) -> str | None:
    """
    Try to detect language ('en', 'de') from text.
    Return 'en', 'de', or None if detection fails or is different.
    """
    text = text.strip()
    if not text:
        return None
    try:
        lang_code = detect(text)  # returns ISO 639-1 like 'en', 'de', 'fr', ...
    except Exception:
        return None

    if lang_code == "en":
        return "en"
    if lang_code == "de":
        return "de"
    return None

# --- Helper: tokenization ---

token_pattern = re.compile(r"[a-zA-ZäöüÄÖÜß]+")

def tokenize(text: str) -> list[str]:
    """
    Lowercase and extract alphabetic tokens including German umlauts / ß.
    """
    text = text.lower()
    return token_pattern.findall(text)

# --- Main counting loop ---

discarded_count = 0
word_counts = Counter()
word_counts_en = Counter()
word_counts_de = Counter()

for _, row in data.iterrows():
    text = row.get("TEXT", "")
    if not isinstance(text, str):
        discarded_count += 1
        continue

    lang = detect_lang_safe(text)
    if lang is None:
        discarded_count += 1
        continue

    if lang == "en":
        stop = stop_en
    elif lang == "de":
        stop = stop_de
    else:
        # shouldn't happen due to detect_lang_safe, but keep for safety
        discarded_count += 1
        continue

    tokens = tokenize(text)

    # Filter: remove stopwords, and very short tokens (e.g. 1-letter)
    filtered = [
        tok for tok in tokens
        if tok not in stop and len(tok) > 1
    ]

    # Update counters
    word_counts.update(filtered)
    if lang == "en":
        word_counts_en.update(filtered)
    elif lang == "de":
        word_counts_de.update(filtered)

print(f"Number of discarded texts (non EN/DE or empty): {discarded_count}")

# --- Plot histogram of most common non-trivial words (combined EN+DE) ---

top_n = 50
most_common = word_counts.most_common(top_n)
if not most_common:
    raise ValueError("No non-trivial words found after filtering.")

words, freqs = zip(*most_common)

plt.figure(figsize=(12, 6))
plt.bar(range(len(words)), freqs)
plt.xticks(range(len(words)), words, rotation=90)
plt.xlabel("Word")
plt.ylabel("Frequency")
plt.title(f"Top {top_n} most common non-trivial words (EN+DE)")
plt.tight_layout()
plt.show()

# --- OPTIONAL: separate histograms per language ---

# English
top_n_en = 30
mc_en = word_counts_en.most_common(top_n_en)
if mc_en:
    words_en, freqs_en = zip(*mc_en)
    plt.figure(figsize=(10, 5))
    plt.bar(range(len(words_en)), freqs_en)
    plt.xticks(range(len(words_en)), words_en, rotation=90)
    plt.xlabel("Word")
    plt.ylabel("Frequency")
    plt.title(f"Top {top_n_en} EN words (non-trivial)")
    plt.tight_layout()
    plt.show()

# German
top_n_de = 30
mc_de = word_counts_de.most_common(top_n_de)
if mc_de:
    words_de, freqs_de = zip(*mc_de)
    plt.figure(figsize=(10, 5))
    plt.bar(range(len(words_de)), freqs_de)
    plt.xticks(range(len(words_de)), words_de, rotation=90)
    plt.xlabel("Word")
    plt.ylabel("Frequency")
    plt.title(f"Top {top_n_de} DE words (non-trivial)")
    plt.tight_layout()
    plt.show()
