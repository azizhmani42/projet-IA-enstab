import requests
import time
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://pollinations.ai/',
}

# Test different models with a new seed every time to avoid cache
prompt = "minimalist vector logo of a blue bird, white background"
models = ["flux", "turbo", "sdxl", "default"]

for model in models:
    seed = random.randint(1, 100000)
    if model == "default":
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&seed={seed}&nologo=true"
    else:
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&model={model}&seed={seed}&nologo=true"
    
    t0 = time.time()
    try:
        r = requests.get(url, headers=headers, timeout=15)
        duration = time.time() - t0
        print(f"Model: {model} -> Status: {r.status_code}, Length: {len(r.content)} bytes, Time: {duration:.2f}s")
        if r.status_code != 200:
            print(f"  Response: {r.text[:200]}")
    except Exception as e:
        print(f"Model: {model} -> Exception: {e}")
    time.sleep(1) # sleep a bit between tests
