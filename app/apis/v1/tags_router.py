from typing import List

from fastapi import APIRouter, HTTPException, status
from tortoise.exceptions import IntegrityError

from app.dtos.tags_dto import TagCreate, TagResponse
from app.models.tags import TagModel

# APIRouter 생성
router = APIRouter(prefix="/tags", tags=["tags"])


# 태그 생성
@router.post(
    "",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="태그 생성",
    description="새로운 태그를 생성합니다.",
)
async def create_tag(tag_data: TagCreate):
    try:
        # 새 태그 생성
        new_tag = await TagModel.create(tag_name=tag_data.tag_name)
        return TagResponse(id=new_tag.tag_id, tag_name=new_tag.tag_name)

    except IntegrityError:
        # 만약 태그가 중복된다면
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 태그입니다."
        )


# 태그 조회
@router.get(
    "",
    response_model=List[TagResponse],
    status_code=status.HTTP_200_OK,
    summary="태그 목록 조회",
    description="모든 태그 목록을 조회합니다.",
)
async def get_tags():
    tags = await TagModel.all()
    return [TagResponse(id=tag.tag_id, tag_name=tag.tag_name) for tag in tags]


# 조회(특정 태그만)랑 삭제?
@router.get(
    "/{tag_id}",
    response_model=TagResponse,
    summary="특정 태그 조회",
    description="ID로 특정 태그를 조회합니다.",
)
async def get_tag(tag_id: int):
    tag = await TagModel.filter(tag_id=tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="태그를 찾을 수 없습니다."
        )
    return TagResponse(id=tag.tag_id, tag_name=tag.tag_name)


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="태그 삭제",
    description="특정 태그를 삭제합니다.",
)
async def delete_tag(tag_id: int):
    tag = await TagModel.filter(tag_id=tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="태그를 찾을 수 없습니다."
        )

    await tag.delete()
    return
