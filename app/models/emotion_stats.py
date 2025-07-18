from tortoise import fields, models
from enum import Enum


class TimePeriodType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class EmotionStat(models.Model):
    user_email = fields.ForeignKeyField("models.User", related_name="emotion_stats")
    time_period_type = fields.CharEnumField(TimePeriodType)
    time_period_value = fields.CharField(max_length=50)
    emotion_type = fields.CharField(max_length=50)
    frequency = fields.IntField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "emotion_stats"
        unique_together = ("user_email", "time_period_type", "time_period_value", "emotion_type")
