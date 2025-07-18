from tortoise import fields, models


class User(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"


__all__ = ["User"]
