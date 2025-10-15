# CONTRIBUTING

Thanks for wanting to contribute to the project!

## Initial Setup

The very first thing you'll need to do is to install
[uv](https://docs.astral.sh/uv/), the package manager, and install all the
project dependencies using

```shell
uv sync
```

The next good step is to enable the pre-commit hooks we use to format and lint
the project, for optimum consistency and readability between all the devs:

```shell
uv run pre-commit install
```

This will make sure each and every commit are up to par with our coding habits.

To run it manually:

```shell
uv run pre-commit run --all-files
```

Or simply use the `Makefile` target:

```shell
make lint-and-format
```

The commands executed by the `pre-commit` call are all configured in the
[.pre-commit-config.yaml](.pre-commit-config.yaml) file.

## Running tests

Running tests is as easy as:
```sh
make test
```

If you'd rather run the tests manually, copy and paste the command from the Makefile:
```
uv run pytest
```

To run a single test, you would use something like:
```
uv run pytest tests/test_foo.py::test_bar
```
