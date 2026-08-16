import qrcode
import os

def generate_qr(url):
    os.makedirs("static/qr", exist_ok=True)

    path = "static/qr/latest_qr.png"

    img = qrcode.make(url)
    img.save(path)

    return path
