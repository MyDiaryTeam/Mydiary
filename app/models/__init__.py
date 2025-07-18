from tortoise import Tortoise

TORTOISE_ORM = {
    "connections": {
        "default": "postgres://postgres:비밀번호@localhost:5432/my_diary"
    },
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.diary",
                "app.models.tag",
                "app.models.emotion_stats",
                "app.models.alert_log",
                "aerich.models"  # 마이그레이션용
            ],
            "default_connection": "default",
        }
    },
}



# __all__ = ["User"]  # import 할 클래스 빼줘야함 항상.