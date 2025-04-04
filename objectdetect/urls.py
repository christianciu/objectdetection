from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from yolov12_detect.views import detect_objects

urlpatterns = [
    path('', detect_objects),
    path('admin/', admin.site.urls),
    path('object-detect/', include('yolov12_detect.urls')),
]

if settings.DEBUG:
    try:
        from debug_toolbar.toolbar import debug_toolbar_urls
        urlpatterns += debug_toolbar_urls()
    except ImportError:
        pass

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
