# TruthLens: writing-style analysis and fact-check lookup for news text

TruthLens takes a piece of text (a news article, a post or a single claim) and returns three separate things:

1. **A writing-style verdict**: does the text read like articles from fake-news websites or from ordinary news websites, or is the model unsure?
2. **Related fact-checks**: ratings that professional fact-checkers have already published about similar claims, found through the Google Fact Check Tools API.
3. **Warnings** that explain what the result does and does not mean.

TruthLens **does not decide whether a text is true**, and it deliberately shows no "real/fake" label and no confidence percentage. The reasons are in [Key findings](#key-findings).

**Live demo (saved example results):** https://thamindu16.github.io/Fake-News-Detetction-System-Project/

The demo page shows results recorded from the real system, because the full system (two language models) needs about 0.9 GB of RAM and was not hosted. It runs locally in a few steps, see [Run it locally](#run-it-locally).

## Key findings

This is the second version of the project. The first version reported high accuracy but had never been tested properly. Version 2 starts from the data and measures everything.

**1. The public datasets have problems that inflate accuracy.**

| Problem found | Evidence |
|---|---|
| Labels in the WELFake file are inverted (`0` = real, `1` = fake, the opposite of its description) | 38,644 articles appear in both WELFake and ISOT; the two datasets agreed on **0** of them |
| Source markers leak the label | "Reuters" appears in 99.8% of real ISOT articles; it was removed |
| ISOT is contained in WELFake | all 38,646 unique ISOT articles also appear in WELFake, so one cannot be used to test the other |
| Duplicates, empty and very short articles | 72,134 articles reduced to 61,148 |

After removing URLs, tweet leftovers, publisher names, dates and formatting residue, a TF-IDF model's accuracy fell from 95.3% to 93.1%, which measures how much came from shortcuts.

**2. Good scores on the same dataset did not carry over to an independent one.**

All models were also tested on [LIAR](https://arxiv.org/abs/1705.00648): 8,072 short political statements labelled by PolitiFact editors (statements rated *pants-fire* or *false* count as fake, *mostly-true* or *true* as real; the two middle ratings were dropped).

| Model | Held-out test accuracy (6,115 articles) | Test ROC AUC | LIAR accuracy | LIAR ROC AUC |
|---|---|---|---|---|
| Always answer "real" | n/a | n/a | 56.06% | n/a |
| TF-IDF + Logistic Regression | 93.08% | 0.981 | 49.23% | 0.531 |
| DistilRoBERTa, raw text | 99.66% | about 1.00 | 56.73% | 0.532 |
| DistilRoBERTa, normalized text (used in the app) | 96.70% | 0.995 | 46.42% | 0.547 |

On LIAR all three models are close to chance (ROC AUC 0.5 means no skill). The models learned **how fake-news sites write**, not **whether a statement is true**. LIAR statements are also much shorter (about 18 words) than the training articles, so part of the drop comes from that mismatch; shortening the validation articles to 18 words dropped accuracy to 83%, so length alone does not explain it.

**3. Model confidence cannot be trusted as a probability.**

On LIAR, 71% of the statements were classified with at least 99% confidence, yet only 47% of those were correct. On the validation set, 98.6% of articles received at least 90% confidence, so the score barely separates easy from hard cases. The app therefore never shows a percentage.

**4. Formatting cues matter.** The raw-text model fell from 99.6% to 74.5% when case and punctuation were removed from validation articles. A second model trained on normalized text reached 97.2% on validation and is the one the app uses.

## How it works

```
text ──► style model (DistilRoBERTa, normalized text) ──► verdict: fake-site style / news-site style / not sure
  │          rules: under 40 words = no verdict, 40-79 words = "less reliable" warning,
  │                 only the first 256 tokens are read
  │
  └────► keywords (up to 3 per sentence) ──► Google Fact Check Tools API
              └─► sentence-embedding similarity (all-MiniLM-L6-v2) between your text and each matched claim
                    ≥ 0.80  "this claim has been fact-checked"
                    0.50-0.80  "fact-checks on similar topics" (different claims on the same topic)
                    < 0.50  not shown
```

Design decisions that follow from the findings:

- A fact-check rating applies to the **matched claim shown next to it**, never to the user's text; a matched claim can even say the opposite of the input. The interface always shows both together.
- "No fact-check found" is shown as "not checked", never as "true". In a test with 50 LIAR statements, a related fact-check was found for 40% and a close match (similarity of 0.8 or more) for only 4%, so most texts will have no result.
- The API caches lookups for 24 hours and allows 10 requests per minute per client.

## Project structure

```
src/        data scripts, training scripts, evaluation scripts, FastAPI backend (api.py)
notebooks/  Google Colab notebook: DistilRoBERTa fine-tuning, robustness checks, LIAR and test evaluation
docs/       static web page (index.html) and saved example results (demo-data.js); served by GitHub Pages
```

## Run it locally

Requirements: Python 3.11 or newer. The style model is not stored in this repository because of its size.

```bash
git clone https://github.com/Thamindu16/Fake-News-Detetction-System-Project.git
cd Fake-News-Detetction-System-Project
python -m venv venv
venv\Scripts\activate            # on Linux or macOS: source venv/bin/activate
pip install -r requirements.txt
```

**Reproduce the data and the baseline** (in this order):

```bash
python src/download_data.py       # WELFake
python src/clean_data.py          # clean, de-duplicate, split 80/10/10
python src/scrub_text.py          # remove leakage markers (writes data/processed_v3)
python src/train_baseline.py --data data/processed_v3 --name baseline_v3
```

The ISOT files used for the data audit (`explore_data.py`, `verify_labels.py`) come from the `v1-legacy` branch: `git restore --source=v1-legacy -- data`.

**Train the transformer:** run `notebooks/fake_news_distilroberta.ipynb` on Google Colab (free T4 GPU) and save the normalized model into `models/distilroberta_v3_normalized/`.

**Start the app:**

1. Create a Fact Check Tools API key in Google Cloud and put it in a file named `.env`: `FACTCHECK_API_KEY=your_key`
2. Start the backend: `uvicorn api:app --app-dir src --port 8765`
3. Serve the page: `python -m http.server 5500 --directory docs`
4. Open http://localhost:5500. The status pill should read "Server connected".

Without the backend the page runs in demo mode and offers the saved examples.

## Limitations

- The style model was trained on English political news from 2015 to 2018. It may misjudge other topics, other languages or other regions.
- It describes writing style. A calm, professional-looking text containing a false claim can be judged "news-site style", and an excited text about a true event can be judged "fake-site style".
- The fact-check lookup depends on the Google Fact Check Tools API and on someone having already checked a similar claim.
- The validation and test scores come from the same sources as the training data; the independent LIAR results are the more realistic indication.

## Version history

The first version (TF-IDF + Logistic Regression, deployed on Render) is preserved in the `v1-legacy` branch.

## Data and tools

- WELFake dataset: https://zenodo.org/record/4561253 (loaded from https://huggingface.co/datasets/davanstrien/WELFake)
- ISOT Fake News Dataset, University of Victoria
- LIAR dataset: Wang (2017), "Liar, Liar Pants on Fire", https://arxiv.org/abs/1705.00648
- Google Fact Check Tools API; fact-check ratings shown by the app are published by their respective organisations, which are named next to each result
- Hugging Face Transformers (`distilroberta-base`), Sentence-Transformers (`all-MiniLM-L6-v2`), scikit-learn, FastAPI

## Author

H.M. Thamindu Kavinda Dinujaya, BSc (Hons) Data Science, Sri Lanka Technology Campus.
[GitHub](https://github.com/Thamindu16) · [LinkedIn](https://www.linkedin.com/in/thamindu-kavinda)
