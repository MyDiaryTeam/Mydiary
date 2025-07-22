from typing import TYPE_CHECKING

from tortoise import fields, models

if TYPE_CHECKING:
    from app.models.users import UserModel


class AlertLogModel(models.Model):
    id = fields.IntField(pk=True, description="알림 로그 고유 ID")
    user_email: fields.ForeignKeyRelation["UserModel"] = fields.ForeignKeyField(
        "models.UserModel", related_name="alerts"
    )
    alert_content = fields.TextField(description="알림 내용")
    created_at = fields.DatetimeField(auto_now_add=True, description="알림 생성일")

    class Meta:
        table = "alert_logs"
