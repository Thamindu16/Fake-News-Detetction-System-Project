import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix

# Command-line options: which data folder to use and what to call the saved model
parser = argparse.ArgumentParser()
parser.add_argument("--data", default="data/processed")
parser.add_argument("--name", default="baseline")
args = parser.parse_args()

DATA = Path(args.data)
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
    stop_words="english",
    ngram_range=(1, 2),
    min_df=5,
    max_df=0.8,
    max_features=200_000,
    sublinear_tf=True,
)
X_train_vec = vectorizer.fit_transform(X_train)  # learn vocabulary from train only
X_val_vec = vectorizer.transform(X_val)

# 2. Train the classifier
model = LogisticRegression(max_iter=1000, C=1.0)
model.fit(X_train_vec, y_train)

# 3. Evaluate on the validation set
pred = model.predict(X_val_vec)
print(f"\n=== Validation results ({args.data}) ===")
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
joblib.dump(vectorizer, MODELS / f"{args.name}_vectorizer.joblib")
joblib.dump(model, MODELS / f"{args.name}_model.joblib")
print(f"\nSaved model as models/{args.name}_*.joblib")