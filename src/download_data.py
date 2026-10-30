from datasets import load_dataset
from pathlib import Path

OUT = Path("data/raw")
OUT.mkdir(parents=True, exist_ok=True)

ds = load_dataset("davanstrien/WELFake")["train"]
df = ds.to_pandas()
df.to_csv(OUT / "welfake.csv", index=False)

print(df.shape)
print(df["label"].value_counts())