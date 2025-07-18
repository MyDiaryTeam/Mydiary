from tortoise import fields, models
from enum import Enum


class Mood(str, Enum):
    HAPPY = "happy"
    SAD = "sad"
    NEUTRAL = "neutral"
    ANGRY = "angry"


class Diary(models.Model):
    diary_id = fields.IntField(pk=True, description="일기 고유 ID")
    user_email = fields.ForeignKeyField(
        "models.User", related_name="diaries", description="사용자 이메일"
    )
    title = fields.CharField(max_length=255, description="제목")
    content = fields.TextField(description="내용")
    emotion_summary = fields.JSONField(null=True, description="감정 요약 (AI 분석 결과)")
    mood = fields.CharEnumField(Mood, description="기분")
    created_at = fields.DatetimeField(auto_now_add=True, description="작성일자")
    updated_at = fields.DatetimeField(auto_now=True, description="수정일자")

    class Meta:
        table = "diaries"

    def __str__(self):
        return self.title
