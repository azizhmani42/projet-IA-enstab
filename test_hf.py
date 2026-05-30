import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")
HF_MODEL_ID = "black-forest-labs/FLUX.1-schnell"

print(f"Token: {HF_API_TOKEN[:10]}...")

headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL_ID}"

prompt = "minimalist vector logo of a blue bird, white background, high quality, vector art"

payload = {
    "inputs": prompt,
    "parameters": {
        "width": 512,
        "height": 512,
    }
}

t0 = time.time()
try:
    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    duration = time.time() - t0
    print(f"HF Inference Status: {response.status_code}, Time: {duration:.2f}s")
    if response.status_code == 200:
        content_type = response.headers.get("content-type", "")
        print(f"  Success! Size: {len(response.content)} bytes, Type: {content_type}")
        with open("hf_test_output.png", "wb") as f:
            f.write(response.content)
        print("  Saved to hf_test_output.png")
    else:
        print(f"  Error: {response.text[:400]}")
except Exception as e:
    print(f"Exception: {e}")
