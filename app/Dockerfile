# syntax=docker/dockerfile:1
FROM python:3.10
WORKDIR /app

COPY requirements.txt /app
RUN pip install -U pip
RUN pip install -r requirements.txt

EXPOSE 8000
COPY . .
CMD ["flask", "run", "--debug", "--host=0.0.0.0"]