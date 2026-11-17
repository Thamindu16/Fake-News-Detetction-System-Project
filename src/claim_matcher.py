import re
import sys

from sentence_transformers import SentenceTransformer, util

from factcheck_search import search_fact_checks

sys.stdout.reconfigure(encoding="utf-8")

# Small model that turns text into numbers capturing its meaning. Runs fine on CPU.
_model = SentenceTransformer("all-MiniLM-L6-v2")


def split_sentences(text):
    """Split text into sentences and drop very short fragments."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if len(p.split()) >= 5]


def pick_queries(text, max_queries=3):
    """Choose which parts of the input to look up. Short input is used as it is."""
    text = text.strip()
    if len(text.split()) <= 40:
        return [text]
    sentences = split_sentences(text)
    if not sentences:
        return [text[:300]]
    queries = sentences[:1]                                        # the opening sentence
    queries += [s for s in sentences[1:] if re.search(r"\d", s)]   # sentences containing numbers
    return queries[:max_queries]


def match_claims(text, max_queries=3, per_query=5):
    """Look up fact-checks for parts of the text and score how close each match is."""
    found, seen = [], set()
    for query in pick_queries(text, max_queries):
        for match in search_fact_checks(query, max_results=per_query):
            key = (match["url"], match["claim"])
            if key in seen:
                continue
            seen.add(key)
            match["query"] = query
            found.append(match)
    if not found:
        return []

    # Compare each input part with the claim text of the fact-check it matched
    query_vecs = _model.encode([m["query"] for m in found], convert_to_tensor=True)
    claim_vecs = _model.encode([m["claim"] or "" for m in found], convert_to_tensor=True)
    scores = util.cos_sim(query_vecs, claim_vecs).diagonal()
    for match, score in zip(found, scores):
        match["similarity"] = float(score)
    return sorted(found, key=lambda m: m["similarity"], reverse=True)


if __name__ == "__main__":
    # Usage: python src/claim_matcher.py "your text here"
    text = " ".join(sys.argv[1:]) or "5G causes covid"
    print("queries used:", pick_queries(text))
    results = match_claims(text)
    print("matches:", len(results))
    for m in results:
        print(f"\n[similarity {m['similarity']:.2f}] {m['claim']}")
        print(f"    rating: {(m['rating'] or '')[:100]} | {m['publisher']}")