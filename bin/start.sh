#!/bin/bash

PORT="${PORT:-8000}"
HOSTNAME="${HOSTNAME:-127.0.0.1}"
RUN=""

if [ -z "$CONTAINER" ]
then
  SSL="${SSL:---ssl-keyfile=ssl-key.pem --ssl-certfile=ssl-cert.pem}"
  RUN="uv run"
fi

make migrate && gunicorn ami.asgi:application --bind ${HOST}:${PORT} --worker-class uvicorn.workers.UvicornWorker --forwarded-allow-ips="*" --log-file -
