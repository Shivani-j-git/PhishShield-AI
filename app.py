from flask import Flask, render_template, request
import sqlite3
import os
import joblib
from datetime import datetime
from utils.url_features import extract_features

app = Flask(__name__)

DB = "database/history.db"
MODEL_PATH = "model/phishing_model.pkl"

# ---------- Database ----------
def init_db():
    os.makedirs("database", exist_ok=True)

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS scans(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        result TEXT,
        score INTEGER,
        time TEXT
    )
    """)

    conn.commit()
    conn.close()

# ---------- Load ML Model ----------
model = None
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)

# ---------- Prediction ----------
def predict_url(url):
    features = [extract_features(url)]

    if model:
        pred = model.predict(features)[0]
        prob = model.predict_proba(features)[0][1]
        score = int(prob * 100)
    else:
        pred = 1 if len(url) > 60 else 0
        score = 70 if pred else 20

    result = "Phishing" if pred else "Safe"
    return result, score

# ---------- Routes ----------
@app.route("/")
def home():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT * FROM scans ORDER BY id DESC LIMIT 5")
    history = cur.fetchall()

    conn.close()

    return render_template("index.html", history=history)


@app.route("/scan", methods=["POST"])
def scan():

    url = request.form["url"]

    result, score = predict_url(url)

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO scans(url,result,score,time) VALUES (?,?,?,?)",
        (
            url,
            result,
            score,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        )
    )

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        url=url,
        result=result,
        score=score
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
