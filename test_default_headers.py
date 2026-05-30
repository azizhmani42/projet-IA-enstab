import requests
import time
import random

models = ["flux", "turbo", "sdxl", "default"]
prompt = "minimalist vector logo of a blue bird, white background"

for model in models:
    seed = random.randint(1, 100000)
    if model == "default":
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&seed={seed}&nologo=true"
    else:
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&model={model}&seed={seed}&nologo=true"
    
    t0 = time.time()
    try:
        # Absolutely NO custom headers
        r = requests.get(url, timeout=20)
        duration = time.time() - t0
        print(f"Model: {model} -> Status: {r.status_code}, Length: {len(r.content)} bytes, Time: {duration:.2f}s")
        if r.status_code != 200:
            print(f"  Response: {r.text[:200]}")
    except Exception as e:
        print(f"Model: {model} -> Exception: {e}")
    time.sleep(1)
