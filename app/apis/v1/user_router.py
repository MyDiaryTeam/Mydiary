from fastapi import APIRouter, HTTPException
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_409_CONFLICT,
)

from app.dtos.user_dto import UserCreate, UserResponse
from app.models.users import UserModel
from app.services.auth_service import AuthService

router = APIRouter(prefix="/users", tags=["users"])


# 회원가입 로직
@router.post("/signup", status_code=HTTP_201_CREATED, response_model=UserResponse)
async def create_user(user_create: UserCreate):
    if await UserModel.filter(email=user_create.email).exists():
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail="Email already exists"
        )
    hashed_password = AuthService.get_password_hash(user_create.password)
    user = await UserModel.create(
        password=hashed_password, **user_create.model_dump(exclude={"password"})
    )
    return UserResponse.model_validate(user)
