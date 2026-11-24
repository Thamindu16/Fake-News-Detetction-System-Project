import io
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

URL = "https://www.cs.ucsb.edu/~william/data/liar_dataset.zip"
OUT = Path("data/raw/liar")
OUT.mkdir(parents=True, exist_ok=True)

# 1. Download and unzip the dataset
print("Downloading LIAR ...")
with urllib.request.urlopen(URL, timeout=60) as response:
    data = response.read()
with zipfile.ZipFile(io.BytesIO(data)) as zf:
    zf.extractall(OUT)
print("Files:", [p.name for p in OUT.iterdir()])

# 2. Read the test split (the TSV files have no header row)
columns = [
    "id", "label", "statement", "subject", "speaker", "job", "state",
    "party", "barely_true", "false", "half_true", "mostly_true",
    "pants_on_fire", "context",
]
test = pd.read_csv(OUT / "test.tsv", sep="\t", header=None, names=columns)

print("\nrows:", len(test))
print("\nlabel counts:")
print(test["label"].value_counts())

print("\nsample statements:")
for _, row in test.sample(6, random_state=1).iterrows():
    print(f"  [{row['label']}] {row['statement']}")