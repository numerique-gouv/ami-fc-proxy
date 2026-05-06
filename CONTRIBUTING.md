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

## Database Setup

This project uses PostgreSQL for both development and testing. Follow these steps to set up the database locally using Docker:

### 1. Start PostgreSQL Container

```shell
docker run --name ami-fc-proxy-postgres \
  -e POSTGRES_PASSWORD=some_password \
  -e POSTGRES_DB=postgres \
  -p 5432:5432 \
  -d postgres:15
```

### 2. Create Test Database

The test suite requires a separate test database:

```shell
docker exec -it ami-postgres psql -U postgres -c "CREATE DATABASE postgres_test;"
```

### 3. Configure Environment

There's a `.env` file that holds all the default env variable values.
For any specific env variables, create (or edit) a `.env.local` file. Anything in here
will overload what's in the `.env` file.

For example you'll need to overload the FranceConnect secrets for AMI and RVO in
your `.env.local` file.

On the front end, Vite uses dotenv to load additional environment variables
from the following files in your environment directory, in this order:

    .env # loaded in all cases
    .env.local # loaded in all cases, ignored by git
    .env.development # loaded only in development, values should be overloaded on Scalingo
    .env.development.local # loaded only in development, ignored by git

### 4. Run Database Migrations

Apply the database schema:

```shell
make migrate
```

### 5. Verify Setup

Run the tests to ensure everything is working:

```shell
make test
```

### Managing the Database Container

- **Stop the container:** `docker stop ami-fc-proxy-postgres`
- **Start the container:** `docker start ami-fc-proxy-postgres`
- **Remove the container:** `docker rm ami-fc-proxy-postgres` (you'll need to recreate it and the test database)

### Managing the database schema changes (migrations)

The base command to run the migrations and update to the latest database schema is:
```sh
make migrate
```

##### Changing the database schema

When changing the models, create a new migration to reflect those changes in
the database:
```sh
uv run manage.py makemigrations <app> --name <explicit_migration_name>
```

This should generate a migration file in `<app>/migrations/<some
id>_explicit_migration_name.py`, which you'll then modify according to your
needs.

It should already have some code automatically generated to accomodate the
changes.

##### Rolling back a schema change

To list the existing migrations:
```sh
uv run manage.py showmigrations
```

Then, to target a revision (version):
```sh
uv run manage.py migrate <app> <some id>
```

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
