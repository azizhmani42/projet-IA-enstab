#!/usr/bin/env python3
"""Debug galerie API."""

import requests
import json

print("\n🔍 Vérification de la galerie API...\n")

resp = requests.get('http://localhost:8080/api/gallery')
data = resp.json()

print(f"Status: {resp.status_code}")
print(f"Total images: {data.get('total')}")
print(f"Images dans la réponse: {len(data.get('images', []))}")
print(f"\nPremières images:")

for i, img in enumerate(data.get('images', [])[:3]):
    print(f"\n{i+1}. {img.get('id')[:8]}...")
    print(f"   Filename: {img.get('filename')}")
    print(f"   URL: {img.get('url')}")
    print(f"   Prompt: {img.get('prompt')[:50]}...")
    print(f"   Created: {img.get('created_at')}")
