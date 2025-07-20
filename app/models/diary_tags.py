from tortoise import fields, models


class DiaryTagModel(models.Model):
    diary = fields.ForeignKeyField("models.DiaryModel", related_name="diary_tags")
    tag = fields.ForeignKeyField("models.TagModel", related_name="diary_tags")

    class Meta:
        table = "diary_tags"
        unique_together = ("diary", "tag")
