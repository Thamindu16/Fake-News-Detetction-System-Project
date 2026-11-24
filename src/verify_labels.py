import pandas as pd

# 1. Load the datasets
wel = pd.read_csv("data/raw/welfake.csv")
fake = pd.read_csv("data/raw/isot/Fake.csv")
true = pd.read_csv("data/raw/isot/True.csv")

# ISOT labels come from the file names, so we trust them (0 = fake, 1 = real)
fake["label"] = 0
true["label"] = 1
isot = pd.concat([fake, true], ignore_index=True)


def keep_valid(df):
    """Drop rows with missing or empty text."""
    df = df.dropna(subset=["text"])
    return df[df["text"].str.strip() != ""]


def consistent_labels(df):
    """Keep one row per unique text, only if all copies share the same label."""
    n_labels = df.groupby("text")["label"].nunique()
    ok_texts = n_labels[n_labels == 1].index
    conflicting = (n_labels > 1).sum()
    print("  texts with conflicting labels (removed):", conflicting)
    out = df[df["text"].isin(ok_texts)].drop_duplicates(subset="text")
    return out[["text", "label"]]


wel = keep_valid(wel)
isot = keep_valid(isot)

print("WELFake:")
wel_clean = consistent_labels(wel)
print("ISOT:")
isot_clean = consistent_labels(isot)

# 2. Match the same article in both datasets using its text
merged = wel_clean.merge(isot_clean, on="text", suffixes=("_welfake", "_isot"))
print("\nArticles found in both datasets:", len(merged))

# 3. Compare the labels given by the two datasets for the same article
# Rows = WELFake label, columns = ISOT label (ISOT: 0 = fake, 1 = real)
table = pd.crosstab(merged["label_welfake"], merged["label_isot"])
print("\nLabel comparison (rows = WELFake, columns = ISOT):")
print(table)

agree = (merged["label_welfake"] == merged["label_isot"]).mean()
print(f"\nShare of articles where both labels agree: {agree:.2%}")