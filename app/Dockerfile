# syntax=docker/dockerfile:1
FROM python:3.10-alpine
WORKDIR /FlaskApp
RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt

EXPOSE 5000
COPY . .
CMD ["flask", "run", "--debug", "--host=0.0.0.0"]