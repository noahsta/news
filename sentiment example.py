from transformers import pipeline
import pandas as pd

data = pd.read_csv("FULLTEXT20230301_20230930_ch.csv")


# Load the classification pipeline with the specified model
pipe = pipeline("text-classification", model="tabularisai/multilingual-sentiment-analysis")

# Classify a new sentence
sentence1 = "I love this product! It's amazing and works perfectly."
result = pipe(sentence1)
print(result)

sentence2 = data["TEXT"][0]
print(pipe(sentence2))