import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from threading import Lock

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

from claim_matcher import match_claims                       # loads the similarity model when imported
from style_model import _load as load_style_model, analyze_style

MAX_CHARS = 20_000      # refuse very long inputs
CLOSE_MATCH = 0.80      # "this claim has been fact-checked"
RELATED_MATCH = 0.50    # "fact-checks about a similar topic"; weaker matches are dropped

RATE_LIMIT = 10         # requests allowed per client ...
RATE_WINDOW = 60        # ... in this many seconds

# Websites allowed to call this API from a browser. Add the real frontend address later.
ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "https://thamindu16.github.io",
]

STYLE_MESSAGES = {
    "fake_site_style": "The writing style closely resembles articles from fake-news websites in the training data.",
    "news_site_style": "The writing style closely resembles articles from ordinary news websites in the training data.",
    "uncertain": "The model is not sure which kind of website this writing style resembles.",
    "too_short": "This text is too short for a style analysis (at least 40 words are needed).",
}

_hits = defaultdict(deque)   # client address -> times of its recent requests
_hits_lock = Lock()


def is_rate_limited(client):
    """Allow RATE_LIMIT requests per client in any RATE_WINDOW seconds."""
    now = time.time()
    with _hits_lock:
        if len(_hits) > 5000:   # forget quiet clients, so memory cannot grow forever
            for key in [k for k, q in _hits.items() if not q or now - q[-1] > RATE_WINDOW]:
                del _hits[key]
        hits = _hits[client]
        while hits and now - hits[0] > RATE_WINDOW:
            hits.popleft()
        if len(hits) >= RATE_LIMIT:
            return True
        hits.append(now)
        return False


@asynccontextmanager
async def lifespan(app):
    load_style_model()   # load the model once at start-up, so the first request is not slow
    yield


app = FastAPI(title="TruthLens API", version="2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class AnalyzeRequest(BaseModel):
    text: str = Field(..., max_length=MAX_CHARS)

    @field_validator("text")
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError("text must not be empty")
        return value


def clean_rating(rating):
    """Return the rating text, or None when it is missing or meaningless (for example just '1')."""
    if not rating:
        return None
    rating = rating.strip()
    if len(rating) < 3 or rating.isdigit():
        return None
    return rating[:300]


def format_match(match):
    return {
        "matched_claim": match["claim"],     # the claim the fact-checkers examined
        "rating": clean_rating(match["rating"]),
        "publisher": match["publisher"],
        "url": match["url"],
        "review_date": match["review_date"],
        "your_text_part": match["sentence"],  # which part of the input led to this match
    }


def build_fact_checks(text):
    result = match_claims(text)
    close, related = [], []
    for match in result["matches"]:              # already sorted, best match first
        if match["similarity"] >= CLOSE_MATCH:
            close.append(format_match(match))
        elif match["similarity"] >= RELATED_MATCH:
            related.append(format_match(match))

    if close or related:
        status = "partial" if result["failed_lookups"] else "ok"
    elif result["failed_lookups"] and not result["matches"]:
        status = "unavailable"                   # the lookup service failed, so we know nothing
    else:
        status = "none_found"
    return {"status": status, "close_matches": close, "related": related}


def build_warnings(style, fact_checks):
    warnings = [{
        "code": "style_only",
        "message": "The style result describes how the text is written. It says nothing about whether the content is true.",
    }]
    if style["verdict"] == "too_short":
        warnings.append({"code": "too_short", "message": STYLE_MESSAGES["too_short"]})
    elif style["reliability"] == "limited":
        warnings.append({"code": "short_text",
                         "message": "The text has fewer than 80 words, so the style result is less reliable."})
    if style["only_start_read"]:
        warnings.append({"code": "long_text",
                         "message": "The text is long: only its first part was read by the style model."})

    status = fact_checks["status"]
    if status == "none_found":
        warnings.append({"code": "no_fact_checks",
                         "message": "No related fact-checks were found. This does not mean the content is true; it may simply not have been checked."})
    elif status == "unavailable":
        warnings.append({"code": "fact_check_unavailable",
                         "message": "The fact-check lookup failed, so no result is shown. Please try again later."})
    elif status == "partial":
        warnings.append({"code": "fact_check_partial",
                         "message": "Part of the fact-check lookup failed, so some results may be missing."})
    if fact_checks["close_matches"] or fact_checks["related"]:
        warnings.append({"code": "match_meaning",
                         "message": "Each rating applies to the matched claim shown next to it, not to your text. A matched claim can even say the opposite of your text."})
    return warnings


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(body: AnalyzeRequest, http: Request):
    # When deployed behind a proxy, the real visitor address arrives in the X-Forwarded-For header.
    # That is handled at deploy time; for now the direct connection address is used.
    client = http.client.host if http.client else "unknown"
    if is_rate_limited(client):
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please wait a minute and try again.",
            headers={"Retry-After": str(RATE_WINDOW)},
        )

    text = body.text.strip()
    try:
        style = analyze_style(text)
    except FileNotFoundError:
        raise HTTPException(status_code=503, detail="The style model is not available on this server.")

    fact_checks = build_fact_checks(text)
    return {
        "style": {
            "verdict": style["verdict"],
            "message": STYLE_MESSAGES[style["verdict"]],
            "words": style["words"],
            "reliability": style["reliability"],
            "only_start_read": style["only_start_read"],
        },   # the raw probability is deliberately not included
        "fact_checks": fact_checks,
        "warnings": build_warnings(style, fact_checks),
    }