from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies import get_current_user, oauth2_scheme
from app.dtos.user_dto import Token, UserCreate, UserResponse, UserUpdate
from app.models.users import UserModel
from app.services import auth_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    """
    현재 로그인된 사용자 정보를 반환합니다.
    :param current_user: get_current_user 의존성 주입을 통해 얻은 현재 사용자 정보
    :return: 현재 사용자 정보
    """
    return current_user


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(user_create: UserCreate):
    """
    새로운 사용자를 등록합니다.
    :param user_create: 사용자 생성에 필요한 정보
    :return: 생성된 사용자 정보
    """
    # 이메일 중복 확인
    existing_user = await UserModel.get_or_none(email=user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # 비밀번호 해싱
    hashed_password = auth_service.get_password_hash(user_create.password)

    # 사용자 생성
    user = await UserModel.create(
        email=user_create.email,
        password=hashed_password,
        nickname=user_create.nickname,
        name=user_create.name,
        phone_number=user_create.phone_number,
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token)
async def login_for_access_and_refresh_token(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    사용자 로그인 후 액세스 토큰과,
     리프레시 토큰을 발급합니다.
    액세스 토큰은 응답 바디에,
    리프레시 토큰은 HTTP Only 쿠키로 전달됩니다.
    :param response: FastAPI 응답 객체
    :param form_data: OAuth2 표준에 따른 이메일 비밀번호
    :return: 액세스 토큰 정보
    """
    # 사용자 인증
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 액세스 토큰 생성
    access_token = auth_service.create_token(
        data={"sub": user.email}, token_type="access"
    )
    # 리프레시 토큰 생성
    refresh_token = auth_service.create_token(
        data={"sub": user.email}, token_type="refresh"
    )

    # 리프레시 토큰을 HTTP Only 쿠키로 설정
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # JavaScript에서 접근 불가
        secure=True,  # HTTPS에서만 전송 (배포 시 필수)
        samesite="Lax",  # CSRF 공격 방지
        max_age=auth_service.REFRESH_TOKEN_EXPIRE_MINUTES * 60,  # 초 단위로 설정
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response, token: str = Depends(oauth2_scheme)):
    """
    사용자를 로그아웃하고 현재 액세스 토큰을
    블랙리스트에 추가하며 리프레시 토큰 쿠키를 삭제합니다.
    :param response: FastAPI 응답 객체 (쿠키 삭제를 위해 사용)
    :param token: 현재 사용 중인 액세스 토큰
    """
    # 현재 액세스 토큰을 블랙리스트에 추가하여 무효화
    await auth_service.add_token_to_blacklist(token)
    # 리프레시 토큰 쿠키 삭제
    response.delete_cookie(key="refresh_token")
    return


@router.post("/refresh_token", response_model=Token)
async def refresh_token(request: Request, response: Response):
    """
    리프레시 토큰을 사용하여 새로운 액세스 토큰과 리프레시 토큰을 재발급합니다.
    :param request: FastAPI 요청 객체 (쿠키에서 리프레시 토큰을 읽기 위해 사용)
    :param response: FastAPI 응답 객체 (새 리프레시 토큰 쿠키 설정을 위해 사용)
    :return: 새로운 액세스 토큰 정보
    """
    # 요청 쿠키에서 리프레시 토큰 가져오기
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found"
        )

    # 리프레시 토큰 디코딩 및 유효성 검증
    payload = auth_service.decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
        )

    # 사용자 정보 조회
    user = await auth_service.get_user(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    # 새로운 액세스 토큰과 리프레시 토큰 생성
    new_access_token = auth_service.create_token(
        data={"sub": user.email}, token_type="access"
    )
    new_refresh_token = auth_service.create_token(
        data={"sub": user.email}, token_type="refresh"
    )

    # 새로운 리프레시 토큰을 HTTP Only 쿠키로 설정
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,  # HTTPS only
        samesite="Lax",
        max_age=auth_service.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )
    return {"access_token": new_access_token, "token_type": "bearer"}


@router.put("/me", response_model=UserResponse)
async def update_users_me(
    user_update: UserUpdate, current_user: UserResponse = Depends(get_current_user)
):
    updated_user = await auth_service.update_user(
        current_user.id, user_update.model_dump(exclude_unset=True)
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(updated_user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users_me(current_user: UserResponse = Depends(get_current_user)):
    """
    현재 로그인된 사용자를 삭제합니다.
    :param current_user: 현재 사용자 정보
    """
    deleted = await auth_service.delete_user(current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return
