from fastapi import APIRouter

from apps.test.crud import router as test_crud_router  # 테스트 CRUD 라우터

api_router = APIRouter()

# 각 기능별 라우터를 여기서 api_router에 등록한다
# (main.py가 이 api_router 하나만 app에 include 함)
api_router.include_router(test_crud_router)
