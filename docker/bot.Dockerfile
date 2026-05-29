FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry==1.8.0

COPY pyproject.toml ./

RUN poetry config virtualenvs.create false && \
    poetry lock --no-update && \
    poetry install --no-interaction --no-ansi --no-root

COPY . .

CMD ["python", "-m", "app.main"]
