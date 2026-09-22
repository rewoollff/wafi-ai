import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "training_data.csv"
MODEL_DIR = BASE_DIR / "models"

MODEL_DIR.mkdir(exist_ok=True)


texts = []
labels = []

with DATA_PATH.open("r", encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        text = (
            f"{row['ticket_text']} "
            f"affected users {row['affected_users']} "
            f"category {row['category']}"
        )

        texts.append(text)
        labels.append(f"{row['team']}|{row['urgency']}")


model = Pipeline(
    [
        ("vectorizer", TfidfVectorizer()),
        ("classifier", LogisticRegression(max_iter=1000)),
    ]
)

model.fit(texts, labels)

joblib.dump(model, MODEL_DIR / "wafi_model.joblib")

print("Model trained successfully.")
print(f"Saved to: {MODEL_DIR / 'wafi_model.joblib'}")