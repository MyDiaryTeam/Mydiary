from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from app.dependencies import get_current_user
from app.dtos.diary_dto import (
    DiaryCreateRequest,
    DiaryResponse,
    DiaryUpdateRequest,
)
from app.models.diaries import DiaryModel, EmotionType
from app.models.emotion_keywords import EmotionKeywordModel
from app.models.users import UserModel
from app.services import gemini_service

router = APIRouter(prefix="/diaries", tags=["diaries"])


@router.post(
    "", response_model=DiaryResponse, status_code=HTTP_201_CREATED
)  # CreateDiary
async def create_diary(
    dairy_create: DiaryCreateRequest,
    current_user: UserModel = Depends(get_current_user),  # 0. 로그인 여부 확인
):
    # email의 타입을 되돌리기. (str -> email)
    user = await UserModel.get(email=current_user.email)
    # 2. User을 넣어야 하니 이에 따른 모델 생성. (모델에 맞게 생성해야함)
    diary = await DiaryModel.create(
        user=user,
        title=dairy_create.title,
        content=dairy_create.content,
        mood=dairy_create.mood,
    )
    print("diary is generated")
    print(type(diary))

    # 3. 리턴 값이 딕셔너리여야 함.
    await diary.fetch_related("emotion_keywords")
    return DiaryResponse.model_validate(diary)


@router.post("/{diary_id}/summarize")
async def summarize_diary(
    diary_id: int,
    current_user: UserModel = Depends(get_current_user),
):
    """
    특정 일기 내용을 Gemini API를 사용하여 2~3줄로 요약합니다.
    :param diary_id: 요약할 일기의 ID
    :param current_user: 현재 로그인된 사용자 정보
    :return: 요약된 일기 내용
    """
    diary = await DiaryModel.get_or_none(id=diary_id, user=current_user.id)
    # print(f"DEBUG: diary_id={diary_id}, current_user.id={current_user.id})
    # print(f"DEBUG: Retrieved diary: {diary})
    if not diary:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Diary not found or you don't have permission to access it",
        )

    summarized_text = await gemini_service.summarize_diary_content(diary.content)

    diary.emotion_summary = {"summary_text": summarized_text}
    await diary.save()

    return {"summary": summarized_text}


@router.post("/{diary_id}/emotion_stats", response_model=DiaryResponse)
async def analyze_diary_emotion_endpoint(
    diary_id: int,
    current_user: UserModel = Depends(get_current_user),
):
    """
    일기 내용을 Gemini API로 분석하여 감정 키워드를 추출하고 저장합니다.
    :param diary_id: 분석할 일기의 ID
    :param current_user: 현재 로그인된 사용자 정보
    :return: 업데이트된 일기 정보 (감정 키워드 포함)
    """
    diary = await DiaryModel.get_or_none(id=diary_id, user=current_user.id)
    if not diary:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Diary not found or you don't have permission to access it",
        )

    analysis_result = await gemini_service.analyze_diary_emotion(
        diary_id=diary.id, user_id=current_user.id, content=diary.content
    )
    print(f"DEBUG: Gemini analysis result: {analysis_result}")

    # 기존 감정 키워드 삭제
    await EmotionKeywordModel.filter(diary=diary).delete()

    # 새로운 감정 키워드 저장
    overall_sentiment_scores = {
        EmotionType.POSITIVE: 0,
        EmotionType.NEGATIVE: 0,
        EmotionType.NEUTRAL: 0,
    }
    if "keywords" in analysis_result:
        for keyword_data in analysis_result["keywords"]:
            word = keyword_data.get("word")
            emotion_str = keyword_data.get("emotion")
            if word and emotion_str:
                try:
                    emotion_type = EmotionType(emotion_str)
                    await EmotionKeywordModel.create(
                        diary=diary, word=word, emotion=emotion_type
                    )
                    overall_sentiment_scores[emotion_type] += 1
                except ValueError:
                    print(f"Invalid emotion type received: {emotion_str}")

    # 전체 감정 결정 (가장 많은 키워드 감정으로)
    overall_emotion: EmotionType | None = None
    max_score = 0
    for emotion_type, score in overall_sentiment_scores.items():
        if score > max_score:
            max_score = score
            overall_emotion = emotion_type
        elif score == max_score and overall_emotion is not None:
            # 동점일 경우, 부정 > 긍정 > 중립 순으로 우선순위 (선택 사항)
            if (
                overall_emotion is not None
                and emotion_type == EmotionType.NEGATIVE
                and overall_emotion != EmotionType.NEGATIVE
            ):
                overall_emotion = EmotionType.NEGATIVE
            elif (
                overall_emotion is not None
                and emotion_type == EmotionType.POSITIVE
                and overall_emotion == EmotionType.NEUTRAL
            ):
                overall_emotion = EmotionType.POSITIVE

    if overall_emotion is not None:
        diary.emotion = overall_emotion
    else:
        diary.emotion = None
    await diary.save()

    # 업데이트된 일기 정보 반환 (감정 키워드 포함)
    return await DiaryModel.get(id=diary_id).prefetch_related("emotion_keywords")


@router.get("/{diary_id}", response_model=DiaryResponse)  # GetDiary
async def get_diary(diary_id: int):
    diary = await DiaryModel.get_or_none(id=diary_id).prefetch_related(
        "emotion_keywords"
    )
    if not diary:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Diary not found")

    return DiaryResponse.model_validate(diary)


@router.get("", response_model=list[DiaryResponse])  # List Update
async def list_diaries(
    sort: str = Query("Latest", enum=["Oldest", "Latest"]),
    tag: str | None = None,
):
    # order가 Oldest이면 오래된 순, Latest이면 최신순   \
    order_by_field = "-created_at" if sort == "Latest" else "created_at"
    if tag:
        diaries = (
            await DiaryModel.filter(tags__name=tag)
            .order_by(order_by_field)
            .distinct()
            .prefetch_related("emotion_keywords")
        )
    else:
        diaries = (
            await DiaryModel.all()
            .order_by(order_by_field)
            .prefetch_related("emotion_keywords")
        )

    return [DiaryResponse.model_validate(diary) for diary in diaries]


@router.patch("/{diary_id}", response_model=DiaryResponse)  # Update Diary
async def update_diary(
    diary_id: int,
    request: DiaryUpdateRequest,
    current_user: UserModel = Depends(get_current_user),  # 0. 로그인 여부 확인
):

    # 1. 수정할 diary가 DB에 있는지 확인
    diary = await DiaryModel.get_or_none(id=diary_id)
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
