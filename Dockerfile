FROM python:3.8-slim-buster

COPY . /app

RUN cd /app

WORKDIR /app

RUN python3 -m pip install -r requirements.txt

CMD ["python3", "main.py"]