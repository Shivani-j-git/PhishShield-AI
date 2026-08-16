from flask import Flask, render_template, request
import sqlite3
import os
import joblib
from datetime import datetime
from utils.url_features import extract_features
from utils.email_scanner import scan_email
from utils.qr_scanner import generate_qr
from utils.pdf_report import create_report

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

    # Recent scans
    cur.execute("SELECT * FROM scans ORDER BY id DESC LIMIT 5")
    history = cur.fetchall()

    # Total scans
    cur.execute("SELECT COUNT(*) FROM scans")
    total = cur.fetchone()[0]

    # Safe count
    cur.execute("SELECT COUNT(*) FROM scans WHERE result='Safe'")
    safe = cur.fetchone()[0]

    # Phishing count
    cur.execute("SELECT COUNT(*) FROM scans WHERE result='Phishing'")
    phishing = cur.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        history=history,
        total=total,
        safe=safe,
        phishing=phishing
    )

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

    # Generate PDF report
    pdf = create_report(url, result, score)

    return render_template(
        "result.html",
        url=url,
        result=result,
        score=score,
        pdf=pdf
    )
@app.route("/email_scan", methods=["POST"])
def email_scan():
    email = request.form["email"]

    result, score, reasons = scan_email(email)

    return render_template(
        "email_result.html",
        email=email,
        result=result,
        score=score,
        reasons=reasons
    )
@app.route("/qr_generate", methods=["POST"])
def qr_generate():

    url = request.form["qr_url"]

    qr_path = generate_qr(url)

    return render_template(
        "qr_result.html",
        url=url,
        qr_image=qr_path
    )
@app.route("/analytics")
def analytics():

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM scans")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM scans WHERE result='Safe'")
    safe = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM scans WHERE result='Phishing'")
    phishing = cur.fetchone()[0]

    conn.close()

    return render_template(
        "analytics.html",
        total=total,
        safe=safe,
        phishing=phishing
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
