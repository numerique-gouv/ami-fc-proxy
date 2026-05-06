from urllib.parse import urlencode

from django.http import HttpResponseRedirect, JsonResponse


def authorize_request(request) -> JsonResponse | HttpResponseRedirect:
    query = request.GET
    if "from_url" not in query or "fc_url" not in query:
        details = {"error": "Can not redirect to FC authorize endpoint"}
        return JsonResponse(details, status=500)
    request.session["ami_fi_from_url"] = query["from_url"]
    return HttpResponseRedirect(query["fc_url"])


def get_from_url(request) -> JsonResponse:
    return JsonResponse({"from_url": request.session.get("ami_fi_from_url") or ""})


def authorize(request) -> JsonResponse | HttpResponseRedirect:
    query = request.GET
    from_url = request.session.get("ami_fi_from_url")
    if not from_url:
        details = {"error": "Can not redirect to FI authorize endpoint"}
        return JsonResponse(details, status=500)
    redirect_url = f"{from_url}api/v1/fi/authorize/"
    return HttpResponseRedirect(f"{redirect_url}?{urlencode(query, doseq=True)}")
