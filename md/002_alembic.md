# 002. Alembic (DB 마이그레이션)

## 왜 쓰는가
- SQLModel 모델(`class Post` 등)을 수정해도, **이미 만들어진 DB 테이블은 자동으로 바뀌지 않는다.**
- 예: `Post`에 `author` 컬럼을 추가해도 Supabase의 `test_post` 테이블에는 아무 변화가 없음.
- Alembic은 "모델의 현재 모습"과 "실제 DB의 모습"을 비교해서, 그 차이를 메꾸는 SQL을 **파이썬 파일(마이그레이션)로 기록**해 준다.
- 이 파일을 git에 커밋하면 팀원 모두가 `alembic upgrade head` 한 번으로 똑같은 DB 구조를 맞출 수 있다.

## 구성 (backend/ 기준)
- `alembic.ini` : Alembic 설정 파일. **DB 주소는 여기 적지 않는다.**
- `alembic/env.py` : 마이그레이션 실행 환경. `core/db.py`의 `ASYNC_DB_URL`(= `.env`의 `SBDB_URL`)과 `SQLModel.metadata`를 불러와서 사용한다.
- `alembic/script.py.mako` : 마이그레이션 파일 템플릿. (`import sqlmodel` 한 줄이 추가돼 있음)
- `alembic/versions/*.py` : 실제 마이그레이션 파일들. **반드시 git에 커밋한다.**

## 기본 사용법
모든 명령은 `backend/` 디렉토리에서 실행한다.

### 1) 모델을 바꾼 뒤 → 마이그레이션 파일 생성
```bash
poetry run alembic revision --autogenerate -m "post에 author 컬럼 추가"
```
- `alembic/versions/`에 새 파일이 생긴다.
- **생성된 파일을 꼭 열어서 확인한다.** (autogenerate가 완벽하지 않음. 특히 컬럼 이름 변경은 "삭제 후 추가"로 잘못 잡을 수 있음)

### 2) 마이그레이션을 실제 DB에 적용
```bash
poetry run alembic upgrade head
```

### 3) 되돌리기 (직전 1단계)
```bash
poetry run alembic downgrade -1
```

### 상태 확인용 명령
```bash
poetry run alembic current   # 지금 DB가 어느 버전인지
poetry run alembic history   # 마이그레이션 목록
poetry run alembic check     # 모델과 DB가 일치하는지 (CI에서 유용)
```

## 새 모델을 추가했다면
`alembic/env.py`의 `# 1. 우리 프로젝트의 설정/모델 불러오기` 부분에
그 모델 모듈을 import 하는 줄을 추가해야 autogenerate가 인식한다.
```python
from apps.test import model  # noqa: E402, F401
from apps.user import model as user_model  # noqa: E402, F401  ← 이런 식으로 추가
```

## 주의사항
- `core/db.py`에는 더 이상 `create_all`이 없다. 테이블 생성/변경은 **전부 Alembic 담당**이다.
- 새로 프로젝트를 받은 사람은 `.env` 세팅 후 `poetry run alembic upgrade head`를 먼저 실행해야 테이블이 만들어진다.
- Supabase 접속 주소는 **Session pooler(5432)** 를 권장한다. (Transaction pooler(6543)는 DDL 작업에서 문제가 생길 수 있음)
- 마이그레이션 파일(`alembic/versions/*.py`)은 자동 생성 코드라 ruff 린트 대상에서 제외돼 있다. (`pyproject.toml`의 `extend-exclude`)
