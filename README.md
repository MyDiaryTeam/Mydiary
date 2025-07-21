MyDiaryProject

# FastAPI Project 생성하기
1. 프로젝트 구조 구성 예시     
2. 개발환경 구분

## 프로젝트 구조 구성 예시 
```
fastapi_mini_project/
├── app/                              # FastAPI 애플리케이션 디렉토리
│   ├── __init__.py                   # app 패키지 초기화 파일
│   ├── core/                         # 설정 파일 디렉토리
│   │   ├── __init__.py
│   │   └── config.py                 # 설정 파일 (env 설정 로드 등)
│   ├── models/                       # TortoiseORM 모델 디렉토리
│   │   ├── __init__.py               # 모델 초기화 및 등록
│   │   └── user.py                   # 예시 모델
│   ├── database.py                   # TortoiseORM 초기화 및 설정
│   └── main.py                       # FastAPI 애플리케이션 진입점
├── migrations/                       # aerich 마이그레이션 디렉토리
├── aerich.ini                        # Aerich 설정 파일
├── .env                              # 개발 환경 설정 파일 (예: DEBUG=True)
├── .env.prod                         # 배포 환경 설정 파일 (예: DEBUG=False)
├── pyproject.toml                    # uv/Poetry 설정 파일
├── uv.lock                           # 의존성 잠금 파일
```
## 개발환경 구분
1. prod 그룹
`uv add fastapi uvicorn python-dotenv tortoise-orm asyncpg aerich --group prod`
2. dev 그룹
`uv add black isort flake8 pytest httpx pytest-asyncio --dev`

# PostgreSQL + TortoiseORM 비동기 연결하기
- [1]  프로젝트 구조에 `database.py` 추가하여 Tortoise ORM 초기화 설정을 분리합니다.
- [2]  `PostgreSQL`을 로컬 환경에 설치하고 세팅한다.
- [3]  DB를 생성하고 `.env` 를 수정하여 데이터베이스를 비동기로 연결한다.
- [4]  `Tortoise ORM`과 `asyncpg`로 데이터베이스 연결 설정한다.
- [5]  `aerich`을 사용하여 데이터베이스 마이그레이션을 생성하고 적용한다.

## [1] 프로젝트 구조에 `database.py` 추가하여 Tortoise ORM 초기화 설정을 분리합니다.
database.py
``` 
# 데이터 베이스 연결 설정과 초기화 함수
import os

from dotenv import load_dotenv
from tortoise import Tortoise

load_dotenv() # 데이터베이스 접근을 안전하게 만든다. (환경변수에 따로 관리하기 때문에)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

async def init_db():
    await Tortoise.init(
        db_url = f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}", # 환경변수로 관리하여 보안 강화
        #
        modules={"models":["models"]},
    )
    await Tortoise.generate_schemas()
```

.env
```angular2html
# 앱 실행 설정
APP_ENV=development
APP_NAME=MyDiaryProject
APP_PORT=8000

# 데이터베이스 설정
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mydatabase
```

.main.py
```
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_db


# @app.on_event("startup") # 오래된 방식 > New Way: lifespan
# async def startup():     # 유지보수 부담을 줄이기 위해
#     await init_db()      #
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Start Lifespan")
    await init_db()         # DB 시작
    yield                   # 시작과 종료의 경계: 종료 시 실행할 codes
    print("End Lifespan")

app = FastAPI(lifespan=lifespan) # 서버의 뇌를 만드는 과정,
                                 # Flask API는 애플리케이션 생성;
                                 # Uvicorn(ASGI 서버)가 그 객체를 통해 요청을 처리.
```

## [2]  `PostgreSQL`을 로컬 환경에 설치하고 세팅한다.
설치 ㄱㄱ, 
`https://www.enterprisedb.com/downloads/postgres-postgresql-downloads`

## [3]  DB를 생성하고 `.env` 를 수정하여 데이터베이스를 비동기로 연결한다.
``` 설치 및 실행
psql --vesrion   # 설치 확인
psql -U postgres # 슈퍼유저로 접속
```
``` postgre 유저 생성
CREATE DATABASE mydiary; 
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE mydiary TO myuser;
```  
``` 접속 테스트
psql -U myuser -d mydiary -h localhost
```
``` 한정적 권한 제공 및 실행
CREATE DATABASE mydiary OWNER myuser;               # myuser 소유의 mydiary 데이터베이스 생성
GRANT ALL PRIVILEGES ON DATABASE mydiary TO myuser; # myuesr에게 mydiary 데이터베이스에 한해서만 모든 권한 제공
psql -U myuser -d mydiary -h localhost;             
```

## [4]  `Tortoise ORM`과 `asyncpg`로 데이터베이스 연결 설정한다.
> PostgreSQL = DB > Tortoise ORM + asyncpg = SQL구문 + 비동기 연결 > FastAPI = APP

Tortoise ORM: SQL을 DB내부가 아닌 밖에서 작성.
asyncpg     : DB 명령을 비동기적으로 실행 및 통신하기 위함.

1. database.py
``` 
from tortoise import Tortoise, run_async

(중략)

async def main():   # main 함수에 비지니스 로직/DB작업 함수(main.py or service.py) 추가
    await init_db()

if __name__ == "__main__":
    run_async(main())  # 비동기 main() 실행
    
```
2. example_models.py
```angular2html
from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

__all__ = ["User"]
```
3. tortoise_config.py 생성 및 models 등록
```
import os
from dotenv import load_dotenv

load_dotenv()

TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
    },
    "apps": {
        "models": {
            "models": ["aerich.models", "app.models"], # "app.models" 추가
            "default_connection": "default",
        }
    }
}
```

## [5]  `aerich`을 사용하여 데이터베이스 마이그레이션을 생성하고 적용한다.
1. Tortoise_ORM: aerich 사용
```
aerich init -t tortoise_config.TORTOISE_ORM # Aerich 초기화
aerich init-db                              # 초기 마이그레이션 + DB 테이블 생성
aerich migrate --name add_field             # 모델 변경 시 마이그레이션 생성
aerich upgrate                              # 마이그레이션 적용
```
2. models/__init__.py
```angular2html
from .models import User

__all__ = ["User"] # import 할 클래스 빼줘야함 항상.
```

# Github Actions CI 설정 (Continious Integration)
1. **[project.optional-dependencies.dev]** 에 Code Qulity Checking 을 위한 라이브러리를 설치한다.
2. 민감한 정보를 코드에 노출시키지 않기 위해 Git Actions에서 환경변수를 저장한다.
3. 프로젝트 루트 디렉터리에 `.github` 폴더를 생성하고 하위에 `workflows/checks.yml` 파일을 생성한다.
   
## 1. **[project.optional-dependencies.dev]** 에 Code Qulity Checking 을 위한 라이브러리를 설치한다.
 -  **`black`** : PEP8 코드 포매터
 -  **`ruff`** : import 정렬 순서 코드 포매터
    
## 2. 민감한 정보를 코드에 노출시키지 않기 위해 Git Actions에서 환경변수를 저장한다.
Github Repository의 Settings → Secrets and Variables → Action → New repository secret
 - Database 연결정보
 - EC2 연결 정보 등(추후 배포 구현 시 추가)
    
## 3. 프로젝트 루트 디렉터리에 `.github` 폴더를 생성하고 하위에 `workflows/checks.yml` 파일을 생성한다.
    
`checks.yml` 파일에 CI를 위한 스크립트를 아래의 요구사항을 만족하도록 작성한다.

- [1]  브랜치에 PUSH할 때 작동되도록 설정
- [2]  `Postgresql` 서비스 생성 및 연결 테스트
- [3]  `uv` 설치 및 의존성 패키지 및 라이브러리 설치
- [4]  `ruff`, `black`  코드 스타일 및 정적 타입 검사 테스트 추가
- [5]  `pytest` 코드 실행 추가 (2단계 도전 미션 관련)
- 스크립트 예시
```yaml
# .github/workflows/checks.yml

name: Code Quality Checks

# 트리거 이벤트 부분
# 코드가 푸시되거나 풀 리퀘스트가 생성될 때 CI가 실행됩니다.
on:
  push:
    branches:
      - main
  pull_request:

jobs:
  ci:
    # 가장 최신버전의 ubuntu를 OS 환경으로 설정합니다.
    runs-on: ubuntu-latest

    # services 키워드를 사용하여 PostgreSQL 서비스를 설정
    services:
      db:
        image: postgres:15
        ports:
          - 5432:5432
        # Github Secrets에서 가져와서 env로 등록, PostgreSQL 데이터베이스 연결 설정
        env:
          POSTGRES_DB: ${{ secrets.POSTGRES_DB }}
          POSTGRES_USER: ${{ secrets.POSTGRES_USER }}
          POSTGRES_PASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
        # 옵션으로 PostgreSQL의 연결 상태를 확인. 10초 단위로 5번 재시도. 5초간 기다림.
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      # CI 환경에서 코드를 체크아웃합니다.
      - name: Checkout code
        uses: actions/checkout@v3

      # CI 환경에서 사용할 파이썬 버전을 지정합니다.
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      # uv를 설치합니다.
      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.local/bin" >> $GITHUB_PATH
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH

      # uv를 사용하여 의존성 패키지들을 설치합니다.
      - name: Install dependencies using uv
        run: |
          uv sync --dev-packages

      # ruff로 import 정렬 및 코드 스타일 검사
      - name: Run ruff (Code quality check)
        run: |
          uv run ruff check . 

      # black을 사용하여 PEP8 코드스타일을 준수했는지 체크합니다.
      - name: Run black (Code formatting)
        run: |
          uv run black . --check

      # db 연결을 테스트
      - name: Wait for PostgreSQL
        run: |
          until pg_isready -h localhost -p 5432 -U "${{ secrets.POSTGRES_USER }}"; do
            echo "Waiting for PostgreSQL..."
            sleep 2
          done

      # .env 환경 구성
      - name: Set environment variables
        run: |
          echo "DATABASE_URL=postgres://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:5432/$POSTGRES_DB" >> $GITHUB_ENV
        env:
          POSTGRES_USER: ${{ secrets.POSTGRES_USER }}
          POSTGRES_PASSWORD: ${{ secrets.POSTGRES_PASSWORD }}
          POSTGRES_DB: ${{ secrets.POSTGRES_DB }}

      # 정상적인 db 연결을 확인했으니 마이그레이션 수행 
      - name: Run aerich migrations
        run: |
          uv run aerich upgrade

      # 도전 미션
      # FastAPI에서 pytest로 테스트를 실행합니다.
      - name: Run tests with pytest
        run: |
          uv run pytest
```

# Model 생성하기
Step 1: 모델 정의하기
Step 2: tortoise_config.py 
Step 3: Aerich

## Step 1: 모델 정의하기
ERD
`https://www.mermaidchart.com/app/projects
/3a33ee98-654f-41f6-a2c7-a04e5f2494e9
/diagrams/1a5d8e4e-f696-4e4b-a979-afa4af308137/version/v0.1/edit`

users.py
```
from tortoise import fields, models
from datetime import datetime


class User(models.Model):
    user_id = fields.IntField(pk=True, description="사용자 고유 식별자")
    email = fields.CharField(max_length=255, unique=True, description="사용자 이메일 (로그인 ID)")
    name = fields.CharField(max_length=100, description="사용자 이름")
    nickname = fields.CharField(max_length=100, unique=True, description="사용자 닉네임")
    phone_number = fields.CharField(max_length=15, description="휴대폰 번호")
    password_hash = fields.CharField(max_length=255, description="해시된 비밀번호")
    account_status = fields.CharEnumField(enum_type=["active", "inactive"], description="계정 활성화 상태")
    account_type = fields.CharEnumField(enum_type=["admin", "general"], description="계정 유형")
    created_at = fields.DatetimeField(auto_now_add=True, description="계정 생성 시간")
    updated_at = fields.DatetimeField(auto_now=True, description="계정 마지막 업데이트 시간")

    class Meta:
        table = "users"
```

### Exception 1: Enum
Tortoise ORM Should use "Python Enum Class" at EnumField 

❌ 리스트로 정의 → Tortoise가 타입을 해석 못함
```
account_status = fields.CharEnumField(["active", "inactive"], max_length=10)
```

✅ 올바른 예시
```
from enum import Enum
from tortoise import fields, models

class AccountStatus(str, Enum):     # PythonEnumClass로 EnumField를 우선 정의
    ACTIVE = "active"
    INACTIVE = "inactive"

class User(models.Model):           # 정의한 EnumField를 넣기 "AccountStatus"
    id = fields.IntField(pk=True)
    account_status = fields.CharEnumField(AccountStatus, max_length=10)
```

### Exception 2: Use UserModel Library
써야 하는데....

## Step 2: TORTOISE_ORM 
```angular2html
TORTOISE_ORM = {
    "connections": {"default": "postgres://user:password@localhost:5432/mydb"},
    "apps": {
        "models": {
            "models": [
                "app.models.user",              # ✅ User 모델
                "app.models.account",           # ✅ Account 모델
                "aerich.models"                 # ✅ 반드시 추가 (마이그레이션 관리용)
            ],
            "default_connection": "default",
        }
    },
}
```

## Step3: Aerich
- `aerich migrate`
- `aerich upgrade`

### Exception 1: PREVILEGES
```angular2html
슈퍼유저로 접속 후
GRANT ALL PRIVILEGES ON DATABASE mydiary TO myuser;
GRANT USAGE ON SCHEMA public TO myuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO myuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO myuser;
```

# API 구현
Step 1: API 스펙 설계
Step 2: 유저 API 구현
Step 3: 일기 API 구현
Step 4: Test Code 작성

## STEP 3: 일기 API 구현
MDR (Model, DTO, Router)
1. Model # Already done
2. DTO (Pydantic)

Pydantic: 직렬화/ 역질렬화를 자동화 하기 위함.
 - Validation
``` Valiation
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
```

 - Type Casting
``` Type Casting
user = User(name="Alice", age="25")
print(user.age)  # 25 (int로 자동 변환)
```

 - Serialization / Deserialization
```Serialization / Deserialization
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    name: str
    age: int

@app.post("/users")
def create_user(user: User):
    return user  # JSON 자동 변환
```
 - IDE, Type Hinting
 - 무결성 확보

3. Router
```angular2html

```
```including router

```

### Exception 1: SwaggerUI에 보이지 않음
Code:
Cause: Router을 새로 등록해서 서버를 재시작해야함. 8000 Port가 종료가 안됨.  
Solution 1: 8000번 포트 종료
Solution 2: 컴퓨터 재부팅

### Exception 2: DB Connection 오류
Code: `tortoise.exceptions.ConfigurationError: default_connection for the model <class 'app.models.diaries.DiaryModel'> cannot be None`
Cause: User을 UserModel로 변경함. 이후, 모든 관련 스키마가 같이 바꾸지 않음.
Solution 1: 다른 모델 및 라우터의 FK Key를 재확인

### Exception 3: dto 입력 오류
Code: ``
Cause: Model의 스키마에서 꼭 채워야하는 값이 없을 때 오류가 생김
Solution: 

### Exception 4: 일기 생성 시 / 422 Unprocessable Entity
Code: `POST /diaries/ HTTP/1.1" 422 Unprocessable Entity`
Cause: 서버에서 받은 필드와 dto의 필드가 다름
Solution 1: id는 AutoIncrement이므로 Create 기능엔 추가하지 않음
Solution 2: user_email은 FK이므로 스트링이 아님.
Solution 3: EnumField로 정의한 것은 class를 이용하여 따로 정의해줘야함.

### Exception 5: 일기 생성 시 / 500 Internal Server Error
Code: `"POST /diaries/ HTTP/1.1" 500 Internal Server Error`
Cause 1: 라우터에 FK 값이 있는 콜럼, 참조 오류
Solution 1: UserModel 불러오기, UserModel의 값을 클래스 인스턴스로 반환하여 사용

Cause 2: Dict 값 참조 오류
Solution 1: `return DiaryResponse.model_validate(diary.__dict__)`
Solution 2: ` model_config = { "from_attributes": True, }`

### Exception 6: 일기 하나 불러오기 / 존재하지 않는 필터명으로 불러오기
Code: `Unknown filter param 'id'. Allowed base values are [...]`
Cause: 존재하지 않는 필드가 있다는 것
Solution: Router에서 잘 찾아보자

### Exception 7: 유저 헤더에 정보 보내는 법
Code: `POST /diaries/ HTTP/1.1" 401 Unauthorized`
Cause: 토큰 값을 헤더로 보내지 않음.
Solution: Pydantic Model에서 user_email 필드 삭제

### Exception 8: 
Code: `AttributeError: 'UserInDB' object has no attribute '_saved_in_db'`
Cause: ForeignKeyField는 TortoiseORM Model만 받을 수 있음, PydanticModel을 주고 있어 에러가 남.
Solution:  
