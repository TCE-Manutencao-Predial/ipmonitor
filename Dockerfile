FROM python:3

WORKDIR /app

COPY requirements.txt .

COPY . .

RUN make setup

EXPOSE 5000

ENV CONFIG=docker

CMD [ "make", "run" ]

