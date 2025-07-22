from typing import TYPE_CHECKING

from tortoise import fields, models

if TYPE_CHECKING:
    from app.models.diaries import DiaryModel
    from app.models.tags import Tag


class DiaryTagModel(models.Model):
    diary: fields.ForeignKeyRelation["DiaryModel"] = fields.ForeignKeyField(
        "models.DiaryModel", related_name="diary_tags"
    )
    tag: fields.ForeignKeyRelation["Tag"] = fields.ForeignKeyField(
        "models.Tag", related_name="diary_tags"
    )

    class Meta:
        table = "diary_tags"
        unique_together = ("diary", "tag")
