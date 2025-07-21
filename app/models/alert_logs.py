from tortoise import fields, models


class AlertLogModel(models.Model):
    id = fields.IntField(pk=True, description="알림 로그 고유 ID")
    user_email = fields.ForeignKeyField("models.UserModel", related_name="alerts")
    alert_content = fields.TextField(description="알림 내용")
    created_at = fields.DatetimeField(auto_now_add=True, description="알림 생성일")

    class Meta:
        table = "alert_logs"
