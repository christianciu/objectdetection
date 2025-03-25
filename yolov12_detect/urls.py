from django.urls import path
from . import views

app_name = 'yolov12_detect'

urlpatterns = [
    path('', views.detect_objects, name='detect_objects'),
]
