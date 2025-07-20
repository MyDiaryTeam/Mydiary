from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND
from app.models.diaries import DiaryModel
from app.dtos.diary_dto import DiaryCreateRequest, DiaryUpdateRequest, DiaryResponse
from app.models.users import UserModel

router = APIRouter(prefix="/diaries", tags=["diaries"])


@router.post(
    "/", response_model=DiaryResponse, status_code=HTTP_201_CREATED
)  # CreateDiary
async def create_diary(dairy_create: DiaryCreateRequest):
    # 1. UserModel 찾기
    user = await UserModel.get_or_none(email=dairy_create.user_email)
    if not user:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")

    # 2. User을 넣어야 하니 이에 따른 모델 생성. (모델에 맞게 생성해야함)
    diary = await DiaryModel.create(
        user_email=user,
        title=dairy_create.title,
        content=dairy_create.content,
        emotion_summary=dairy_create.emotion_summary,
        mood=dairy_create.mood,
    )
    print("diary is generated")
    print(type(diary))

    # 3. 리턴 값이 딕셔너리여야 함.
    return DiaryResponse.model_validate(diary)


@router.get("/{diary_id}", response_model=DiaryResponse)  # GetDiary
async def get_diary(diary_id: int):
    diary = await DiaryModel.get_or_none(diary_id=diary_id)
    if not diary:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Diary not found")

    return DiaryResponse.model_validate(diary)


@router.get("/", response_model=list[DiaryResponse])  # List Update
async def list_diaries():
    diaries = await DiaryModel.all().order_by("-created_at")
    return [DiaryResponse.model_validate(diary) for diary in diaries]


@router.patch("/{diary_id}", response_model=DiaryResponse)  # Update Diary
async def update_diary(diary_id: int, request: DiaryUpdateRequest):
    # 1. 수정할 diary가 DB에 있는지 확인
    diary = await DiaryModel.get_or_none(diary_id=diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")

    # 2. 전달된 값만 업데이트
    if request.title is not None:
        diary.title = request.title
    if request.content is not None:
        diary.content = request.content

    # 3. DB 저장
    await diary.save()

    # 4. 수정된 diary를 response 모델로 반환
    return DiaryResponse.model_validate(diary)
