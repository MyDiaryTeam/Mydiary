from pydantic import BaseModel


class DiaryTagSchemas:
    # 요청 바디: 태그 추가 요청
    class TagAddRequest(BaseModel):
        id: int

    # 응답 메시지
    class MessageResponse(BaseModel):
        message: str

    # 태그 조회 응답용
    class TagResponse(BaseModel):
        id: int
        name: str
