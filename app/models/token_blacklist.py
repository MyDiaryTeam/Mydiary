from tortoise import fields, models


class TokenBlacklist(models.Model):
    token = fields.CharField(max_length=500, unique=True, description="블랙리스트 토큰")
    created_at = fields.DatetimeField(auto_now_add=True, description="생성일")

    class Meta:
        table = "token_blacklist"

    def __str__(self):
        return self.token
