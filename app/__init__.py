from typing import Any
from urllib.parse import parse_qs, unquote, urlparse, urlunparse

from httpx import AsyncClient
from litestar import (
    Litestar,
    Request,
    Response,
    get,
    post,
)
from litestar.config.cors import CORSConfig
from litestar.middleware.session.client_side import CookieBackendConfig
from litestar.response.redirect import Redirect
from litestar.status_codes import (
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from litestar.stores.memory import MemoryStore

cors_config = CORSConfig(allow_origins=["*"])
session_config = CookieBackendConfig(secret=b"34682223291bc7c0736507d1b91288bd")


# ENDPOINTS


@get(path="/", include_in_schema=False)
async def fc_proxy(query: dict[str, str]) -> Response[Any]:
    if "state" not in query or not query["state"].startswith("http"):
        details = {
            "error": "No callback URL provided in the `state` parameter (have you set it when querying FC?)"
        }
        return Response(details, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    # Unquote the redirect url provided in the state query parameter:
    # https%3A%2F%2Flocalhost%3A5173%2F%3Fis_logged_out => https://localhost:5173/?is_logged_out.
    state_redirect_url = unquote(query["state"])
    # Parse the redirect url provided in the `state` query param.
    parsed = urlparse(state_redirect_url)
    # Parse the provided redirect url's query params into a dict.
    redirect_url_query = parse_qs(parsed.query, keep_blank_values=True)
    # We'll reconstruct the query params, so strip them from the provided redirect url.
    without_query_params = parsed._replace(query="")
    # Reconstruct (unparse) the redirect url, without its query parameters.
    redirect_url = urlunparse(without_query_params)
    all_query_params = {**query, **redirect_url_query}
    return Redirect(redirect_url, query_params=all_query_params)


@get(path="/ami-fi-authorize-request/", include_in_schema=False)
async def ami_fi_authorize_request(
    request: Request[Any, Any, Any], query: dict[str, str]
) -> Response[Any]:
    if "from_url" not in query or "fc_url" not in query:
        details = {"error": "Can not redirect to FC authorize endpoint"}
        return Response(details, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    request.session["ami_fi_from_url"] = query["from_url"]
    return Redirect(query["fc_url"])


@get(path="/ami-fi-authorize-callback/", include_in_schema=False)
async def ami_fi_authorize_callback(
    request: Request[Any, Any, Any], query: dict[str, str]
) -> Response[Any]:
    if "redirect_uri" not in query:
        details = {"error": "Can not redirect to FC oidc-callback endpoint"}
        return Response(details, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    store = request.app.stores.get("oidc_sessions")
    from_url = request.session.get("ami_fi_from_url")
    if not from_url:
        details = {"error": "Can not found from_url"}
        return Response(details, status_code=HTTP_500_INTERNAL_SERVER_ERROR)

    redirect_uri = unquote(query["redirect_uri"])
    parsed = urlparse(redirect_uri)
    redirect_uri_query = parse_qs(parsed.query)
    code = redirect_uri_query.get("code")
    if not code:
        details = {"error": "Can not found code in redirect_uri"}
        return Response(details, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    await store.set(code[0], from_url, expires_in=300)
    return Redirect(redirect_uri)


@get(path="/ami-fi-get-from-url/", include_in_schema=False)
async def ami_fi_get_from_url(request: Request[Any, Any, Any]) -> dict[str, str]:
    return {"from_url": request.session.get("ami_fi_from_url") or ""}


@get(path="/api/v1/fi/authorize/", include_in_schema=False)
async def ami_fi_authorize(request: Request[Any, Any, Any], query: dict[str, str]) -> Response[Any]:
    from_url = request.session.get("ami_fi_from_url")
    if not from_url:
        details = {"error": "Can not redirect to FI authorize endpoint"}
        return Response(details, status_code=HTTP_500_INTERNAL_SERVER_ERROR)
    redirect_url = f"{from_url}api/v1/fi/authorize/"
    return Redirect(redirect_url, query_params=query)


@post(path="/api/v1/fi/token/", include_in_schema=False)
async def ami_fi_token(request: Request[Any, Any, Any], query: dict[str, str]) -> Response[Any]:
    code = query.get("code")
    if not code:
        raise Exception("Can not found code in query")
    store = request.app.stores.get("oidc_sessions")
    from_url = await store.get(code)
    if not from_url:
        raise Exception("Can not found from_url in storage")

    async with AsyncClient() as client:
        response = await client.post(
            f"{from_url.decode()}api/v1/fi/token/",
            params=query,
        )
    return Response(
        response.json(),
        status_code=response.status_code,
    )


# APP


def exception_handler(_: Request[Any, Any, Any], exc: Exception):
    print(exc)
    raise exc


def create_app() -> Litestar:
    return Litestar(
        route_handlers=[
            fc_proxy,
            ami_fi_authorize_request,
            ami_fi_authorize_callback,
            ami_fi_get_from_url,
            ami_fi_authorize,
            ami_fi_token,
        ],
        cors_config=cors_config,
        middleware=[session_config.middleware],
        stores={"oidc_sessions": MemoryStore()},
        exception_handlers={Exception: exception_handler},
    )
