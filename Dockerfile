FROM python:3.12.0-alpine

ENV PYTHONUNBUFFERED 1
ENV DOCKER 1

WORKDIR /usr/src/app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
