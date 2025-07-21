from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status

from app.dtos.diary_tags import DiaryTagSchemas
from app.services.diary_tags import DiaryTagService

router = APIRouter(prefix="/diaries", tags=["Diary Tags"])
service = DiaryTagService()


@router.post(
    "/{diary_id}/tags",
    response_model=DiaryTagSchemas.MessageResponse,
    summary="일기 태그 추가",
    description="특정 일기에 태그를 추가합니다.",
)
async def add_tag_to_diary(
    diary_id: int = Path(...),
    tag_data: DiaryTagSchemas.TagAddRequest = Body(...),
    service: DiaryTagService = Depends(),
):
    return await service.add_tag_to_diary(diary_id, tag_data.id)


@router.delete(
    "/{diary_id}/tags/{tag_id}",
    response_model=DiaryTagSchemas.MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def remove_tag_from_diary(
    diary_id: int = Path(...),
    tag_id: int = Path(...),
):
    try:
        return await service.remove_tag_from_diary(diary_id, tag_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{diary_id}/tags", response_model=List[DiaryTagSchemas.TagResponse])
async def get_tags_of_diary(diary_id: int = Path(...)):
    try:
        return await service.get_tags_of_diary(diary_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
