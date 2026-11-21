import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, roc_auc_score

test = pd.read_csv("data/processed_v3/test.csv")
text = test["title"].fillna("") + ". " + test["text"].fillna("")
y = test["label"].values  # 0 = real, 1 = fake

vectorizer = joblib.load("models/baseline_v3_vectorizer.joblib")
model = joblib.load("models/baseline_v3_model.joblib")
X = vectorizer.transform(text)
pred = model.predict(X)
prob = model.predict_proba(X)[:, 1]

print("test articles:", len(y))
print(f"accuracy: {accuracy_score(y, pred):.4f} | macro F1: {f1_score(y, pred, average='macro'):.4f}"
      f" | ROC AUC: {roc_auc_score(y, prob):.4f}")
print("Confusion matrix (rows = true, columns = predicted; order: real, fake):")
print(confusion_matrix(y, pred))