FROM python:3.12-alpine3.19
LABEL maintainer="gamjass"

ENV PYTHONUNBUFFERED 1
ENV DISPLAY=:99

# 설치에 필요한 패키지 설치
RUN apk update && apk add --no-cache \
    jpeg-dev \
    zlib-dev \
    libffi-dev \
    build-base

# 필요에 따라 추가적인 패키지 설치
# RUN apk add --no-cache <additional-packages>

ENV PYTHONPATH="/app"

# 설치된 패키지로 pip 설치
WORKDIR /app
RUN pip install poetry

# pyproject.toml 및 poetry.lock 파일 복사
COPY pyproject.toml poetry.lock ./

# 의존성 설치 (가상 환경 생성 및 의존성 설치)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Daphne, Gunicorn 설치
RUN pip install daphne gunicorn

# 프로젝트 코드 복사
COPY . .

RUN chmod -R 777 /app

# # PostgreSQL 클라이언트 설치
# RUN apk update && apk add --no-cache postgresql-client

# 사용자 추가 및 /app 디렉토리 소유권 변경
RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user \
    && chown -R django-user:django-user /app  # /app 디렉토리 소유권 변경

EXPOSE 8000 8001

ARG DEV=false

## Django 애플리케이션 실행
#CMD ["python", "api/manage.py", "runserver", "0.0.0.0:8000"]

USER django-user