FROM python:3.9-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN \
    set -ex \
 && apt-get update -yqq \
 && apt-get install -yqq --no-install-recommends \
 xfonts-75dpi \
 xfonts-base \
 &&  pip install -r requirements.txt \
 && wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.buster_amd64.deb \
 && dpkg -i wkhtmltox_0.12.6-1.buster_amd64.deb

COPY frontend.py frontend.py
COPY backend.py backend.py

ENV \
 FRONTEND_PORT=8013 \
 MAX_THREADS=3 \
 LOGFILE=/var/log/nspc.log \
 RABBIT_HOST=rabbithost \
 RABBIT_QUEUE=0 \
 RABBIT_USER=guest \
 RABBIT_PASS=guest \
 REDIS_PORT=6379 \
 REDIS_HOST=redishost \
 REDIS_DB=0

ENTRYPOINT ["python3"]
