import base64
import urllib.parse
import sys
from pathlib import Path

def svg_to_base64_urlencoded(svg_path):
    svg_file = Path(svg_path)
    if not svg_file.exists():
        print(f"Error: File '{svg_path}' not found.")
        return

    with open(svg_file, "rb") as f:
        svg_data = f.read()

    base64_data = base64.b64encode(svg_data).decode("utf-8")
    url_encoded = urllib.parse.quote(base64_data)

    shields_logo_url = f"data:image/svg+xml;base64,{url_encoded}"

    print("Shields.io logo URL:\n")
    print(shields_logo_url)
    print("\nExample badge URL:\n")
    print(f"https://img.shields.io/badge/Label-Message-blue?logo={shields_logo_url}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python svg_to_shields_logo.py <your-logo.svg>")
    else:
        svg_to_base64_urlencoded(sys.argv[1])
