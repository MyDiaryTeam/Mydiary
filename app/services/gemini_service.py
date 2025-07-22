import json

import google.generativeai as genai

from app.config.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


async def summarize_diary_content(content: str) -> str:
    """
    Gemini API를 사용하여 일기 내용을 2~3줄로 요약합니다.
    :param content: 요약할 일기 내용
    :return: 요약된 내용
    """
    model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp-1219")
    prompt = f"""다음 일기 내용을 2~3줄로 요약해주세요:

{content}

요약:"""
    response = model.generate_content(prompt)
    return response.text


async def analyze_diary_emotion(diary_id: int,
                                user_id: int,
                                content: str) -> dict:
    """
    Gemini API를 사용하여 일기 내용에서 감정 키워드를 추출합니다.
    :param diary_id: 일기 ID
    :param user_id: 사용자 ID
    :param content: 분석할 일기 내용
    :return: 감정 키워드가 포함된 JSON
    """
    model = genai.GenerativeModel(
        "models/gemini-2.0-flash-thinking-exp-1219"
    )
    prompt = f"""아래는 사용자가 작성한 일기 내용입니다.
각 문장에서 나타나는 감정 키워드를 추출해주세요.
감정 키워드는 '긍정', '부정', '중립'
세 가지 감정 분류로 나누어 주세요.

특히, 부정적 감정 키워드(예: 슬픔, 분노, 짜증, 우울 등)를 명확히
구분하여 별도로 표시해 주세요.

출력은 JSON 형태로 아래 예시처럼 작성해 주세요.

{{
  "diary_id": {diary_id},
  "user_id": {user_id},
  "keywords": [
    {{"word": "슬픔", "emotion": "부정"}},
    {{"word": "기쁨", "emotion": "긍정"}},
    {{"word": "짜증", "emotion": "부정"}}
  ]
}}

아래는 일기 내용입니다:

---
{content}
---

부정적 감정 키워드만 따로 추출하고 싶으니, 부정 키워드도 꼭 포함해 주세요.
"""
    response = model.generate_content(prompt)
    raw_text = response.text.strip()
    # 마크다운 코드 블록 제거
    if raw_text.startswith("```json") and raw_text.endswith("```"):
        raw_text = raw_text[len("```json\n") : -len("```")].strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # Gemini가 유효한 JSON을 반환하지 않을 경우를 대비한 처리
        print(f"Gemini API에서 유효하지 않은 JSON 응답: {response.text}")
        return {
            "error": "Failed to parse Gemini API response",
            "raw_response": response.text,
        }
