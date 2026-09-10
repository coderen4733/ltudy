"""Alembic 마이그레이션 실행 환경 설정 파일.

`alembic revision --autogenerate` / `alembic upgrade` 같은 명령을 실행하면
Alembic이 이 파일을 먼저 읽어서 "어떤 DB에, 어떤 모델을 기준으로"
작업할지 결정합니다.
"""

import asyncio
import os
import sys
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from alembic import context

# --------------------------------------------------------------------------
# 0. backend 폴더를 import 경로에 추가
#    - 이 파일은 backend/alembic/env.py 이므로, 상위 폴더(backend)를
#      sys.path에 넣어줘야 `from core...`, `from apps...` import가 동작함
# --------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# --------------------------------------------------------------------------
# 1. 우리 프로젝트의 설정/모델 불러오기
#    - 경로 추가(0번) 이후에 import 해야 하므로 여기서 import 함 (E402 무시)
#    - ✅ [중요] 새 모델 파일을 만들 때마다 여기에 import 를 한 줄 추가해야
#      autogenerate가 그 테이블을 인식합니다.
#      (import 만 해두면 SQLModel.metadata 에 테이블 정보가 등록됨)
# --------------------------------------------------------------------------
from apps.test import model  # noqa: E402, F401  (테스트 CRUD 모델)
from core.db import ASYNC_DB_URL  # noqa: E402  (정규화된 DB 접속 주소)

# --------------------------------------------------------------------------
# 2. Alembic 기본 설정
# --------------------------------------------------------------------------
# alembic.ini 의 값에 접근하기 위한 객체
config = context.config

# alembic.ini 에 적힌 로깅 설정을 적용
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# autogenerate 가 "현재 코드의 모델 구조"로 삼을 기준
# - SQLModel 로 정의한 모든 테이블 정보가 SQLModel.metadata 에 모여 있음
target_metadata = SQLModel.metadata


# --------------------------------------------------------------------------
# 3. 오프라인 모드: DB에 연결하지 않고 SQL 문만 출력 (`--sql` 옵션)
# --------------------------------------------------------------------------
def run_migrations_offline() -> None:
    context.configure(
        url=ASYNC_DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # 컬럼 "타입" 변경도 감지
    )

    with context.begin_transaction():
        context.run_migrations()


# --------------------------------------------------------------------------
# 4. 온라인 모드: 실제 DB에 연결해서 마이그레이션 실행 (기본 동작)
# --------------------------------------------------------------------------
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # 컬럼 "타입" 변경도 감지
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    # 앱 본체(core/db.py)와 동일한 비동기 드라이버(asyncpg)로 접속
    # - Supabase 커넥션 풀러 호환을 위해 statement 캐시를 끔
    # - 마이그레이션은 커넥션 풀이 필요 없으므로 NullPool 사용
    connectable = create_async_engine(
        ASYNC_DB_URL,
        poolclass=pool.NullPool,
        connect_args={"statement_cache_size": 0},
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# --------------------------------------------------------------------------
# 5. 모드에 따라 실행
# --------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
