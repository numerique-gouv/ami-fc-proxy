import pytest


@pytest.mark.django_db
def test_proxy_ami_fi_authorize_request(client) -> None:
    data = {
        "from_url": "http://review-app1/",
        "fc_url": "http://fc/",
    }
    response = client.get("/ami-fi-authorize-request/", data=data)
    assert response.status_code == 302
    assert response.headers["location"] == "http://fc/"
    assert client.session["ami_fi_from_url"] == "http://review-app1/"

    response = client.get("/ami-fi-get-from-url")
    assert response.json() == {"from_url": "http://review-app1/"}


def test_proxy_ami_fi_authorize_request_missing_params(client) -> None:
    data = {}
    response = client.get("/ami-fi-authorize-request/", data=data)
    assert response.status_code == 500
    assert response.json() == {"error": "Can not redirect to FC authorize endpoint"}

    data = {
        "from_url": "http://review-app1/",
    }
    response = client.get("/ami-fi-authorize-request/", data=data)
    assert response.status_code == 500
    assert response.json() == {"error": "Can not redirect to FC authorize endpoint"}

    data = {
        "fc_url": "http://fc/",
    }
    response = client.get("/ami-fi-authorize-request/", data=data)
    assert response.status_code == 500
    assert response.json() == {"error": "Can not redirect to FC authorize endpoint"}
