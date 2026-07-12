from django.http import HttpResponse
from django.template.loader import render_to_string


def manifest_view(request):
    content = render_to_string("manifest.json", request=request)
    return HttpResponse(content, content_type="application/manifest+json")


def service_worker_view(request):
    content = render_to_string("sw.js", request=request)
    return HttpResponse(content, content_type="application/javascript")
