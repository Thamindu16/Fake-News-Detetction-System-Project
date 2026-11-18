import os
import sys
import time

import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")  # print special characters correctly on Windows

load_dotenv()  # reads FACTCHECK_API_KEY from the .env file
API_KEY = os.environ.get("FACTCHECK_API_KEY")
URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

# Temporary problems worth retrying. Other errors (bad key, bad request) will not fix themselves.
RETRY_CODES = {429, 500, 502, 503, 504}


class FactCheckError(Exception):
    """Raised when the lookup fails. The message never contains the API key."""


def parse_results(data):
    """Turn the API response into a simple list of dicts."""
    results = []
    for claim in data.get("claims", []):
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


def search_fact_checks(query, language="en", max_results=5, retries=3):
    """Return fact-checks related to a claim. Raises FactCheckError if the lookup fails."""
    if not API_KEY:
        raise FactCheckError("FACTCHECK_API_KEY is not set. Put it in the .env file.")

    params = {
        "query": query,
        "languageCode": language,
        "pageSize": max_results,
        "key": API_KEY,
    }

    problem = "unknown problem"
    for attempt in range(retries):
        try:
            response = requests.get(URL, params=params, timeout=15)
        except requests.exceptions.RequestException as error:
            # Use only the error type: the full message can contain the URL, and the URL contains the key
            problem = type(error).__name__
        else:
            if response.status_code == 200:
                return parse_results(response.json())
            problem = f"HTTP {response.status_code}"
            if response.status_code not in RETRY_CODES:
                break  # retrying will not help
        if attempt < retries - 1:
            time.sleep(2 ** attempt)  # wait 1 second, then 2 seconds, before the next try

    raise FactCheckError(f"Fact-check lookup failed ({problem}).")


if __name__ == "__main__":
    # Usage: python src/factcheck_search.py "your claim here"
    query = " ".join(sys.argv[1:]) or "5G causes covid"
    print("query:", query)
    try:
        matches = search_fact_checks(query)
    except FactCheckError as error:
        print("ERROR:", error)
        sys.exit(1)

    print("fact-checks found:", len(matches))
    for m in matches:
        print(f"\n  claim:     {m['claim']}")
        print(f"  claimant:  {m['claimant']}")
        print(f"  rating:    {m['rating']}")
        print(f"  publisher: {m['publisher']}")
        print(f"  url:       {m['url']}")