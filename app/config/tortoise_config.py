import os

from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise
from dotenv import load_dotenv
from fastapi import FastAPI


load_dotenv()
TORTOISE_APP_MODELS = [
    "aerich.models",
    "app.models.users",
    "app.models.diaries",
    "app.models.diary_tags",
    "app.models.emotion_stats",
    "app.models.alert_logs",
    "app.models.tags",
]

TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
    },
    "apps": {
        "models": {
            "models":
                TORTOISE_APP_MODELS,

            "default_connection": "default",
        }
    },
}



def initialize_tortoise(app: FastAPI) -> None:
    Tortoise.init_models(TORTOISE_APP_MODELS, "models") # 이 줄은 register_tortoise를 사용한다면 중복될 수 있으므로 제거하는 것을 고려하세요.
    register_tortoise(app, config=TORTOISE_ORM)

