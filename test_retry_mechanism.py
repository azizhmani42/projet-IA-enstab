import requests
import time
import random

url = "https://image.pollinations.ai/prompt/minimalist%20logo%20of%20a%20bird?width=512&height=512&seed=8888&model=flux&nologo=true"

# Let's try up to 5 times with a 2-second wait between attempts
for attempt in range(5):
    t0 = time.time()
    try:
        r = requests.get(url, timeout=15)
        duration = time.time() - t0
        print(f"Attempt {attempt+1} -> Status: {r.status_code}, Length: {len(r.content)} bytes, Time: {duration:.2f}s")
        if r.status_code == 200:
            print("Success!")
            break
        else:
            print(f"  Response: {r.text[:200]}")
    except Exception as e:
        print(f"  Exception: {e}")
    time.sleep(2)
