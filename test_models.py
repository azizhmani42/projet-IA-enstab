import requests
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://pollinations.ai/',
}

models = ["flux", "turbo", "unity", "sdxl", "default (no model parameter)"]

for model in models:
    if model == "default (no model parameter)":
        url = "https://image.pollinations.ai/prompt/logo%20icon?width=512&height=512&seed=42&nologo=true"
    else:
        url = f"https://image.pollinations.ai/prompt/logo%20icon?width=512&height=512&model={model}&seed=42&nologo=true"
    
    try:
        t0 = time.time()
        r = requests.get(url, timeout=30, headers=headers)
        dt = time.time() - t0
        print(f"Model: {model:30s} -> Status: {r.status_code}, Size: {len(r.content)} bytes, Time: {dt:.2f}s")
    except Exception as e:
        print(f"Model: {model:30s} -> Error: {e}")
