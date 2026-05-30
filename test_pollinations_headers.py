import requests
import time
import random

headers_options = [
    # Option 1: Empty headers (let requests handle it)
    None,
    # Option 2: Basic User-Agent only
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    },
    # Option 3: Full browser headers
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
]

prompt = "minimalist vector logo of a blue bird, white background"

for idx, headers in enumerate(headers_options):
    seed = random.randint(1, 100000)
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=512&height=512&seed={seed}&nologo=true"
    
    t0 = time.time()
    try:
        r = requests.get(url, headers=headers, timeout=15)
        duration = time.time() - t0
        print(f"Header Option {idx+1} -> Status: {r.status_code}, Length: {len(r.content)} bytes, Time: {duration:.2f}s")
        if r.status_code != 200:
            print(f"  Response: {r.text[:200]}")
    except Exception as e:
        print(f"Header Option {idx+1} -> Exception: {e}")
    time.sleep(1)
