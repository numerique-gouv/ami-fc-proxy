import pytest


@pytest.mark.django_db
def test_proxy_ami_fi_authorize(client) -> None:
    session = client.session
    session["ami_fi_from_url"] = "http://review-app1/"
    session.save()

    data = {
        "foo": "bar",
    }
    response = client.get("/api/v1/fi/authorize/", data=data)
    assert response.status_code == 302
    assert response.headers["location"] == "http://review-app1/api/v1/fi/authorize/?foo=bar"


def test_proxy_ami_fi_authorize_missing_session(client) -> None:
    response = client.get("/api/v1/fi/authorize/", data={}, status=500)
    assert response.json() == {"error": "Can not redirect to FI authorize endpoint"}
