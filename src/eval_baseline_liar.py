import joblib
import pandas as pd
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, roc_auc_score)

df = pd.read_csv("data/processed_liar/liar_eval.csv")
y = df["label"]  # 0 = real, 1 = fake

vectorizer = joblib.load("models/baseline_v3_vectorizer.joblib")
model = joblib.load("models/baseline_v3_model.joblib")

X = vectorizer.transform(df["statement"])
pred = model.predict(X)
prob_fake = model.predict_proba(X)[:, 1]  # probability that each statement is fake

print("statements evaluated:", len(df))
print(f"accuracy: {accuracy_score(y, pred):.4f}")
print(f"macro F1: {f1_score(y, pred, average='macro'):.4f}")
print(f"ROC AUC:  {roc_auc_score(y, prob_fake):.4f}  (0.5 = no skill, 1.0 = perfect)")

# Reference: what a model that always predicts the most common class would score.
# A real model must beat this to be worth anything.
majority = y.value_counts().idxmax()
print(f"always predicting '{['real', 'fake'][majority]}' would score: {(y == majority).mean():.4f}")
print(f"share of statements the model labelled fake: {pred.mean():.2%}")
print(f"share that are truly fake:                   {y.mean():.2%}")

print("\n", classification_report(y, pred, target_names=["real", "fake"], digits=4))
print("Confusion matrix (rows = true, columns = predicted; order: real, fake):")
print(confusion_matrix(y, pred))