import requests
import time
import random

# We'll test the new gen.pollinations.ai endpoint!
prompt = "minimalist vector logo of a blue bird, white background"
models = ["flux", "nanobanana", "seedream", "gptimage", "zimage"]

for model in models:
    seed = random.randint(1, 100000)
    url = f"https://gen.pollinations.ai/image/{prompt}?width=512&height=512&seed={seed}&model={model}&nologo=true"
    
    t0 = time.time()
    try:
        r = requests.get(url, timeout=30)
        duration = time.time() - t0
        print(f"Model: {model} -> Status: {r.status_code}, Length: {len(r.content)} bytes, Time: {duration:.2f}s")
        if r.status_code != 200:
            print(f"  Response: {r.text[:200]}")
    except Exception as e:
        print(f"Model: {model} -> Exception: {e}")
    time.sleep(1)
