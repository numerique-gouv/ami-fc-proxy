# FranceConnect (login/logout) proxy

This is a proxy for [FranceConnect](https://docs.partenaires.franceconnect.gouv.fr/).

As we're working on the [AMI](github.com/numerique-gouv/ami-notifications-api)
project, and deploying review apps on Scalingo, we were met with the pain of
going through many manual and error-prone steps to configure the redirect URLs
and sector identifier URL in our FC partner's page and in env variables.

This was defeating some of the benefits of the automation provided by our
continuous integration.

Thus this project came to be: a simple login and logout proxy for FranceConnect.

## Setup

To use this project, you'll need to deploy it (eg on Scalingo), and in your
project using FranceConnect, use its URL for the login and logout requests.

For this proxy to work, the final expected
[redirect_uri](https://docs.partenaires.franceconnect.gouv.fr/fs/fs-technique/fs-technique-endpoints/#authorization-endpoint)
needs to be provided in the `state` parameter when querying FC through the proxy.


Here's an example query for the login from `https://example.com` to the FC services
through a proxy deployed on `https://fc-proxy`:

```
https://fcp-low.sbx.dev-franceconnect.fr/api/v2/authorize?scope=email&redirect_uri=https%3A%2F%2Ffc-proxy&response_type=code&client_id=fb9615294c746145edd857b4edbeb4996e316ae1712ed2bb361150a1e6cd8c6f&state=https%3A%2F%2Fexample.com%2Flogin-callback&nonce=not-implemented-yet-and-has-more-than-32-chars&acr_values=eidas1&prompt=login
```

Note the presence of the (urlencoded) proxy url in the `redirect_uri` query
parameter, and the "real" redirect uri `https://example.com/login-callback` in
the `state` query parameter.


## Tech stack

### Language: python

[python](https://docs.python.org) using
[pyright](https://github.com/microsoft/pyright).

### Package and project manager: uv

[uv](https://docs.astral.sh/uv/) is "An extremely fast Python package and
project manager, written in Rust.", and is used to setup and manage the project.

Please follow the [installation
instructions](https://docs.astral.sh/uv/getting-started/installation/) to set it
up on your machine.

Once it's installed, it should be used for everything project related:
- adding more dependencies: `uv add (--dev) <dependency, eg: requests>`
- running a script (or editor) in the project's python environment: `uv run
<command, eg: code>`

### Linter and formatter: ruff

[ruff](https://docs.astral.sh/ruff/) is "An extremely fast Python linter and
code formatter, written in Rust."

Ruff is used both for linting and formatting:
```shell
make lint-and-format
```

### Tests

The easiest way to run tests is to use the Makefile target:
```
make test
```

You'll find detailed commands and usage in the [CONTRIBUTING.md](CONTRIBUTING.md) file.


### Contributing

Please check the [CONTRIBUTING.md](CONTRIBUTING.md) file.
