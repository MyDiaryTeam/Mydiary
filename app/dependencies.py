from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.dtos.user_dto import UserResponse
from app.services import auth_service

# OAuth2PasswordBearer는 토큰을 추출하는 데 사용됩니다.
# tokenUrl은 클라이언트가 토큰을 요청할 엔드포인트입니다.
# user_router에 prefix="/users"가 설정되어 있으므로,
# 실제 토큰 엔드포인트는 /users/token 입니다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserResponse:
    """
    현재 인증된 사용자를 가져옵니다.
    액세스 토큰의 유효성을 검증하고 블랙리스트 여부를 확인합니다.
    :param token: 요청 헤더에서 추출된 액세스 토큰
    :return: 현재 사용자 정보 (UserResponse DTO)
    """
    payload = auth_service.decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    email: str | None = payload.get("sub")
    token_type: str | None = payload.get("type")

    # 토큰 페이로드 유효성 검사 및 토큰 타입 확인
    if email is None or token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload or type",
        )

    # 토큰이 블랙리스트에 있는지 확인 (로그아웃된 토큰인지 확인)
    if await auth_service.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked"
        )

    # 사용자 정보 조회
    user = await auth_service.get_user(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    # UserResponse DTO로 변환하여 반환
    return UserResponse.model_validate(user)
