import os
from anthropic import AnthropicVertex

# Настройки
PROJECT = "positive-leaf-462823-h2"
REGIONS = ["us-east5", "europe-west1", "us-central1"]
MODEL_ID = "claude-sonnet-4-5" # или "claude-opus-4-6"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

def diagnostic():
    print(f"--- Тест модели {MODEL_ID} ---")
    for region in REGIONS:
        print(f"Проверка региона {region}...", end=" ")
        try:
            client = AnthropicVertex(region=region, project_id=PROJECT)
            # Минимальный запрос
            response = client.messages.create(
                model=MODEL_ID,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            print("✅ ДОСТУПНО")
            return # Если нашли работающий регион, выходим
        except Exception as e:
            error_text = str(e)
            if "400" in error_text:
                print("❌ НЕДОСТУПНО (Модель не развернута в этом регионе)")
            elif "429" in error_text:
                print("⚠️ КВОТА ИСЧЕРПАНА (Нужно увеличить лимиты в консоли)")
            elif "403" in error_text:
                print("🚫 ОТКАЗАНО (Проверьте IAM права или включите Model Garden)")
            else:
                print(f"❓ ОШИБКА: {error_text}")

if __name__ == "__main__":
    diagnostic()
