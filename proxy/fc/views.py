from urllib.parse import parse_qs, unquote, urlencode, urlparse, urlunparse

from django.http import HttpResponseRedirect, JsonResponse


def fc_callback(request) -> JsonResponse | HttpResponseRedirect:
    query = request.GET
    if "state" not in query or not query["state"].startswith("http"):
        details = {
            "error": "No callback URL provided in the `state` parameter (have you set it when querying FC?)"
        }
        return JsonResponse(details, status=500)
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
    all_query_params = {**query.dict(), **redirect_url_query}
    return HttpResponseRedirect(f"{redirect_url}?{urlencode(all_query_params, doseq=True)}")
