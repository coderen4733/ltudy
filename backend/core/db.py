from collections.abc import AsyncGenerator  # 세션 제너레이터 타입 힌팅용

from sqlalchemy import text  # 순수 SQL(SELECT 1) 실행용
from sqlalchemy.ext.asyncio import (
    AsyncEngine,  # 비동기 엔진 타입 힌팅용
    async_sessionmaker,  # 비동기 세션 팩토리 생성용
    create_async_engine,  # 비동기 엔진 생성용
)
from sqlmodel import SQLModel  # 테이블 메타데이터(모델 정의) 관리용
from sqlmodel.ext.asyncio.session import AsyncSession  # 비동기 ORM 세션

from core.config import SBDB_URL  # .env에서 불러온 SupabaseDB URL

# SBDB_URL 정규화
# Supabase가 알려주는 URL은 "postgresql://..." 형태인데,
# 비동기로 접속하려면 asyncpg 드라이버를 명시한 "postgresql+asyncpg://..."가 필요함
# 그래서 드라이버 지정이 없으면 여기서 자동으로 붙여줌
#
# [참고] .env의 SBDB_URL에는 Supabase의 "Connection Pooling(Session pooler)" 주소를
#        넣어야 합니다. Direct 연결 주소(db.<ref>.supabase.co)는 IPv6 전용이라
#        IPv4 환경에서는 접속되지 않습니다.
#        예) postgresql://postgres.<ref>:<PW>@aws-0-<region>.pooler.supabase.com:5432/postgres
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
    pool_pre_ping=True,  # 커넥션이 끊겼는지 미리 확인 후 사용(끊긴 커넥션 방지)
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
    # 커넥션을 하나 빌려 "SELECT 1"을 날려보고, 예외가 없으면 연결 성공으로 판단
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


# 테이블 생성용 함수
# SQLModel 모델 클래스로 정의한 테이블들을 DB에 없으면 만들어 줌
# (실무에서는 Alembic 같은 마이그레이션 도구를 쓰지만, 초기 개발엔 이걸로 충분함)
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


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
