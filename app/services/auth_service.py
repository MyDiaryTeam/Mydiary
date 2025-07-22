from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.config import settings
from app.dtos.user_dto import (
    UserInDB,
)  # 사용자 DTO 임포트 (비밀번호 포함된 사용자 정보)
from app.models.token_blacklist import TokenBlacklist
from app.models.users import UserModel  # 사용자 모델 임포트

# 비밀번호 해싱을 위한 CryptContext 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해싱된 비밀번호를 비교하여 일치하는지 확인합니다.
    :param plain_password: 사용자가 입력한 평문 비밀번호
    :param hashed_password: 데이터베이스에 저장된 해싱된 비밀번호
    :return: 비밀번호 일치 여부 (True/False)
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    주어진 평문 비밀번호를 해싱합니다.
    :param password: 해싱할 평문 비밀번호
    :return: 해싱된 비밀번호 문자열
    """
    return pwd_context.hash(password)


def create_token(
    data: dict, token_type: str, expires_delta: Optional[timedelta] = None
) -> str:
    """
    액세스 토큰 또는 리프레시 토큰을 생성합니다.
    :rtype: str
    :param data: 토큰에 포함될 페이로드 데이터
    :param token_type: 생성할 토큰의 종류
    :param expires_delta: 토큰의 명시적 만료 시간 (timedelta 객체)
    :return: 인코딩된 JWT 문자열
    """
    to_encode = data.copy()

    # 토큰 타입에 따라 만료 시간 설정
    if token_type == "access":
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )
    elif token_type == "refresh":
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=REFRESH_TOKEN_EXPIRE_MINUTES
            )
    else:
        # 유효하지 않은 토큰 타입이 전달된 경우 에러 발생
        raise ValueError("Invalid token type. Must be 'access' or 'refresh'.")

    # 페이로드에 만료 시간(exp)과 토큰 타입(type) 클레임 추가
    to_encode.update({"exp": expire, "type": token_type})

    # JWT 인코딩 (서명)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_user(email: str) -> Optional[UserInDB]:
    user = await UserModel.get_or_none(email=email)
    if user:
        return UserInDB.model_validate(user)
    return None


async def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    """
    사용자 이메일과 비밀번호를 사용하여 인증을 수행합니다.
    :param email: 사용자의 이메일
    :param password: 사용자가 입력한 비밀번호
    :return: 인증된 UserInDB 객체 또는 False
    """
    user = await get_user(email)  # 이메일로 사용자 조회
    if not user:
        return False  # 사용자가 존재하지 않으면 인증 실패

    # 저장된 해싱 비밀번호와 입력된 비밀번호 비교
    if not verify_password(password, user.password):
        return False  # 비밀번호가 일치하지 않으면 인증 실패

    return user  # 인증 성공 시 사용자 객체 반환


def decode_token(token: str) -> Optional[dict]:
    """
    JWT를 디코딩하고 유효성을 검증하여 페이로드 데이터를 반환합니다.
    :param token: 디코딩할 JWT 문자열
    :return: 디코딩된 페이로드 딕셔너리 또는 None
    """
    try:
        # JWT 디코딩 및 서명 검증
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # JWT 관련 오류 (예: 토큰 만료, 서명 불일치, 변조 등) 발생 시 None 반환
        return None


async def add_token_to_blacklist(token: str):
    """
    주어진 토큰을 블랙리스트에 추가하여 무효화합니다.
    주로 로그아웃 시 액세스 토큰을 재사용할 수 없도록 할 때 사용됩니다.
    :param token: 블랙리스트에 추가할 토큰 문자열
    """
    if not await is_token_blacklisted(token):
        await TokenBlacklist.create(token=token)


async def is_token_blacklisted(token: str) -> bool:
    """
    주어진 토큰이 블랙리스트에 등록되어 있는지 확인합니다.
    :param token: 확인할 토큰 문자열
    :return: 토큰이 블랙리스트에 있으면 True, 없으면 False
    """
    blacklisted_token = await TokenBlacklist.get_or_none(token=token)
    return blacklisted_token is not None  # 토큰이 존재하면 True, 없으면 False
