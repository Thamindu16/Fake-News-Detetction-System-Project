import re
from pathlib import Path

import pandas as pd

SRC = Path("data/processed")
DST = Path("data/processed_v2")
DST.mkdir(parents=True, exist_ok=True)

# "may" and "march" are skipped because they are also ordinary English words
MONTHS = r"january|february|april|june|july|august|september|october|november|december"
DAYS = r"monday|tuesday|wednesday|thursday|friday|saturday|sunday"

# Each rule is (regex pattern, replacement). Order matters.
RULES = [
    # 1. URLs, bare domain names, @handles and #hashtags
    (r"https?://\S+|www\.\S+", " "),
    (r"\b[\w-]+\.(?:com|org|net|co\.uk)\b", " "),
    (r"[@#]\w+", " "),
    # 2. Image credits and web page boilerplate
    (r"featured image|getty images?|image credit|photo credit|flickr|screenshot", " "),
    (r"follow [^.\n]{0,80}? on (?:twitter|facebook)[^.\n]*", " "),
    (r"\b(?:twitter|facebook|instagram|youtube)\b", " "),
    # 3. Publisher names
    (r"breitbart(?: news)?|new york times|washington post|associated press|fox news|\bcnn\b", " "),
    # 4. Dates: years, month names, weekday names
    (r"\b(?:19|20)\d{2}\b", " "),
    (rf"\b(?:{MONTHS})\b", " "),
    (rf"\b(?:{DAYS})\b", " "),
]
COMPILED = [(re.compile(pattern, re.IGNORECASE), repl) for pattern, repl in RULES]


def scrub(text):
    """Remove source/format/date markers that can leak the label."""
    if not isinstance(text, str):
        return ""
    for pattern, repl in COMPILED:
        text = pattern.sub(repl, text)
    return re.sub(r"\s+", " ", text).strip()  # collapse extra spaces


# Same rows, same split; only the text changes, so the comparison is fair
for split in ["train", "val", "test"]:
    df = pd.read_csv(SRC / f"{split}.csv")
    df["title"] = df["title"].apply(scrub)
    df["text"] = df["text"].apply(scrub)
    df.to_csv(DST / f"{split}.csv", index=False)
    print(split, "scrubbed:", len(df))