from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.models.diaries import MoodModel


class DiaryCreateRequest(BaseModel):  # 일기 작성
    title: str
    content: str
    emotion_summary: None
    mood: MoodModel


class DiaryUpdateRequest(BaseModel):  # 일기 수정
    title: str | None = None
    content: str | None = None
    emotion_summary: None
    mood: MoodModel


class DiaryResponse(BaseModel):
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
