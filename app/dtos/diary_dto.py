from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.diaries import EmotionType, MoodModel


class EmotionKeywordResponse(BaseModel):
    word: str
    emotion: EmotionType

    model_config = {
        "from_attributes": True,
    }


class DiaryCreateRequest(BaseModel):
    title: str
    content: str
    mood: MoodModel


class DiaryUpdateRequest(BaseModel):  # 일기 수정
    title: str | None = None
    content: str | None = None
    mood: MoodModel


class DiaryResponse(BaseModel):
    id: int
    title: str
    content: str
    emotion: Optional[EmotionType] = None
    emotion_keywords: List[EmotionKeywordResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
