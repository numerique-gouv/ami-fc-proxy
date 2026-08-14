import pytest
from litestar import Litestar
from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_302_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from litestar.testing import TestClient
from pytest_httpx import HTTPXMock


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
        response.headers["location"] == "https://example.com/login-callback?code=some-code"
        "&state=https%3A%2F%2Fexample.com%2Flogin-callback&iss=https%3A%2F%2Ffcp-low.sbx.dev-franceconnect.fr%2Fapi%2Fv2"
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
    # https://fc-proxy/?state=https%3A%2F%2Fexample.com%2F%3Fis_logged_out#/login
    params = {
        "state": "https://example.com/?is_logged_out#/login",
    }
    response = test_client.get("/", params=params, follow_redirects=False)

    assert response.status_code == HTTP_302_FOUND
    assert (
        response.headers["location"]
        == "https://example.com/?state=https%3A%2F%2Fexample.com%2F%3Fis_logged_out%23%2Flogin&is_logged_out=#/login"
    )


def test_proxy_ami_fi_authorize_request(test_client: TestClient[Litestar]) -> None:
    params = {
        "from_url": "http://review-app1/",
        "fc_url": "http://fc/",
    }
    response = test_client.get("/ami-fi-authorize-request/", params=params, follow_redirects=False)
    assert response.status_code == HTTP_302_FOUND
    assert response.headers["location"] == "http://fc/"

    response = test_client.get("/ami-fi-get-from-url")
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"from_url": "http://review-app1/"}


def test_proxy_ami_fi_authorize_request_missing_params(test_client: TestClient[Litestar]) -> None:
    params: dict[str, str] = {}
    response = test_client.get("/ami-fi-authorize-request/", params=params)
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"error": "Can not redirect to FC authorize endpoint"}

    params = {
        "from_url": "http://review-app1/",
    }
    response = test_client.get("/ami-fi-authorize-request/", params=params)
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"error": "Can not redirect to FC authorize endpoint"}

    params = {
        "fc_url": "http://fc/",
    }
    response = test_client.get("/ami-fi-authorize-request/", params=params)
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"error": "Can not redirect to FC authorize endpoint"}


async def test_proxy_ami_fi_authorize_callback(
    app: Litestar, test_client: TestClient[Litestar], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("litestar.Request.session", {"ami_fi_from_url": "http://review-app1/"})
    response = test_client.get(
        "/ami-fi-authorize-callback/",
        params={"redirect_uri": "https://fc-url/oidc-callback?code=fake-code"},
        follow_redirects=False,
    )
    assert response.status_code == HTTP_302_FOUND
    assert response.headers["location"] == "https://fc-url/oidc-callback?code=fake-code"
    store = app.stores.get("oidc_sessions")
    code = await store.get("fake-code")
    assert code
    assert code.decode() == "http://review-app1/"


def test_proxy_ami_fi_authorize_callback_missing_redirect_uri(
    test_client: TestClient[Litestar],
) -> None:
    response = test_client.get("/ami-fi-authorize-callback/", follow_redirects=False)
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"error": "Can not redirect to FC oidc-callback endpoint"}


def test_proxy_ami_fi_authorize_callback_missing_session(
    test_client: TestClient[Litestar],
) -> None:
    response = test_client.get(
        "/ami-fi-authorize-callback/",
        params={"redirect_uri": "https://fc-url/oidc-callback?code=fake-code"},
        follow_redirects=False,
    )
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"error": "Can not found from_url"}


def test_proxy_ami_fi_authorize_callback_missing_code(
    test_client: TestClient[Litestar], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("litestar.Request.session", {"ami_fi_from_url": "http://review-app1/"})
    response = test_client.get(
        "/ami-fi-authorize-callback/",
        params={"redirect_uri": "https://fc-url/oidc-callback"},
        follow_redirects=False,
    )
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"error": "Can not found code in redirect_uri"}

    response = test_client.get(
        "/ami-fi-authorize-callback/",
        params={"redirect_uri": "https://fc-url/oidc-callback?code="},
        follow_redirects=False,
    )
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"error": "Can not found code in redirect_uri"}


def test_proxy_ami_fi_authorize(
    test_client: TestClient[Litestar], monkeypatch: pytest.MonkeyPatch
) -> None:
    params = {
        "foo": "bar",
    }
    monkeypatch.setattr("litestar.Request.session", {"ami_fi_from_url": "http://review-app1/"})
    response = test_client.get("/api/v1/fi/authorize/", params=params, follow_redirects=False)
    assert response.status_code == HTTP_302_FOUND
    assert response.headers["location"] == "http://review-app1/api/v1/fi/authorize/?foo=bar"


def test_proxy_ami_fi_authorize_missing_session(test_client: TestClient[Litestar]) -> None:
    response = test_client.get("/api/v1/fi/authorize/", params={}, follow_redirects=False)
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"error": "Can not redirect to FI authorize endpoint"}


async def test_proxy_ami_fi_token(
    app: Litestar,
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
    store = app.stores.get("oidc_sessions")
    await store.set("fake-code", "http://review-app1/", expires_in=500)
    httpx_mock.add_response(json={"access_token": "fake-access-token"})
    params = {"code": "fake-code"}
    response = test_client.post("/api/v1/fi/token/", data=params, follow_redirects=False)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"access_token": "fake-access-token"}
    store = app.stores.get("oidc_sessions")
    access_token = await store.get("fake-access-token")
    assert access_token
    assert access_token.decode() == "http://review-app1/"


def test_proxy_ami_fi_token_missing_code(test_client: TestClient[Litestar]) -> None:
    with pytest.raises(Exception) as e:
        test_client.post("/api/v1/fi/token/", data={}, follow_redirects=False)
    assert str(e.value) == "Can not found code in query"


async def test_proxy_ami_fi_token_missing_from_url(
    app: Litestar,
    test_client: TestClient[Litestar],
) -> None:
    store = app.stores.get("oidc_sessions")
    await store.set("another-fake-code", "from_url", expires_in=500)
    params = {"code": "fake-code"}
    with pytest.raises(Exception) as e:
        test_client.post("/api/v1/fi/token/", data=params, follow_redirects=False)
    assert str(e.value) == "Can not found from_url in storage"


async def test_proxy_ami_fi_userinfo(
    app: Litestar,
    test_client: TestClient[Litestar],
    httpx_mock: HTTPXMock,
) -> None:
    store = app.stores.get("oidc_sessions")
    await store.set("fake-access-token", "http://review-app1/", expires_in=500)
    httpx_mock.add_response(json={"foo": "bar"})
    headers = {"authorization": "Bearer fake-access-token"}
    response = test_client.get("/api/v1/fi/userinfo/", headers=headers, follow_redirects=False)
    assert response.status_code == HTTP_200_OK
    assert response.json() == {"foo": "bar"}


def test_proxy_ami_fi_userinfo_missing_authorization_header(
    test_client: TestClient[Litestar],
) -> None:
    with pytest.raises(Exception) as e:
        test_client.get("/api/v1/fi/userinfo/", follow_redirects=False)
    assert str(e.value) == "Missing authorization header"


def test_proxy_ami_fi_userinfo_wrong_format_authorization_header(
    test_client: TestClient[Litestar],
) -> None:
    headers = {"authorization": "wrong-format-authorization-header"}
    with pytest.raises(Exception) as e:
        test_client.get("/api/v1/fi/userinfo/", headers=headers, follow_redirects=False)
    assert str(e.value) == "Wrong format authorization header"


async def test_proxy_ami_fi_userinfo_missing_from_url(
    app: Litestar,
    test_client: TestClient[Litestar],
) -> None:
    store = app.stores.get("oidc_sessions")
    await store.set("another-fake-access-token", "from_url", expires_in=500)
    headers = {"authorization": "Bearer fake-access-token"}
    with pytest.raises(Exception) as e:
        test_client.get("/api/v1/fi/userinfo/", headers=headers, follow_redirects=False)
    assert str(e.value) == "Can not found from_url in storage"


def test_proxy_ami_fi_logout(
    test_client: TestClient[Litestar], monkeypatch: pytest.MonkeyPatch
) -> None:
    params = {
        "post_logout_redirect_uri": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2/client/logout-callback",
        "state": "fake-state",
    }
    monkeypatch.setattr("litestar.Request.session", {"ami_fi_from_url": "http://review-app1/"})
    response = test_client.get("/api/v1/fi/logout/", params=params, follow_redirects=False)
    assert response.status_code == HTTP_302_FOUND
    assert response.headers["location"] == (
        "http://review-app1/api/v1/fi/logout/"
        "?post_logout_redirect_uri=https%3A%2F%2Ffcp-low.sbx.dev-franceconnect.fr%2Fapi%2Fv2%2Fclient%2Flogout-callback&state=fake-state"
    )


def test_proxy_ami_fi_logout_missing_session_and_post_logout_redirect_uri(
    test_client: TestClient[Litestar],
) -> None:
    response = test_client.get("/api/v1/fi/logout/", params={}, follow_redirects=False)
    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {"error": "Can not redirect to FI logout endpoint"}


def test_proxy_ami_fi_logout_missing_session(test_client: TestClient[Litestar]) -> None:
    params = {
        "post_logout_redirect_uri": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2/client/logout-callback",
    }
    response = test_client.get("/api/v1/fi/logout/", params=params, follow_redirects=False)
    assert response.status_code == HTTP_302_FOUND
    assert (
        response.headers["location"]
        == "https://fcp-low.sbx.dev-franceconnect.fr/api/v2/client/logout-callback?state="
    )

    params = {
        "post_logout_redirect_uri": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2/client/logout-callback",
        "state": "fake-state",
    }
    response = test_client.get("/api/v1/fi/logout/", params=params, follow_redirects=False)
    assert response.status_code == HTTP_302_FOUND
    assert (
        response.headers["location"]
        == "https://fcp-low.sbx.dev-franceconnect.fr/api/v2/client/logout-callback?state=fake-state"
    )
