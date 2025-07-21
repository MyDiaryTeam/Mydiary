from tortoise import fields, models


class Tag(models.Model):
    id = fields.IntField(pk=True, description="태그 ID")
    name = fields.CharField(max_length=100, unique=True, description="태그명")

    class Meta:
        table = "tags"

    def __str__(self):
        return self.name
