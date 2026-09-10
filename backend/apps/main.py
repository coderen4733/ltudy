from contextlib import asynccontextmanager  # Lifespan 생성 시 활용

import redis.asyncio as aioredis  # Async Redis 라이브러리 추가
from fastapi import Depends, FastAPI  # FastAPI로 Back-End 구성
from fastapi.middleware.cors import (
    CORSMiddleware,  # CORS 설정을 위한 Middleware
)
from redis.asyncio import Redis
from sqlalchemy import text  # 순수 SQL 실행용
from sqlmodel.ext.asyncio.session import AsyncSession  # DB 세션 타입 힌팅용

from apps.api import api_router  # Router 등록
from core.config import REDIS_URL  # .env 환경변수 로드
from core.db import (  # SupabaseDB(SQLModel) 연결 관련
    check_db_connection,
    close_db,
    get_session,
)
from core.redis import get_redis


# APP Lifespan
# L-1. lifespan 정의: 앱 시작과 종료 시 실행될 로직
@asynccontextmanager
async def lifespan(app: FastAPI):
    # A. [Startup] 앱이 켜질 때 실행
    app.redis = aioredis.from_url(REDIS_URL, decode_responses=True)

    # A-D. DB 연결
    try:
        # A-D-1. 실제 접속이 되는지 "SELECT 1"로 확인
        # (테이블 생성/변경은 Alembic 마이그레이션이 담당함)
        await check_db_connection()
        # A-D-O. SupabaseDB 연결 성공
        print("SupabaseDB 연결에 성공했습니다.")
    except Exception as db_err:
        # A-D-X. SupabaseDB 연결 실패
        print(f"SupabaseDB 연결에 실패했습니다. {db_err}")

    # A-R. Redis Cloud 연결
    try:
        # A-R-O. Redis Cloud 연결 성공
        await app.redis.ping()
        print("Redis Cloud 연결에 성공했습니다.")
    except Exception as redis_err:
        # A-R-X. Redis Cloud 연결 실패
        print(f"Redis Cloud 연결에 실패했습니다. {redis_err}")
    # A-E. App 실행
    yield

    # B. [Shutdown] 앱이 꺼질 때 실행
    # B-D. SupabaseDB 커넥션 풀(엔진) 정리
    await close_db()
    print("SupabaseDB 연결이 종료되었습니다.")
    # B-R. Redis Cloud 커넥션 정리
    await app.redis.aclose()
    print("Redis Cloud 연결이 종료되었습니다.")


# L-2. FastAPI 인스턴스 생성 시 lifespan(L-1)을 따름
app = FastAPI(lifespan=lifespan)


# CORS 설정 🖥️
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 테스트용이므로 모두 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health Check API ✅
@app.get("/health-check", tags=["Health Check"])
async def health_check():
    return {
        "status": "healthy",
    }


# Redis Check API ✅
@app.get("/redis-check", tags=["Redis Check"])
async def redis_check(redis: Redis = Depends(get_redis)):
    try:
        # 1. Redis에 'health' -> 'check' 저장 (Redis Insight에서 확인 가능)
        await redis.set("health", "check")
        # 2. 'health' 키를 검색해서 값을 받아옴
        value = await redis.get("health")
        # 3. 값이 'check'로 정상 수신되면 healthy
        if value == "check":
            return {"redis_status": "healthy"}
        else:
            return {"redis_status": "sick"}
    # 4. 연결 실패 등 예외 발생 시 ill
    except Exception:
        return {"redis_status": "ill"}


# DB Check API ✅
@app.get("/db-check", tags=["DB Check"])
async def db_check(session: AsyncSession = Depends(get_session)):
    try:
        # 1. DB 세션으로 "SELECT 1"을 실행
        result = await session.exec(text("SELECT 1"))
        # 2. 결과값이 1로 정상 수신되면 healthy
        if result.scalar_one() == 1:
            return {"db_status": "healthy"}
        else:
            return {"db_status": "sick"}
    # 3. 연결 실패 등 예외 발생 시 ill
    except Exception:
        return {"db_status": "ill"}


# APP Router 등록 🚥
app.include_router(api_router)
