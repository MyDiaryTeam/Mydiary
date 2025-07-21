from tortoise import fields, models


class UserModel(models.Model):
    email = fields.CharField(
        max_length=255, pk=True, description="사용자 이메일 (로그인 시 사용)"
    )
    password = fields.CharField(max_length=255, description="비밀번호")
    nickname = fields.CharField(max_length=100, description="닉네임")
    name = fields.CharField(max_length=100, description="이름")
    phone_number = fields.CharField(max_length=20, description="전화번호")
    last_login = fields.DatetimeField(null=True, description="마지막 로그인 시간")
    is_staff = fields.BooleanField(default=False, description="스태프 여부")
    is_admin = fields.BooleanField(default=False, description="관리자 여부")
    is_active = fields.BooleanField(default=True, description="계정 활성화 여부")
    created_at = fields.DatetimeField(auto_now_add=True, description="생성일")
    updated_at = fields.DatetimeField(auto_now=True, description="수정일")

    class Meta:
        table = "users"

    def __str__(self):
        return self.email
