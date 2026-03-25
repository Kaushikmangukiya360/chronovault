FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \
    pip install -e .[dev]

CMD ["chronovault", "--help"]
