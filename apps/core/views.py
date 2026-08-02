from django.http import HttpResponse
from django.template.loader import render_to_string


def manifest_view(request):
    content = render_to_string("manifest.json", request=request)
    return HttpResponse(content, content_type="application/manifest+json")


def service_worker_view(request):
    content = render_to_string("sw.js", request=request)
    response = HttpResponse(content, content_type="application/javascript")
    # Service workers should never be cached by the browser/any proxy — without
    # this, an update can silently sit unused for up to 24h (browsers' own SW
    # freshness cap), which is exactly what caused a fixed bug to keep looking
    # unfixed on-device earlier.
    response["Cache-Control"] = "no-cache"
    return response
