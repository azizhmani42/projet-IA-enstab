import requests
import time

url = "https://image.pollinations.ai/prompt/minimalist%20logo%20of%20a%20bird?width=512&height=512&seed=999&nologo=true"
t0 = time.time()
try:
    r = requests.get(url, timeout=15)
    print(f"Status: {r.status_code}, Length: {len(r.content)} bytes, Time: {time.time()-t0:.2f}s")
except Exception as e:
    print(f"Exception: {e}")
