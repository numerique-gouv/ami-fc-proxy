.PHONY: lint-and-format
lint-and-format:
	uv run pre-commit run --all-files

.PHONY: dev
dev:
	RELOAD="-r" DEBUG="--debug" HOSTNAME="0.0.0.0" bin/start.sh

.PHONY: serve
serve:
	bin/start.sh

.PHONY: test
test:
	uv run pytest
