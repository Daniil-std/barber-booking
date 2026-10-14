from django.conf import settings
from django.http import FileResponse, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_safe


@require_safe
@never_cache
def frontend(request):
    index = settings.FRONTEND_DIST / "index.html"
    if not index.is_file():
        return JsonResponse({"status": "frontend_unavailable"}, status=503)
    return FileResponse(index.open("rb"), content_type="text/html; charset=utf-8")
