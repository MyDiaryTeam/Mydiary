from pydantic import BaseModel


# Pydantic 모델 정의
class TagCreate(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    name: str
