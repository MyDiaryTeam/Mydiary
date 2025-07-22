from typing import TYPE_CHECKING

from tortoise import fields, models

from app.models.diaries import EmotionType

if TYPE_CHECKING:
    from app.models.diaries import DiaryModel


class EmotionKeywordModel(models.Model):
    id = fields.IntField(pk=True, description="감정 키워드 고유 ID")
    diary: fields.ForeignKeyRelation["DiaryModel"] = fields.ForeignKeyField(
        "models.DiaryModel", related_name="emotion_keywords", on_delete=fields.CASCADE
    )
    word = fields.CharField(max_length=100, description="키워드")
    emotion = fields.CharEnumField(EmotionType, description="감정 분류")

    class Meta:
        table = "emotion_keywords"
        app = "models"

    def __str__(self):
        return f"{self.word} ({self.emotion.value})"
