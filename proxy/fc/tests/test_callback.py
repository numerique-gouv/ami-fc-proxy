def test_proxy_login(client) -> None:
    # This would be a redirect from FC with to the following URL:
    # https://fc-proxy/?code=some-code&state=https%3A%2F%2Fexample.com%2Flogin-callback&iss=https%3A%2F%2Ffcp-low.sbx.dev-franceconnect.fr%2Fapi%2Fv2"
    data = {
        "code": "some-code",
        "state": "https://example.com/login-callback",
        "iss": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2",
    }
    response = client.get("/", data=data)

    assert response.status_code == 302
    assert (
        response.headers["location"] == "https://example.com/login-callback?code=some-code&"
        "state=https%3A%2F%2Fexample.com%2Flogin-callback&iss=https%3A%2F%2Ffcp-low.sbx.dev-franceconnect.fr%2Fapi%2Fv2"
    )


def test_proxy_missing_state(client) -> None:
    # This would be a redirect from FC with to the following URL:
    # https://fc-proxy/?code=some-code&iss=https%3A%2F%2Ffcp-low.sbx.dev-franceconnect.fr%2Fapi%2Fv2"
    data = {
        "code": "some-code",
        "iss": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2",
    }
    response = client.get("/", data=data)

    assert response.status_code == 500
    assert response.json() == {
        "error": "No callback URL provided in the `state` parameter (have you set it when querying FC?)"
    }


def test_proxy_bad_state(client) -> None:
    # This would be a redirect from FC with to the following URL:
    # https://fc-proxy/?code=some-code&state=foobar&iss=https%3A%2F%2Ffcp-low.sbx.dev-franceconnect.fr%2Fapi%2Fv2"
    data = {
        "code": "some-code",
        "state": "foobar",
        "iss": "https://fcp-low.sbx.dev-franceconnect.fr/api/v2",
    }
    response = client.get("/", data=data)

    assert response.status_code == 500
    assert response.json() == {
        "error": "No callback URL provided in the `state` parameter (have you set it when querying FC?)"
    }


def test_proxy_logout(client) -> None:
    # This would be a redirect from FC with to the following URL:
    # https://fc-proxy/?state=https%3A%2F%2Fexample.com%2F%3Fis_logged_out
    data = {
        "state": "https://example.com/?is_logged_out",
    }
    response = client.get("/", data=data)

    assert response.status_code == 302
    assert (
        response.headers["location"]
        == "https://example.com/?state=https%3A%2F%2Fexample.com%2F%3Fis_logged_out&is_logged_out="
    )
