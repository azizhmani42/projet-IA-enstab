"""Quick test to find which Pollinations.ai endpoints work."""
import requests
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://pollinations.ai/',
}

tests = [
    ("flux 64px",  "https://image.pollinations.ai/prompt/logo%20icon?width=64&height=64&model=flux&seed=42&nologo=true&nofeed=true"),
    ("flux 512px", "https://image.pollinations.ai/prompt/logo%20icon?width=512&height=512&model=flux&seed=42&nologo=true&nofeed=true"),
    ("flux 768px", "https://image.pollinations.ai/prompt/logo%20icon?width=768&height=768&model=flux&seed=42&nologo=true&nofeed=true"),
    ("no model",   "https://image.pollinations.ai/prompt/logo%20icon?width=512&height=512&seed=42&nologo=true&nofeed=true"),
    ("turbo",      "https://image.pollinations.ai/prompt/logo%20icon?width=512&height=512&model=turbo&seed=42&nologo=true&nofeed=true"),
]

for name, url in tests:
    try:
        t0 = time.time()
        r = requests.get(url, timeout=60, headers=headers)
        dt = time.time() - t0
        ct = r.headers.get("content-type", "?")
        print(f"  {name:15s} -> HTTP {r.status_code}  {len(r.content):>8} bytes  {dt:.1f}s  type={ct}")
    except Exception as e:
        print(f"  {name:15s} -> ERROR: {e}")
    time.sleep(2)

print("\nDone!")
