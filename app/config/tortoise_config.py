import os

from dotenv import load_dotenv

load_dotenv()

TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
    },
    "apps": {
        "models": {
            "models": [
                "aerich.models",
                "app.models",
                "app.models.users",
                "app.models.diaries",
                "app.models.diary_tags",
                "app.models.emotion_stats",
                "app.models.alert_logs",
                "app.models.tags",
            ],
            "default_connection": "default",
        }
    },
}
