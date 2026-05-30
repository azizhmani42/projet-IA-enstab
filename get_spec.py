import requests
import re

r = requests.get('https://gen.pollinations.ai/')
print("Length:", len(r.text))

# Let's find any occurrences of json or yaml files, or urls
urls = re.findall(r'https?://[^\s"\'<>]+', r.text)
for u in urls:
    if 'openapi' in u or 'swagger' in u or 'json' in u or 'yaml' in u:
        print("Found matching URL:", u)

# Let's find spec-url or url in JS objects
matches = re.findall(r'"(spec-url|url|spec)"\s*:\s*"([^"]+)"', r.text)
print("Matches:", matches)
