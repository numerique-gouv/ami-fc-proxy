#!/bin/bash

PORT="${PORT:-8000}"
HOSTNAME="${HOSTNAME:-127.0.0.1}"
RUN=""

if [ ! -z "$CONTAINER" ]
then
  # We're on scalingo, don't use uv
  RUN=""
else
  if [ ! -f .env.local ]
  then
    # Create an empty file so uv won't fail on a missing file
    touch .env.local
  fi

  SSL="${SSL:---ssl-keyfile=ssl-key.pem --ssl-certfile=ssl-cert.pem}"
  RUN="uv run --env-file .env --env-file .env.local"
fi

${RUN} litestar run -p ${PORT} -H ${HOSTNAME} ${RELOAD} ${DEBUG} ${SSL}
