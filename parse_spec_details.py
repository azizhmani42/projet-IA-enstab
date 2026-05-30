import requests
import json

r = requests.get('https://gen.pollinations.ai/docs/open-api/generate-schema')
data = r.json()

print("Servers:", data.get('servers'))

image_prompt_path = data.get('paths', {}).get('/image/{prompt}', {})
print("\n--- /image/{prompt} ---")
print(json.dumps(image_prompt_path, indent=2)[:1000])

images_gen_path = data.get('paths', {}).get('/v1/images/generations', {})
print("\n--- /v1/images/generations ---")
print(json.dumps(images_gen_path, indent=2)[:1000])
