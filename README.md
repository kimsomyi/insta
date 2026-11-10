# insta PJT

- 프로젝트 세팅
```
uv init insta --bare --python 3.14
```

- 필요한 라이브러리 설치
```
uv add "fastapi[standard]" sqlalchemy "psycopg[binary]" alembic
```

- 데이터 베이스 생성
```
psql -d postgres # macOS
psql -U postgres # window

CREATE DATABASE insta OWNER sd4;
```

- 환경변수 설정
```
# .env.example 을 복사해서 .env 를 만들고, 내 DB 정보로 채우기
cp .env.example .env
```


- alembic init
```
uv run alembic init alembic
```

- alembic revision
```
uv run alembic revision --autogenerate -m "create posts"
```

- alembic upgrade
```
uv run alembic upgrade head
```

- alembic downgrade
```
uv run alembic downgrade -1
```

- alembic history
```
uv run alembic history
```