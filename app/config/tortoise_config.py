import os

from dotenv import load_dotenv
from fastapi import FastAPI
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

load_dotenv()
TORTOISE_APP_MODELS = [
    "aerich.models",
    "app.models.users",
    "app.models.token_blacklist",
    "app.models.diaries",
    "app.models.diary_tags",
    "app.models.emotion_stats",
    "app.models.alert_logs",
    "app.models.tags",
    "app.models.emotion_keywords",
]

TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
    },
    "apps": {
        "models": {
            "models": TORTOISE_APP_MODELS,
            "default_connection": "default",
        }
    },
}


def initialize_tortoise(app: FastAPI) -> None:
    Tortoise.init_models(TORTOISE_APP_MODELS, "models")
    register_tortoise(app, config=TORTOISE_ORM)
