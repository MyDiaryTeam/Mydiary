from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_409_CONFLICT,
)

from app.config.config import settings
from app.dtos.user_dto import Token, UserCreate, UserResponse, UserUpdate
from app.models.users import UserModel
from app.services.auth_service import AuthService, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


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


# 로그인 로직
@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserModel.get_or_none(email=form_data.username)
    if not user or not AuthService.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="잘못된 아이디 혹은 비번입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# 로그아웃 로직
@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(token: str = Depends(oauth2_scheme)):
    AuthService.add_token_to_blacklist(token)
    return {"message": "Successfully logged out"}


# 보호된 엔드포인트 예시 (로그인된 사용자만 접근 가능)
@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_users_me(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
):
    user = await UserModel.get(id=current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    await user.save()
    return UserResponse.model_validate(user)


@router.delete("/me", response_model=UserResponse)
async def delete_users_me(current_user: UserResponse = Depends(get_current_user)):
    user = await UserModel.get(id=current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()
    return UserResponse.model_validate(user)
