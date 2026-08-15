from flask import Flask, render_template, request
import sqlite3
from datetime import datetime
from urllib.parse import urlparse
import os

app = Flask(__name__)

DB = "database/history.db"

# ---------------- DATABASE ----------------
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

# ---------------- DETECTION ----------------
def detect_phishing(url):
    score = 0
    reasons = []

    if len(url) > 60:
        score += 20
        reasons.append("Long URL")

    if "@" in url:
        score += 25
        reasons.append("@ symbol detected")

    if "-" in urlparse(url).netloc:
        score += 15
        reasons.append("Hyphen in domain")

    suspicious = ["login", "verify", "secure", "update", "bank", "signin"]

    for word in suspicious:
        if word in url.lower():
            score += 10
            reasons.append(f"Contains '{word}'")

    if url.startswith("http://"):
        score += 20
        reasons.append("Not using HTTPS")

    if score >= 50:
        result = "Phishing"
    else:
        result = "Safe"

    return result, min(score, 100), reasons

# ---------------- ROUTES ----------------
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

    result, score, reasons = detect_phishing(url)

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO scans(url,result,score,time) VALUES (?,?,?,?)",
        (url, result, score, datetime.now().strftime("%d-%m-%Y %H:%M"))
    )
    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        url=url,
        result=result,
        score=score,
        reasons=reasons
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=True)-
