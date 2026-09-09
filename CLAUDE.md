# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

- 이 프로젝트 참여자는 모두 한국인이기 때문에 md파일이나 주석은 모두 한국어로 작성해야 합니다.
- 참여한 개발자는 모두 초급 개발자이기 때문에 코드마다 주석을 달아서 쉽게 설명해주어야 합니다.
- 주석은 현재 작성된 코드에 달려있는 주석들을 참고하여, 기존 주석과 똑같은 방식과 형식으로 일관되게 작성하여야 합니다.

## 1. 프로젝트 개요
- **기술 스택**: Python 3.14+, FastAPI, Poetry, PostgreSQLDB(SQLModel), AWS S3
- **프로젝트 목적**: 다양한 경로를 통해 LLM을 활용할 수 있도록 해주는 웹사이트 개발
- **주요 특징**:
  - 로컬에 있는 오픈소스 LLM을 활용할 수 있는 기능
  - 클라우드 방식으로 대여한 GPU 서버를 활용하여 오픈소스 LLM을 구동할 수 있는 기능
  - AWS Bedrock을 활용하여 클라우드 방식으로 LLM을 호출하여 사용할 수 있는 기능 
  - AWS S3를 활용한 대용량 이미지 및 파일 업로드 및 관리

## 2. 개발 및 빌드 명령어 (Commands)
모든 명령어는 `backend/` 디렉토리에서 실행합니다 (Poetry 프로젝트 루트).
- **의존성 설치**: `poetry install`
- **패키지 추가**: `poetry add <패키지명>`
- **로컬 서버 실행**: `poetry run uvicorn apps.main:app --reload`
- **서버 상태 확인**: `curl http://localhost:8000/health-check`
- **린트 검사**: `poetry run ruff check .`

아직 구성된 테스트 스위트는 없습니다.

## 3. 아키텍처 (Architecture)
- **엔트리포인트**: `backend/apps/main.py`에서 `FastAPI` 앱을 생성하고 CORS를 설정하며, `lifespan`을 통해 앱 시작 시 `motor.motor_asyncio.AsyncIOMotorClient`로 MongoDB에 연결해 `app.mongodb_client` / `app.mongodb`에 저장하고, 종료 시 클라이언트를 닫습니다.
- **라우팅**: `backend/apps/api.py`의 `api_router`(`APIRouter`)를 `main.py`가 include합니다. 새 기능 라우터(auth, user 등)는 이 파일에서 `api_router.include_router(...)`로 등록하도록 설계되어 있습니다.
- **설정**: `backend/core/config.py`가 `python-dotenv`로 `.env`의 모든 환경 변수(Mongo URL/DB, JWT 시크릿/만료 시간)를 로드합니다.
- **공통 모듈**: `backend/common/`은 공유 코드를 위한 위치입니다 (현재 `messages.py`는 빈 placeholder).

## 4. 코딩 스타일 및 아키텍처 규칙 (Code Style & Architecture)
- **경로 참조 (Imports)**: 최상위 `backend` 폴더 내부에서 실행되므로, 절대 경로 지정 시 `from backend.apps...` 대신 `from apps...` 또는 `from core...` 형태로 시작해야 합니다.
- **환경 변수 관리**: 데이터베이스 URL이나 AWS 관련 비밀키는 절대 코드에 하드코딩하지 말고, `core/config.py`를 통해 `.env`에서 안전하게 로드하여 사용해야 합니다.
- **린트**: `pyproject.toml`의 `[tool.ruff]` 설정에 따라 `line-length = 79`, `select = ["E", "F", "I"]` (pycodestyle, pyflakes, isort)를 준수합니다. 백엔드 작업을 마치기 전 `poetry run ruff check .`를 실행하세요.
