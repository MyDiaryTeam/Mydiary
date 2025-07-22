from enum import Enum
from typing import TYPE_CHECKING

from tortoise import fields, models

if TYPE_CHECKING:
    from app.models.users import UserModel


class TimePeriodTypeModel(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class EmotionStatModel(models.Model):
    user_email: fields.ForeignKeyRelation["UserModel"] = fields.ForeignKeyField(
        "models.UserModel", related_name="emotion_stats"
    )
    time_period_type = fields.CharEnumField(TimePeriodTypeModel)
    time_period_value = fields.CharField(max_length=50)
    emotion_type = fields.CharField(max_length=50)
    frequency = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "emotion_stats"
        unique_together = (
            "user_email",
            "time_period_type",
            "time_period_value",
            "emotion_type",
        )
