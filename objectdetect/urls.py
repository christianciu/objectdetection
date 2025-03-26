from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from yolov12_detect.views import upload_model

urlpatterns = [
    path('', upload_model),
    path('admin/', admin.site.urls),
    path('object-detect/', include('yolov12_detect.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
