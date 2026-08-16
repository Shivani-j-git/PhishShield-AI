from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

def create_report(url, result, score):
    os.makedirs("static/reports", exist_ok=True)

    filename = "static/reports/security_report.pdf"

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>PhishShield AI</b>", styles["Title"]))
    story.append(Paragraph("Cybersecurity Scan Report", styles["Heading2"]))
    story.append(Paragraph(f"<b>URL:</b> {url}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Result:</b> {result}", styles["BodyText"]))
    story.append(Paragraph(f"<b>Risk Score:</b> {score}%", styles["BodyText"]))

    doc.build(story)

    return filename
