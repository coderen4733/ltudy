from fastapi import APIRouter, Depends, HTTPException  # 라우터/의존성/에러
from sqlmodel import select  # SELECT 쿼리 작성용
from sqlmodel.ext.asyncio.session import AsyncSession  # 비동기 세션 타입

from apps.test.model import Post, PostCreateReq, PostReadRes, PostUpdateReq
from core.db import get_session  # 요청마다 DB 세션을 주입받는 의존성

# 이 파일의 API들을 "/test/posts" 경로 아래로 묶고 Swagger 태그도 지정
router = APIRouter(prefix="/test/posts", tags=["Test CRUD"])


# 공통 helper: id로 게시글을 조회하고, 없으면 404 에러를 발생시킴
# - 상세 조회 / 수정 / 삭제에서 똑같이 필요하므로 함수로 분리함
async def _get_post_or_404(session: AsyncSession, post_id: int) -> Post:
    # 기본키(id)로 한 건 조회 (없으면 None 반환)
    post = await session.get(Post, post_id)
    if post is None:
        # 404: 해당 id의 게시글이 존재하지 않음
        raise HTTPException(
            status_code=404,
            detail="게시글을 찾을 수 없습니다.",
        )
    return post


# 1. 게시글 작성 (Create) - POST /test/posts
@router.post("", response_model=PostReadRes)
async def create_post(
    payload: PostCreateReq,
    session: AsyncSession = Depends(get_session),
):
    # 1) 요청 body로 받은 값으로 Post 객체를 만든다
    post = Post(
        title=payload.title,
        author=payload.author,
        content=payload.content,
    )
    # 2) 세션에 추가하고 커밋해서 실제 DB에 저장한다
    session.add(post)
    await session.commit()
    # 3) DB가 자동으로 채운 값(id, created_at)을 다시 읽어온다
    await session.refresh(post)
    return post


# 2. 게시글 목록 조회 (Read - List) - GET /test/posts
@router.get("", response_model=list[PostReadRes])
async def list_posts(
    session: AsyncSession = Depends(get_session),
):
    # 최신 글이 위로 오도록 id 내림차순 정렬해서 전체 조회
    result = await session.exec(select(Post).order_by(Post.id.desc()))
    return result.all()


# 3. 게시글 상세 조회 (Read - Detail) - GET /test/posts/{post_id}
@router.get("/{post_id}", response_model=PostReadRes)
async def get_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
):
    # helper로 조회 (없으면 여기서 404 발생)
    return await _get_post_or_404(session, post_id)


# 4. 게시글 수정 (Update) - PATCH /test/posts/{post_id}
@router.patch("/{post_id}", response_model=PostReadRes)
async def update_post(
    post_id: int,
    payload: PostUpdateReq,
    session: AsyncSession = Depends(get_session),
):
    # 1) 수정할 게시글을 먼저 조회한다
    post = await _get_post_or_404(session, post_id)
    # 2) 요청 body에서 "실제로 보낸 필드"만 골라낸다
    #    (exclude_unset=True: 아예 안 보낸 값은 무시)
    data = payload.model_dump(exclude_unset=True)
    # 3) 골라낸 필드만 기존 객체에 덮어쓴다
    for key, value in data.items():
        setattr(post, key, value)
    # 4) 저장
    session.add(post)
    await session.commit()
    await session.refresh(post)
    return post


# 5. 게시글 삭제 (Delete) - DELETE /test/posts/{post_id}
@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
):
    # 1) 삭제할 게시글을 먼저 조회한다 (없으면 404)
    post = await _get_post_or_404(session, post_id)
    # 2) 세션에서 삭제 표시 후 커밋
    await session.delete(post)
    await session.commit()
    # 3) 삭제된 id를 알려준다
    return {"ok": True, "deleted_id": post_id}
