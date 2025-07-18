from tortoise import fields, models


class DiaryTag(models.Model):
    diary = fields.ForeignKeyField("models.Diary", related_name="diary_tags")
    tag = fields.ForeignKeyField("models.Tag", related_name="diary_tags")

    class Meta:
        table = "diary_tags"
        unique_together = ("diary", "tag")
