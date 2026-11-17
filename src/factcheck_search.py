import os
import sys

import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")  # print special characters correctly on Windows

load_dotenv()  # reads FACTCHECK_API_KEY from the .env file
API_KEY = os.environ.get("FACTCHECK_API_KEY")
URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"


def search_fact_checks(query, language="en", max_results=5):
    """Return fact-checks related to a claim, as a list of simple dicts."""
    if not API_KEY:
        raise RuntimeError("FACTCHECK_API_KEY is not set. Put it in the .env file.")

    params = {
        "query": query,
        "languageCode": language,
        "pageSize": max_results,
        "key": API_KEY,
    }
    response = requests.get(URL, params=params, timeout=15)
    response.raise_for_status()  # stop with a clear error if the request failed

    results = []
    for claim in response.json().get("claims", []):
        for review in claim.get("claimReview", []):
            results.append({
                "claim": claim.get("text"),
                "claimant": claim.get("claimant"),
                "rating": review.get("textualRating"),
                "publisher": review.get("publisher", {}).get("name"),
                "url": review.get("url"),
                "review_date": review.get("reviewDate"),
            })
    return results


if __name__ == "__main__":
    # Usage: python src/factcheck_search.py "your claim here"
    query = " ".join(sys.argv[1:]) or "5G causes covid"
    print("query:", query)
    matches = search_fact_checks(query)
    print("fact-checks found:", len(matches))
    for m in matches:
        print(f"\n  claim:     {m['claim']}")
        print(f"  claimant:  {m['claimant']}")
        print(f"  rating:    {m['rating']}")
        print(f"  publisher: {m['publisher']}")
        print(f"  url:       {m['url']}")