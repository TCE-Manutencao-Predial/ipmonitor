FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y make

COPY . .

RUN make setup

EXPOSE 8000

ENV CONFIG=docker

CMD [ "./.venv/bin/waitress-serve", "--host", "0.0.0.0", "--port", "8000", "config:app" ]

