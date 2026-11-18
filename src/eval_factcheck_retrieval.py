import sys
import time

import pandas as pd
from sentence_transformers import util

from claim_matcher import _model, lookup   # same keyword search and same similarity model
from factcheck_search import FactCheckError

sys.stdout.reconfigure(encoding="utf-8")

SAMPLE_SIZE = 50   # kept small: every statement costs up to 2 API calls
SEED = 42          # fixed seed, so the same 50 statements are picked every time

df = pd.read_csv("data/processed_liar/liar_eval.csv")
sample = df.sample(SAMPLE_SIZE, random_state=SEED).reset_index(drop=True)

rows = []
for i, row in sample.iterrows():
    statement = row["statement"]
    error, query, matches = "", None, []
    try:
        query, matches = lookup(statement)
    except FactCheckError as problem:
        error = str(problem)

    best_sim = best_claim = best_publisher = None
    if matches:
        # Which returned fact-check is closest in meaning to the statement?
        statement_vec = _model.encode(statement, convert_to_tensor=True)
        claim_vecs = _model.encode([m["claim"] or "" for m in matches], convert_to_tensor=True)
        sims = util.cos_sim(statement_vec, claim_vecs)[0]
        k = int(sims.argmax())
        best_sim = float(sims[k])
        best_claim, best_publisher = matches[k]["claim"], matches[k]["publisher"]

    rows.append({
        "statement": statement, "query": query, "n_results": len(matches),
        "best_similarity": best_sim, "best_claim": best_claim,
        "best_publisher": best_publisher, "error": error,
    })
    print(f"{i + 1}/{SAMPLE_SIZE} done", end="\r")
    time.sleep(0.5)   # be gentle with the API

res = pd.DataFrame(rows)
res.to_csv("data/processed_liar/retrieval_check.csv", index=False)

ok = res[res["error"] == ""]
print("\n\nstatements tested:", len(res))
print("lookups that failed:", len(res) - len(ok))
if ok.empty:
    sys.exit("Every lookup failed, so there is nothing to measure. Try again later.")

print(f"got at least one result:  {(ok['n_results'] > 0).mean():.0%}")
for t in (0.5, 0.6, 0.7, 0.8):
    print(f"best similarity >= {t}:    {(ok['best_similarity'].fillna(0) >= t).mean():.0%}")

# Show examples spread from the highest to the lowest similarity, to judge by eye
found = ok.dropna(subset=["best_similarity"]).sort_values("best_similarity", ascending=False)
step = max(1, len(found) // 12)
for _, r in found.iloc[::step].iterrows():
    print(f"\n[{r['best_similarity']:.2f}] statement: {r['statement']}")
    print(f"        matched:   {r['best_claim']}  ({r['best_publisher']})")