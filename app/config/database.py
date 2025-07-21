# 데이터 베이스 연결 설정과 초기화 함수
import os

from dotenv import load_dotenv
from tortoise import Tortoise, run_async

load_dotenv()  # 데이터베이스 접근을 안전하게 만든다. (환경변수에 따로 관리하기 때문에)

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

async def init_db():
    await Tortoise.init(
        # 환경변수로 관리하여 보안 강화
        db_url=f"postgres://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
        modules={"models": ["app.models", "aerich.models", "app.models.diaries"]},
    )
    await Tortoise.generate_schemas()  # 필요 시 DB 스키마 생성 함수

async def main():  # main 함수에 비지니스 로직/DB작업 함수(main.py or service.py) 추가
    await init_db()


if __name__ == "__main__":
    run_async(main())  # 비동기 main() 실행
