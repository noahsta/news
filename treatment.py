import pandas as pd
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def longest_text(html: str):
    if html is None:
        return None
    else:
        soup = BeautifulSoup(html, "html.parser")
        best = (None, None, -1)  # (tag_name, text, length)

        for tag in soup.find_all(['p','div','section','article','li']):
            text = tag.get_text(" ", strip=True)
            L = len(text)
            if L > best[2]:
                best = (tag.name, text, L)

        return best

def deduplicate_by_text_similarity(df: pd.DataFrame,
                                   column: str = "TEXT",
                                   threshold: float = 0.85) -> pd.DataFrame:
    
    # work on a copy to avoid side effects
    df = df.copy().reset_index(drop=True)

    # handle trivial edge cases
    if len(df) <= 1:
        return df

    texts = df[column].astype(str).fillna("")

    # Vectorize with TF-IDF
    vec = TfidfVectorizer(stop_words="english").fit(texts)
    X = vec.transform(texts)

    # pairwise cosine similarity matrix
    sim = cosine_similarity(X)

    # mask diagonal to avoid self-matches
    np.fill_diagonal(sim, 0.0)

    keep = np.ones(len(df), dtype=bool)

    # greedy: if i is kept, drop all later j similar to i
    for i in range(len(df)):
        if not keep[i]:
            continue
        duplicates = np.where(sim[i] >= threshold)[0]
        keep[duplicates] = False

    return df[keep].reset_index(drop=True)

from new_collector import fetch_html
from data_selection import remove_duplicate_sourceurls


if __name__=="__main__":

    filename = "20200310_20200310"
    data = pd.read_csv(filename + ".csv")

    domains = [".uk",".ch", ".de", ".ca"]
    for domain in domains:
        mask = data["DOMAIN_EXT"] == domain
        data_region = data[mask]
        if len(data_region) >= 1:
            print("total datapoints in region "+ domain + ": " + str(len(data_region)))
            data_region = remove_duplicate_sourceurls(data_region)
            print("pandas url deduplication: " + str(len(data_region)))

            texts = fetch_html(data_region)
            texts["TEXT"] = texts["PAGE_HTML"].apply(longest_text)
            texts = texts.drop(["PAGE_HTML"], axis=1)
            texts["LEN"] = texts["TEXT"].apply(lambda t: t[2] if t and t[2] is not None else 0)
            texts["TEXT"] = texts["TEXT"].apply(lambda t: t[1] if t and t[1] is not None else 0)

            print("successfully downloaded " + str(len(texts)))
            texts = deduplicate_by_text_similarity(texts, "TEXT", threshold=0.95)
            print("fulltext deduplication " + str(len(texts)))

            thresh = 1e3
            succ = texts["LEN"] > thresh
            texts = texts[succ]

            print("final: " + str(len(texts)) + " texts longer than " + str(thresh) + "characters")
            
            texts.to_csv("FULLTEXT" + filename + "_" + domain[1:] + ".csv")
        else:
            print("no data from " + domain)