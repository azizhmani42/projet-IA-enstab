import requests
r = requests.get(
    'https://image.pollinations.ai/prompt/logo?width=512&height=512&model=flux&seed=42&nologo=true',
    timeout=30,
    headers={'User-Agent': 'Mozilla/5.0'}
)
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('content-type','?')}")
with open("api_response.txt", "wb") as f:
    f.write(r.content)
print(f"Response saved ({len(r.content)} bytes)")
