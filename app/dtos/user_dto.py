from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(..., max_length=255, description="사용자 이메일")
    password: str = Field(..., max_length=255, description="비밀번호")
    nickname: str = Field(..., max_length=100, description="닉네임")
    name: str = Field(..., max_length=100, description="이름")
    phone_number: str = Field(..., max_length=20, description="전화번호")


class UserUpdate(BaseModel):
    nickname: str | None = Field(None, max_length=100, description="닉네임")
    name: str | None = Field(None, max_length=100, description="이름")
    phone_number: str | None = Field(None, max_length=20, description="전화번호")


class UserResponse(BaseModel):
    id: int | None = Field(None, description="<UNK> <UNK> <UNK> <UNK> <UNK>")
    email: str = Field(..., max_length=255, description="사용자 이메일")
    nickname: str = Field(..., max_length=100, description="닉네임")
    name: str = Field(..., max_length=100, description="이름")
    phone_number: str = Field(..., max_length=20, description="전화번호")
    last_login: datetime | None = Field(None, description="마지막 로그인 시간")
    is_active: bool = Field(..., description="계정 활성화 여부")
    created_at: datetime = Field(..., description="생성일")
    updated_at: datetime = Field(..., description="수정일")

    model_config = {
        "from_attributes": True,
    }

class Token(BaseModel):
    access_token: str
    token_type: str


class UserInDB(UserResponse):
    password: str
