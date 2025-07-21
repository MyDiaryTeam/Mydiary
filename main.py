from contextlib import asynccontextmanager

from app.config.database import init_db
from fastapi import FastAPI

from app.apis.v1.user_router import router as user_router
from app.apis.v1.diary_router import router as diary_router


# @app.on_event("startup") # 오래된 방식 > New Way: lifespan
# async def startup():     # 유지보수 부담을 줄이기 위해
#     await init_db()      #
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Start Lifespan")
    await init_db()  # DB 시작
    yield  # 시작과 종료의 경계: 종료 시 실행할 codes
    print("End Lifespan")


app = FastAPI(lifespan=lifespan)  # 서버의 뇌를 만드는 과정,
# Flask API는 애플리케이션 생성;
# Uvicorn(ASGI 서버)가 그 객체를 통해 요청을 처리.

app.include_router(user_router)
app.include_router(diary_router)
