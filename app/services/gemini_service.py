import google.generativeai as genai
from app.config.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

async def summarize_diary_content(content: str) -> str:
    """
    Gemini API를 사용하여 일기 내용을 2~3줄로 요약합니다.
    :param content: 요약할 일기 내용
    :return: 요약된 내용
    """
    model = genai.GenerativeModel('models/gemini-2.0-flash-thinking-exp-1219')
    prompt = f"""다음 일기 내용을 2~3줄로 요약해주세요:

{content}

요약:"""
    response = model.generate_content(prompt)
    return response.text
