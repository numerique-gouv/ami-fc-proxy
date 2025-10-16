from typing import Any
from urllib.parse import parse_qs, unquote, urlparse, urlunparse

from litestar import (
    Litestar,
    Response,
    get,
)
from litestar.config.cors import CORSConfig
from litestar.response.redirect import Redirect
from litestar.status_codes import (
    HTTP_500_INTERNAL_SERVER_ERROR,
)

cors_config = CORSConfig(allow_origins=["*"])


#### ENDPOINTS


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


#### APP


def create_app() -> Litestar:
    return Litestar(
        route_handlers=[fc_proxy],
        cors_config=cors_config,
    )
