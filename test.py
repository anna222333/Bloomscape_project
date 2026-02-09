from google import genai

client = genai.Client(api_key="AIzaSyDWXjNwZlv7k2B2WmxAdI9aCVFeDiF3blg", http_options={'api_version': 'v1alpha'})

try:
    response = client.models.generate_content(
        model='gemini-3-pro-preview', # Или попробуй 'gemini-3.0-pro-preview'
        contents='Привет, ты Gemini 3?'
    )
    print("✅ УСПЕХ!")
    print(response.text)
except Exception as e:
    print(f"❌ Ошибка: {e}")
