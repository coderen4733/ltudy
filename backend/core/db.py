from collections.abc import AsyncGenerator  # 세션 제너레이터 타입 힌팅용

from sqlalchemy import text  # 순수 SQL(SELECT 1) 실행용
from sqlalchemy.ext.asyncio import (
    AsyncEngine,  # 비동기 엔진 타입 힌팅용
    async_sessionmaker,  # 비동기 세션 팩토리 생성용
    create_async_engine,  # 비동기 엔진 생성용
)
from sqlmodel.ext.asyncio.session import AsyncSession  # 비동기 ORM 세션

from core.config import SBDB_URL  # .env에서 불러온 SupabaseDB URL

# SBDB_URL 정규화
# Supabase가 알려주는 URL은 "postgresql://..." 형태인데,
# 비동기 접속에는 asyncpg 드라이버를 명시한
# "postgresql+asyncpg://..." 형태가 필요함
# 그래서 드라이버 지정이 없으면 여기서 자동으로 붙여줌
if SBDB_URL and SBDB_URL.startswith("postgresql://"):
    ASYNC_DB_URL = SBDB_URL.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )
else:
    ASYNC_DB_URL = SBDB_URL


# DB Engine 🐘
# 앱 전체에서 하나만 만들어 재사용하는 커넥션 풀(엔진)
# echo=True로 두면 실행되는 SQL이 콘솔에 출력되어 학습/디버깅에 유용함
engine: AsyncEngine = create_async_engine(
    ASYNC_DB_URL,
    echo=True,
    # pool_pre_ping: 커넥션이 끊겼는지 미리 확인 후 사용(끊긴 커넥션 방지)
    pool_pre_ping=True,
    # Supabase 커넥션 풀러(PgBouncer)는 prepared statement를 지원하지 않으므로,
    # asyncpg가 만드는 statement 캐시를 꺼서 호환성 문제를 방지함
    connect_args={"statement_cache_size": 0},
)


# Session Factory
# 요청마다 새로운 세션(트랜잭션 단위)을 찍어내는 공장
# expire_on_commit=False: commit 후에도 객체 값을 계속 읽을 수 있게 함
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# DB 연결 확인용 함수
# apps/main.py의 lifespan에서 앱 시작 시 호출하여 실제 접속이 되는지 검증함
async def check_db_connection() -> None:
    # 커넥션을 하나 빌려 "SELECT 1"을 날려봄
    # 예외가 발생하지 않으면 연결 성공으로 판단
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


# [참고] 테이블 생성은 Alembic 마이그레이션이 담당합니다.
# 예전에는 여기서 SQLModel.metadata.create_all 로 만들었지만,
# 컬럼 추가/변경까지 관리하려고 Alembic 을 도입하면서 제거했습니다.
# 스키마를 바꾼 뒤에는 아래 명령을 실행하세요.
#   poetry run alembic revision --autogenerate -m "변경 내용"
#   poetry run alembic upgrade head
# (자세한 설명은 md/002_alembic.md 참고)


# Engine 종료용 함수
# apps/main.py의 lifespan에서 앱 종료 시 호출하여 커넥션 풀을 정리함
async def close_db() -> None:
    await engine.dispose()


# Router Depends(get_session)로 사용할 의존성 함수
# 요청이 들어올 때마다 세션을 하나 만들어 주고,
# 요청 처리가 끝나면(with 블록 종료) 자동으로 세션을 닫아 줌
async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        yield session
