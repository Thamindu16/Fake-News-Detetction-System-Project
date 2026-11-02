import re
import sys
from pathlib import Path

import pandas as pd

# Make sure special characters (curly quotes, etc.) print correctly on Windows
sys.stdout.reconfigure(encoding="utf-8")

DATA = Path("data/processed_v3")
# Words to inspect: taken from the command line, or this default list
WORDS = sys.argv[1:] or ["https", "com", "wire", "pic", "milo", "27"]

train = pd.read_csv(DATA / "train.csv")
train["full"] = train["title"].fillna("") + ". " + train["text"].fillna("")

for word in WORDS:
    # \b means "word boundary", so "com" does not match inside "common"
    pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
    has = train["full"].str.contains(pattern)

    print(f"\n===== '{word}' =====")
    # Share of articles containing the word, per label (0 = real, 1 = fake)
    shares = has.groupby(train["label"]).mean().round(4)
    print(f"  share of REAL articles: {shares.get(0, 0):.2%}")
    print(f"  share of FAKE articles: {shares.get(1, 0):.2%}")

    # Show up to 3 random examples per label, with the surrounding text
    for label, name in [(0, "real"), (1, "fake")]:
        subset = train[has & (train["label"] == label)]
        if subset.empty:
            continue
        for text in subset.sample(min(3, len(subset)), random_state=1)["full"]:
            m = pattern.search(text)
            start = max(0, m.start() - 60)
            snippet = text[start:m.end() + 60].replace("\n", " ")
            print(f"  [{name}] ...{snippet}...")