#!/usr/bin/env python3
"""Test du endpoint de génération de logos."""

import requests
import json

url = 'http://localhost:8080/api/generate'
payload = {
    'prompt': 'modern tech logo with geometric shapes',
    'style': 'minimalist',
    'colors': 'blue and cyan',
    'num_images': 1,
    'brand_name': 'TechFlow'
}

print("\n📤 Envoi de la requête de génération...")
print(f"URL: {url}")
print(f"Payload:\n{json.dumps(payload, indent=2)}\n")

try:
    resp = requests.post(url, json=payload, timeout=60)
    print(f"Status: {resp.status_code}")
    result = resp.json()
    
    if result.get('success'):
        print("✅ Génération réussie !")
        print(f"Message: {result.get('message')}")
        if result.get('images'):
            for img in result['images']:
                print(f"\n  📸 Image générée:")
                print(f"    - ID: {img['id']}")
                print(f"    - URL: {img['url']}")
                print(f"    - Prompt: {img['prompt'][:60]}...")
    else:
        print("❌ Erreur:", result.get('message'))
        print(f"Détail: {result.get('detail', 'N/A')}")
except Exception as e:
    print(f"❌ Erreur de connexion: {e}")
