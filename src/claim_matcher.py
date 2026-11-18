import re
import sys

from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from factcheck_search import FactCheckError, search_fact_checks

sys.stdout.reconfigure(encoding="utf-8")

# Small model that turns text into numbers capturing its meaning. Runs fine on CPU.
_model = SentenceTransformer("all-MiniLM-L6-v2")

# Words that appear in many news sentences but say nothing about the topic
GENERIC_WORDS = {
    "said", "says", "say", "according", "announced", "official", "officials",
    "reported", "reports", "report", "experts", "expert", "called", "told",
    "added", "today", "yesterday", "last", "month", "week", "year", "years",
    "people", "new", "news", "shared", "times", "post", "posts", "claim",
    "claims", "claimed", "viral",
}
IGNORED_WORDS = set(ENGLISH_STOP_WORDS) | GENERIC_WORDS


def split_sentences(text):
    """Split text into sentences and drop very short fragments."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if len(p.split()) >= 5]


def pick_sentences(text, max_sentences=3):
    """Choose which sentences to look up: the first few. Short input is used as it is."""
    text = text.strip()
    if len(text.split()) <= 25:
        return [text]
    sentences = split_sentences(text)
    return sentences[:max_sentences] or [text[:300]]


def keywords(sentence, limit):
    """Pick the most informative words: numbers first, then names, then words in their original order."""
    sentence = re.sub(r"(?<=\d),(?=\d)", "", sentence)  # "10,000" becomes "10000"
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", sentence)
    candidates, seen = [], set()
    for position, word in enumerate(words):
        lower = word.lower()
        has_digit = any(c.isdigit() for c in word)
        if lower in IGNORED_WORDS or lower in seen:
            continue
        if len(word) < 3 and not has_digit:
            continue
        seen.add(lower)
        score = 0
        if has_digit:
            score = 2        # for example "5G" or "300"
        elif word[0].isupper() and position > 0:
            score = 1.5      # probably a name, for example "Gates"
        candidates.append((score, position, word))
    # Highest score first; when scores tie, the word that comes first in the sentence wins
    best = sorted(candidates, key=lambda item: (-item[0], item[1]))[:limit]
    return [word for _, _, word in sorted(best, key=lambda item: item[1])]


def lookup(sentence, limits=(3, 2), per_query=5):
    """Search with a few keywords; if nothing is found, retry with fewer."""
    if len(keywords(sentence, 3)) < 2:
        return None, []   # one lonely word (for example a bare number) is not a claim
    tried, last_query = set(), None
    for limit in limits:
        words = keywords(sentence, limit)
        query = " ".join(words)
        if not words or query in tried:
            continue
        tried.add(query)
        last_query = query
        found = search_fact_checks(query, max_results=per_query)
        if found:
            return query, found
    return last_query, []


def match_claims(text, max_sentences=3):
    """Find fact-checks related to the text and score how close each one is to it."""
    found, seen, searches, failed = [], set(), [], 0
    for sentence in pick_sentences(text, max_sentences):
        try:
            query, matches = lookup(sentence)
        except FactCheckError:
            failed += 1          # the service had a problem: note it and carry on
            continue
        if query:
            searches.append(query)
        for match in matches:
            key = (match["url"], match["claim"])
            if key in seen:
                continue
            seen.add(key)
            match["sentence"] = sentence
            found.append(match)

    if found:
        # Compare each input sentence with the claim text of the fact-check it matched
        sentence_vecs = _model.encode([m["sentence"] for m in found], convert_to_tensor=True)
        claim_vecs = _model.encode([m["claim"] or "" for m in found], convert_to_tensor=True)
        scores = util.cos_sim(sentence_vecs, claim_vecs).diagonal()
        for match, score in zip(found, scores):
            match["similarity"] = float(score)
        found.sort(key=lambda m: m["similarity"], reverse=True)

    return {"matches": found, "searches": searches, "failed_lookups": failed}


if __name__ == "__main__":
    # Usage: python src/claim_matcher.py "your text here"
    text = " ".join(sys.argv[1:]) or "5G causes covid"
    result = match_claims(text)
    print("keyword searches used:", result["searches"])
    print("failed lookups:", result["failed_lookups"])
    print("matches:", len(result["matches"]))
    for m in result["matches"]:
        print(f"\n[similarity {m['similarity']:.2f}] {m['claim']}")
        print(f"    rating: {(m['rating'] or '')[:100]} | {m['publisher']}")