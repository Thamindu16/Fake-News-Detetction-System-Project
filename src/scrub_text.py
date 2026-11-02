import re
from pathlib import Path

import pandas as pd

SRC = Path("data/processed")
DST = Path("data/processed_v3")  # new folder, so processed_v2 stays for comparison
DST.mkdir(parents=True, exist_ok=True)

# "may" and "march" are skipped because they are also ordinary English words
MONTHS = r"january|february|april|june|july|august|september|october|november|december"
DAYS = r"monday|tuesday|wednesday|thursday|friday|saturday|sunday"

# Abbreviations are matched case-sensitively (capitalised only), because words like
# "sun", "sat" and "wed" are also ordinary English words. (?-i:...) turns off
# case-insensitivity inside the group.
MONTH_ABBR = r"(?-i:\b(?:Jan|Feb|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b\.?)"
DAY_ABBR = r"(?-i:\b(?:Mon|Tue|Tues|Wed|Thu|Thur|Thurs|Fri|Sat|Sun)\b\.?)"

# Each rule is (regex pattern, replacement). Order matters.
RULES = [
    # 1. Complete URLs, then broken URL leftovers such as "https: ." or "https:// /"
    (r"https?://\S+|www\.\S+", " "),
    (r"\bhttps?\b\s*:?\s*[./]*", " "),
    # 2. Domain names, including the "site. com" form with a space before "com"
    (r"\b[\w-]+\.(?:com|org|net|co\.uk)\b", " "),
    (r"\s*\.\s*(?-i:com|org|net)\b", " "),
    (r"\bcom\b", " "),
    # 3. Leftovers of embedded tweets: "pic. /abc123", empty parentheses, @handles, #hashtags
    (r"\bpic\.(?:\s*/\S+)?", " "),
    (r"\(\s*\)", " "),
    (r"[@#]\w+", " "),
    # 4. Image credits and page boilerplate
    (r"featured image|getty images?|image credit|photo credit|flickr|screen ?captures?", " "),
    (r"follow [^.\n]{0,80}? on (?:twitter|facebook)[^.\n]*", " "),
    (r"\b(?:twitter|facebook|instagram|youtube)\b", " "),
    (r"\bread more\b|\bshare this\b|©", " "),
    # 5. Publisher names and site signatures
    (r"breitbart(?: news)?|new york times|washington post|associated press|fox news|\bcnn\b", " "),
    (r"21st century wire(?: says)?|press tv", " "),
    # 6. Dates: years, month names, weekday names, and their abbreviations
    (r"\b(?:19|20)\d{2}\b", " "),
    (rf"\b(?:{MONTHS})\b", " "),
    (rf"\b(?:{DAYS})\b", " "),
    (MONTH_ABBR, " "),
    (DAY_ABBR, " "),
    # 7. Punctuation clean-up: removing the pieces above leaves messy punctuation
    (r"\s+([.,;:!?])", r"\1"),   # no space before punctuation
    (r"(?:\s*,){2,}", ","),      # ", ," becomes ","
    (r"\.(?:\s*\.)+", "."),      # ". ." becomes "."
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