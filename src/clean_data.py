import re
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

RAW = Path("data/raw/welfake.csv")
OUT = Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)

MIN_WORDS = 30   # articles shorter than this are mostly junk
SEED = 42        # fixed seed so the split is reproducible

df = pd.read_csv(RAW)[["title", "text", "label"]].copy()
print("start:", len(df))

# Label meaning in THIS file (verified against ISOT): 0 = real, 1 = fake
df["label_name"] = df["label"].map({0: "real", 1: "fake"})

# 1. Remove missing / empty texts
df["title"] = df["title"].fillna("")
df = df.dropna(subset=["text"])
df = df[df["text"].str.strip() != ""]
print("after removing empty texts:", len(df))

# 2. Remove source markers that leak the label (e.g. "WASHINGTON (Reuters) -")
DATELINE = re.compile(r"^\s*[A-Z][A-Za-z0-9 ,.'/&-]{0,60}\(Reuters\)\s*[-–—:]*\s*")


def strip_source_markers(text):
    text = DATELINE.sub("", text)                              # leading "CITY (Reuters) -"
    text = re.sub(r"\(?Reuters\)?", "", text, flags=re.IGNORECASE)  # any other mention
    return text.strip()


df["text"] = df["text"].apply(strip_source_markers)
df["title"] = df["title"].apply(strip_source_markers)

# 3. Remove very short articles
words = df["text"].str.split().str.len()
df = df[words >= MIN_WORDS]
print(f"after removing articles under {MIN_WORDS} words:", len(df))

# 4. Remove duplicates and near-duplicates
# Two articles with the same first 300 characters are treated as the same article.
df["key"] = df["text"].str.lower().str[:300]

# If the same article appears with different labels, we cannot trust it: drop it.
n_labels = df.groupby("key")["label"].transform("nunique")
print("articles with conflicting labels (removed):", (n_labels > 1).sum())
df = df[n_labels == 1]

df = df.drop_duplicates(subset="key").drop(columns="key")
print("after removing duplicates:", len(df))

# 5. Leakage re-check: "Reuters" should be gone from both classes now
reuters = df["text"].str.contains("Reuters", case=False)
print("\nshare of articles still containing 'Reuters' (by label):")
print(reuters.groupby(df["label"]).mean())

print("\nfinal label counts:")
print(df["label_name"].value_counts())

# 6. Split into train / validation / test (80 / 10 / 10)
# stratify keeps the real/fake ratio the same in every split
train, temp = train_test_split(
    df, test_size=0.2, stratify=df["label"], random_state=SEED
)
val, test = train_test_split(
    temp, test_size=0.5, stratify=temp["label"], random_state=SEED
)

train.to_csv(OUT / "train.csv", index=False)
val.to_csv(OUT / "val.csv", index=False)
test.to_csv(OUT / "test.csv", index=False)

print("\nsplit sizes -> train:", len(train), "| val:", len(val), "| test:", len(test))