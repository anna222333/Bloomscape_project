import vertexai
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel

# Путь к твоему только что созданному ключу
KEY_PATH = "bloom-key.json"

# Загружаем учетные данные из файла
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)

# Инициализируем Vertex AI с явными правами
vertexai.init(
    project="positive-leaf-462823-h2", 
    location="us-central1", 
    credentials=credentials
)

model = GenerativeModel("gemini-3-pro-preview")

try:
    response = model.generate_content("Привет! На этот раз ты меня слышишь?")
    print("\n✅ ПОБЕДА! Ответ модели:")
    print(response.text)
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
