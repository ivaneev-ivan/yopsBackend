FROM python:3.12-alpine

WORKDIR /usr/src/app

# переменные окружения для python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir poetry
COPY pyproject.toml .
COPY poetry.lock .
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root
COPY . .
CMD ["./wsgi-entrypoint.sh"]