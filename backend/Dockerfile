FROM python:3.9-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY backend.py backend.py

ENV \
 MAX_THREADS=3 \
 LOGFILE=/var/log/nspc.log \
 RABBIT_HOST=rabbithost \
 RABBIT_QUEUE=0 \
 RABBIT_USER=guest \
 RABBIT_PASS=guest \
 REDIS_PORT=6379 \
 REDIS_HOST=redishost \
 REDIS_DB=0

CMD ["python3", "backend.py"]
