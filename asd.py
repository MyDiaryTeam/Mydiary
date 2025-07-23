import google.generativeai as genai

from app.config.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

for m in genai.list_models():
    if "generateContent" in m.supported_generation_methods:
        print(
            f"Model Name: {m.name}, Supported Methods: {m.supported_generation_methods}"
        )

## gemini api 사용 가능한 ver print
