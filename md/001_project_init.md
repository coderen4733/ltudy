## Project 시작
- poetry를 활용하여 필요한 것들을 설치 및 관리한다.
- Uvicorn과 FastAPI를 활용하여 웹 서버를 구동한다.

## DB 연결
- Supabase에서 제공하는 무료티어 Postgresql DB를 사용한다.
- DB URL(DB Password 포함)은 .env에서 core/config.py를 통해 가져온다.
- ORM은 SQLModel을 사용한다.

## Redis 연결
- Redis Cloud 무료티어를 사용한다.
- Redis_URL(Redis Password 포함)은 .env에서 core/config.py를 통해 가져온다.
