import csv
from pathlib import Path

import pandas as pd

RAW = Path("data/raw/liar")
OUT = Path("data/processed_liar")
OUT.mkdir(parents=True, exist_ok=True)

COLUMNS = [
    "id", "label", "statement", "subject", "speaker", "job", "state",
    "party", "barely_true", "false", "half_true", "mostly_true",
    "pants_on_fire", "context",
]

# Our convention everywhere in this project: 0 = real, 1 = fake.
# The two ambiguous middle labels (barely-true, half-true) are not in the map, so they get dropped.
LABEL_MAP = {
    "pants-fire": 1,
    "false": 1,
    "mostly-true": 0,
    "true": 0,
}

frames = []
for split in ["train", "valid", "test"]:
    # QUOTE_NONE: treat quote characters as normal text, so statements with quotes do not break parsing
    df = pd.read_csv(
        RAW / f"{split}.tsv", sep="\t", header=None, names=COLUMNS, quoting=csv.QUOTE_NONE
    )
    df["split"] = split
    frames.append(df)

all_df = pd.concat(frames, ignore_index=True)
print("all statements:", len(all_df))
print("\noriginal label counts:")
print(all_df["label"].value_counts())

# Map to real/fake and drop the ambiguous ones
all_df["binary"] = all_df["label"].map(LABEL_MAP)
df = all_df.dropna(subset=["binary"]).copy()
df["binary"] = df["binary"].astype(int)

# Remove duplicate statements and empty ones
df = df.dropna(subset=["statement"])
df = df.drop_duplicates(subset="statement")

out = df[["id", "split", "label", "binary", "statement"]].rename(
    columns={"label": "original_label", "binary": "label"}
)
out.to_csv(OUT / "liar_eval.csv", index=False)

print("\nkept for evaluation:", len(out))
print("label counts (0 = real, 1 = fake):")
print(out["label"].value_counts())
print("\nwords per statement (average):", round(out["statement"].str.split().str.len().mean(), 1))