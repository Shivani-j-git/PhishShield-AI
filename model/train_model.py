import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Load dataset
data = pd.read_csv("dataset/phishing_urls.csv")

# Features and label
X = data[["length", "dots", "https"]]
y = data["label"]

# Train model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)
model.fit(X, y)

# Save model
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/phishing_model.pkl")

print("✅ Phishing model trained successfully!")
