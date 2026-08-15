from urllib.parse import urlparse

def extract_features(url):
    return [
        len(url),
        url.count("."),
        1 if url.startswith("https") else 0
    ]
