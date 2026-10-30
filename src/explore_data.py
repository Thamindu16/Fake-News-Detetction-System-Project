import pandas as pd

# 1. Load the datasets
wel = pd.read_csv("data/raw/welfake.csv")
fake = pd.read_csv("data/raw/isot/Fake.csv")
true = pd.read_csv("data/raw/isot/True.csv")

# ISOT has no label column, so we create one (0 = fake, 1 = real)
fake["label"] = 0
true["label"] = 1
isot = pd.concat([fake, true], ignore_index=True)


def report(name, df):
    """Print basic quality checks for a dataset."""
    print(f"\n===== {name} =====")
    print("shape:", df.shape)

    # Missing values in the main text columns
    print("missing values:\n", df[["title", "text"]].isna().sum())

    # Articles whose text is empty or only whitespace
    print("empty text:", (df["text"].fillna("").str.strip() == "").sum())

    # Exact duplicate articles (a model can memorize these)
    print("duplicate texts:", df.duplicated(subset="text").sum())

    # Class balance
    print("label counts:\n", df["label"].value_counts())

    # Average article length (in words) per label
    words = df["text"].fillna("").str.split().str.len()
    print("average words by label:\n", words.groupby(df["label"]).mean())


report("WELFake", wel)
report("ISOT", isot)

# 2. Check WELFake labels by reading sample titles manually
# (the dataset description says 0 = fake, 1 = real, but we verify it ourselves)
print("\n===== WELFake sample titles =====")
for lab in [0, 1]:
    print(f"\n--- label = {lab} ---")
    sample = wel[wel["label"] == lab]["title"].dropna().sample(8, random_state=1)
    print(sample.to_string())

# 3. Leakage check: how often does the word "Reuters" appear per label?
# If it appears almost only in one class, a model can cheat by learning it.
for name, df in [("WELFake", wel), ("ISOT", isot)]:
    has_reuters = df["text"].fillna("").str.contains("Reuters", case=False)
    print(f"\n{name}: share of articles containing 'Reuters' (by label)")
    print(has_reuters.groupby(df["label"]).mean())

# 4. Overlap check: identical articles present in both datasets
overlap = set(wel["text"].dropna()) & set(isot["text"].dropna())
print("\nIdentical articles found in both WELFake and ISOT:", len(overlap))