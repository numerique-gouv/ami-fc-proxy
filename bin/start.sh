#!/bin/bash

PORT="${PORT:-8000}"
HOSTNAME="${HOSTNAME:-127.0.0.1}"
RUN=""

if [ -z "$CONTAINER" ]
then
  SSL="${SSL:---ssl-keyfile=ssl-key.pem --ssl-certfile=ssl-cert.pem}"
  RUN="uv run"
fi

${RUN} litestar run -p ${PORT} -H ${HOSTNAME} ${RELOAD} ${DEBUG} ${SSL}
