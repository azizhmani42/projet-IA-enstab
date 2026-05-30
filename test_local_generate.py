import requests
import time

url = "http://localhost:8080/api/generate"
payload = {
    "prompt": "flying eagle clean vector logo icon",
    "style": "minimalist",
    "colors": "blue and white",
    "num_images": 1,
    "brand_name": "EAGLE EYE"
}

t0 = time.time()
try:
    print("Sending generation request to local Flask server...")
    r = requests.post(url, json=payload, timeout=90)
    duration = time.time() - t0
    print(f"Local Generate Status: {r.status_code}, Time: {duration:.2f}s")
    if r.status_code == 200:
        data = r.json()
        print("Response success:", data.get("success"))
        print("Message:", data.get("message"))
        images = data.get("images", [])
        print("Generated images count:", len(images))
        for img in images:
            print(f"  ID: {img.get('id')}")
            print(f"  URL: {img.get('url')}")
            print(f"  Brand Name: {img.get('brand_name')}")
            print(f"  Created At: {img.get('created_at')}")
    else:
        print(f"Error Response: {r.text}")
except Exception as e:
    print(f"Exception occurred: {e}")
