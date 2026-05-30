"""Quick test of the Pollinations.ai free image generation API."""
import requests
from PIL import Image
from io import BytesIO
import urllib.parse

prompt = urllib.parse.quote("a simple red circle logo on white background, minimalist, vector art")
url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true"
print(f"Fetching: {url}")

r = requests.get(url, timeout=120)
print(f"Status: {r.status_code}")
ct = r.headers.get("content-type", "unknown")
print(f"Content-Type: {ct}")
print(f"Content length: {len(r.content)}")

if r.status_code == 200 and "image" in ct:
    img = Image.open(BytesIO(r.content))
    print(f"SUCCESS! Image size: {img.size}")
    img.save("test_output.png")
    print("Saved to test_output.png")
else:
    print(f"FAILED. Body preview: {r.text[:500]}")
