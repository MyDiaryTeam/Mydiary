from app.dtos.diary_tags import DiaryTagSchemas
from app.models.diaries import DiaryModel
from app.models.tags import Tag


class DiaryTagService:
    async def add_tag_to_diary(
        self, diary_id: int, tag_id: int
    ) -> DiaryTagSchemas.MessageResponse:
        diary = await DiaryModel.get_or_none(id=diary_id)
        tag = await Tag.get_or_none(id=tag_id)

        if not diary or not tag:
            raise Exception("Diary or Tag not found")

        await diary.tags.add(tag)

        return DiaryTagSchemas.MessageResponse(message="Tag added to diary")

    async def remove_tag_from_diary(
        self, diary_id: int, tag_id: int
    ) -> DiaryTagSchemas.MessageResponse:
        diary = await DiaryModel.get_or_none(id=diary_id)
        tag = await Tag.get_or_none(id=tag_id)

        if not diary or not tag:
            raise Exception("Diary or Tag not found")

        await diary.tags.remove(tag)

        return DiaryTagSchemas.MessageResponse(message="Tag removed from diary")

    async def get_tags_of_diary(
        self, diary_id: int
    ) -> list[DiaryTagSchemas.TagResponse]:
        diary = await DiaryModel.get_or_none(id=diary_id).prefetch_related("tags")

        if not diary:
            raise Exception("Diary not found")

        tags = await diary.tags.all()
        return [DiaryTagSchemas.TagResponse(id=tag.id, name=tag.name) for tag in tags]
