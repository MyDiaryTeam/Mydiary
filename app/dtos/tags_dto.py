from pydantic import BaseModel


# Pydantic 모델 정의
class TagCreate(BaseModel):
    tag_name: str


class TagResponse(BaseModel):
    id: int
    tag_name: str
