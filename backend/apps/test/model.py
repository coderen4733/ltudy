from datetime import datetime  # 작성 시각 저장용

from sqlmodel import Field, SQLModel  # 모델/컬럼 정의용


# 게시글의 공통 입력 필드 (제목, 본문)
# - 아래 여러 스키마에서 상속해 재사용하기 위한 base 클래스
# - 요청/응답 어느 쪽도 아니므로 접미사(Req/Res)를 붙이지 않음
class PostBase(SQLModel):
    title: str  # 게시글 제목
    author: str  # 게시글 작성자
    content: str  # 게시글 본문


# 실제 DB 테이블로 만들어질 모델
class Post(PostBase, table=True):
    # table=True => SQLModel이 이 클래스를 테이블로 인식
    __tablename__ = "test_post"  # 테이블명: 미지정 시 클래스명 소문자 자동지정
    id: int | None = Field(default=None, primary_key=True)  # auto increment
    created_at: datetime = Field(default_factory=datetime.now)


# [req] 게시글 작성 시 body로 받는 값
class PostCreateReq(PostBase):
    pass


# [req] 게시글 수정 시 body로 받는 값
# - 제목만 또는 본문만 바꿀 수 있도록 전부 선택(Optional) 처리
class PostUpdateReq(SQLModel):
    title: str | None = None
    author: str | None = None
    content: str | None = None


# [res] API가 돌려주는 게시글 형태
class PostReadRes(PostBase):
    id: int
    created_at: datetime
