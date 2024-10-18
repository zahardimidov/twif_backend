FROM python:3.10-alpine

RUN apk add --no-cache gcc musl-dev

WORKDIR /backend

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD python run.py