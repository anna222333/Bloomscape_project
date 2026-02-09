from google import genai
import os

# Твой API Key из AI Studio (AIza...)
api_key = "AIzaSyDWXjNwZlv7k2B2WmxAdI9aCVFeDiF3blg"
client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})

print("--- Доступные модели через API Key ---")
for m in client.models.list():
    print(f"ID: {m.name} | Display Name: {m.display_name}")
