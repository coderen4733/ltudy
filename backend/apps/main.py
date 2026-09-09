from contextlib import asynccontextmanager  # Lifespan

from fastapi import Depends, FastAPI


# APP Lifespan
# L-1. lifespan 정의: 앱 시작과 종료 시 실행될 로직
@asynccontextmanager
async def lifespan(app: FastAPI):
    # A. [Startup] 앱이 켜질 때 실행

    yield


# L-2. FastAPI 인스턴스 생성 시 lifespan(L-1)을 따름
app = FastAPI(lifespan=lifespan)


# Health Check API
@app.get("/health-check", tags=["Health Check"])
async def health_check():
    return {
        "status": "healthy",
    }
