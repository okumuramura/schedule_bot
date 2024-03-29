FROM python:3.9-slim

WORKDIR /usr/src/app

ENV PYTHONBUFFERED=1 \
    PYTHONPATH=/usr/src/app

COPY requirements.txt .

RUN pip install -r requirements.txt && \
    pip install psycopg2-binary

COPY . .
