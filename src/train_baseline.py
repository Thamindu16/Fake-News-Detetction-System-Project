from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

DATA = Path("data/processed")
MODELS = Path("models")
MODELS.mkdir(exist_ok=True)

# Label meaning: 0 = real, 1 = fake
train = pd.read_csv(DATA / "train.csv")
val = pd.read_csv(DATA / "val.csv")  # the test set is NOT touched here


def combine(df):
    """Join title and body into one text per article."""
    return df["title"].fillna("") + ". " + df["text"].fillna("")


X_train, y_train = combine(train), train["label"]
X_val, y_val = combine(val), val["label"]

# 1. Turn text into numbers with TF-IDF
vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",   # ignore very common words like "the", "and"
    ngram_range=(1, 2),     # use single words and pairs of words
    min_df=5,               # ignore words that appear in fewer than 5 articles
    max_df=0.8,             # ignore words that appear in more than 80% of articles
    max_features=200_000,   # keep at most 200k features
    sublinear_tf=True,      # dampen the effect of very frequent words
)
X_train_vec = vectorizer.fit_transform(X_train)  # learn vocabulary from train only
X_val_vec = vectorizer.transform(X_val)          # reuse the same vocabulary

# 2. Train the classifier
model = LogisticRegression(max_iter=1000, C=1.0)
model.fit(X_train_vec, y_train)

# 3. Evaluate on the validation set
pred = model.predict(X_val_vec)
print("\n=== Validation results ===")
print(classification_report(y_val, pred, target_names=["real", "fake"], digits=4))
print("Confusion matrix (rows = true, columns = predicted; order: real, fake):")
print(confusion_matrix(y_val, pred))

# 4. Which words does the model rely on most? (leakage check)
names = np.array(vectorizer.get_feature_names_out())
order = np.argsort(model.coef_[0])
print("\nTop 30 words pushing towards REAL:")
print(", ".join(names[order[:30]]))
print("\nTop 30 words pushing towards FAKE:")
print(", ".join(names[order[-30:][::-1]]))

# 5. Save the model (the models/ folder is ignored by git)
joblib.dump(vectorizer, MODELS / "baseline_vectorizer.joblib")
joblib.dump(model, MODELS / "baseline_model.joblib")
print("\nSaved baseline model to models/")