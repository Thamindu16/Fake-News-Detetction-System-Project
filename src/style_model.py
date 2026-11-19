import argparse
import re
import sys
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

sys.stdout.reconfigure(encoding="utf-8")

MODEL_DIR = Path("models/distilroberta_v3_normalized")
MAX_TOKENS = 256   # the model only reads the first 256 tokens of any text

# Decisions taken from the validation experiments in the notebook:
# accuracy on articles cut to 80 / 40 / 18 words was 96.0% / 93.9% / 83.3%.
MIN_WORDS_RELIABLE = 80
MIN_WORDS_LIMITED = 40

# The model's probabilities sit almost always near 0 or 1, so they are never shown as percentages.
# They are only used to sort a text into three groups.
STRONG = 0.90

_device = "cuda" if torch.cuda.is_available() else "cpu"
_tokenizer = None
_model = None


def normalize(text):
    """Same function used to train the normalized model."""
    text = text.lower()
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _load():
    """Load the model once, the first time it is needed."""
    global _tokenizer, _model
    if _model is None:
        if not MODEL_DIR.exists():
            raise FileNotFoundError(f"Model folder not found: {MODEL_DIR}")
        _tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
        _model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR)).to(_device).eval()
    return _tokenizer, _model


def analyze_style(text):
    """Judge how much the writing style resembles fake-news sites or mainstream news sites."""
    words = len(text.split())
    if words < MIN_WORDS_LIMITED:
        return {"verdict": "too_short", "words": words, "reliability": None,
                "only_start_read": False, "p_fake": None}

    tokenizer, model = _load()
    cleaned = normalize(text)
    only_start_read = len(tokenizer(cleaned, truncation=False, verbose=False)["input_ids"]) > MAX_TOKENS
    inputs = tokenizer(cleaned, truncation=True, max_length=MAX_TOKENS, return_tensors="pt").to(_device)
    with torch.no_grad():
        p_fake = float(torch.softmax(model(**inputs).logits, dim=-1)[0, 1])

    if p_fake >= STRONG:
        verdict = "fake_site_style"
    elif p_fake <= 1 - STRONG:
        verdict = "news_site_style"
    else:
        verdict = "uncertain"

    return {
        "verdict": verdict,
        "words": words,
        "reliability": "normal" if words >= MIN_WORDS_RELIABLE else "limited",
        "only_start_read": only_start_read,   # True when the text was longer than the model can read
        "p_fake": round(p_fake, 4),           # for development only: never shown to users
    }


if __name__ == "__main__":
    # Usage: python src/style_model.py --file samples/article.txt
    #    or: python src/style_model.py "some text here"
    parser = argparse.ArgumentParser()
    parser.add_argument("text", nargs="*")
    parser.add_argument("--file")
    args = parser.parse_args()

    text = Path(args.file).read_text(encoding="utf-8") if args.file else " ".join(args.text)
    if not text.strip():
        sys.exit("Give some text, or use --file path/to/file.txt")

    for key, value in analyze_style(text).items():
        print(f"{key}: {value}")