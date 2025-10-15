from litestar import Litestar
from litestar.status_codes import (
    HTTP_302_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from litestar.testing import TestClient


def test_proxy_login(test_client: TestClient[Litestar]) -> None:
    # This would be a redirect from FC with to the following URL:
    # https://fc-proxy/?code=some-code&state=https%3A%2F%2Fexample.com%2Flogin-callback&iss=https%3A%2F%2Ffcp-low.sbx.dev-franceconnect.fr%2Fapi%2Fv2"
    params = {
        "code": "some-code",
        "state": "https://example.com/login-callback",
        "iss": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2",
    }
    response = test_client.get("/", params=params, follow_redirects=False)

    assert response.status_code == HTTP_302_FOUND
    assert (
        response.headers["location"]
        == "https://example.com/login-callback?code=some-code&state=https%3A%2F%2Fexample.com%2Flogin-callback&iss=https%3A%2F%2Ffcp-low.sbx.dev-franceconnect.fr%2Fapi%2Fv2"
    )


def test_proxy_missing_state(test_client: TestClient[Litestar]) -> None:
    # This would be a redirect from FC with to the following URL:
    # https://fc-proxy/?code=some-code&iss=https%3A%2F%2Ffcp-low.sbx.dev-franceconnect.fr%2Fapi%2Fv2"
    params = {
        "code": "some-code",
        "iss": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2",
    }
    response = test_client.get("/", params=params, follow_redirects=False)

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {
        "error": "No callback URL provided in the `state` parameter (have you set it when querying FC?)"
    }


def test_proxy_bad_state(test_client: TestClient[Litestar]) -> None:
    # This would be a redirect from FC with to the following URL:
    # https://fc-proxy/?code=some-code&state=foobar&iss=https%3A%2F%2Ffcp-low.sbx.dev-franceconnect.fr%2Fapi%2Fv2"
    params = {
        "code": "some-code",
        "state": "foobar",
        "iss": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2",
    }
    response = test_client.get("/", params=params, follow_redirects=False)

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {
        "error": "No callback URL provided in the `state` parameter (have you set it when querying FC?)"
    }


def test_proxy_logout(test_client: TestClient[Litestar]) -> None:
    # This would be a redirect from FC with to the following URL:
    # https://fc-proxy/?state=https%3A%2F%2Fexample.com%2F%3Fis_logged_out
    params = {
        "state": "https://example.com/?is_logged_out",
    }
    response = test_client.get("/", params=params, follow_redirects=False)

    assert response.status_code == HTTP_302_FOUND
    assert (
        response.headers["location"]
        == "https://example.com/?state=https%3A%2F%2Fexample.com%2F%3Fis_logged_out&is_logged_out="
    )
