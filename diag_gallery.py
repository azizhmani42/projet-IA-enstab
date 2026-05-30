#!/usr/bin/env python3
"""Diag: Vérifier la galerie."""

import requests
import json

resp = requests.get('http://localhost:8080/api/gallery')
data = resp.json()

print(f"✅ Status: {resp.status_code}")
print(f"✅ Response has 'success': {'success' in data}")
print(f"✅ Response has 'images': {'images' in data}")
print(f"✅ Response has 'total': {'total' in data}")
print(f"✅ Number of images: {len(data.get('images', []))}")

# Vérifier la structure de la première image
if data.get('images'):
    img = data['images'][0]
    print(f"\n📸 First image structure:")
    print(f"   - id: {img.get('id')}")
    print(f"   - filename: {img.get('filename')}")
    print(f"   - url: {img.get('url')}")
    print(f"   - prompt: {img.get('prompt')[:50]}...")
    print(f"\n   Full first image:")
    print(json.dumps(img, indent=2))
