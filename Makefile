ifdef CONTAINER
  # We're on scalingo, don't use uv
  RUN :=
else
  RUN := uv run
endif

.PHONY: lint-and-format
lint-and-format:
	uv run pre-commit run --all-files

.PHONY: dev
dev: ssl-key.pem
	$(RUN) uvicorn proxy.asgi:application --reload --ssl-keyfile ssl-key.pem --ssl-certfile ssl-cert.pem --host localhost --port 8000

.PHONY: test
test:
	DJANGO_SETTINGS_MODULE=proxy.settings $(RUN) pytest -vvv -ll --ff -x --reuse-db proxy

.PHONY: test-create-db
test-create-db:
	DJANGO_SETTINGS_MODULE=proxy.settings $(RUN) pytest -vvv -ll --ff -x --reuse-db proxy --create-db

.PHONY: test-ci
test-ci:
	DJANGO_SETTINGS_MODULE=proxy.settings $(RUN) pytest proxy

.PHONY: migrate
migrate:
	$(RUN) python manage.py migrate
