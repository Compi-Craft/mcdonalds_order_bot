FROM python:3.12-slim

# Встановити потрібну версію Poetry
ENV POETRY_VERSION=2.1.3
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

# Копіюємо файли конфігурації
COPY pyproject.toml poetry.lock* /app/

# Встановлюємо залежності (без інсталяції root-пакету)
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root

# Копіюємо весь код
COPY . /app
