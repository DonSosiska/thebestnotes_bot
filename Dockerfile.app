
ARG PYTHON_VERSION=3.8

FROM python:${PYTHON_VERSION}

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY . .

RUN pip install --upgrade pip && \
    pip install telebot && \
    pip install mysql-connector-python
