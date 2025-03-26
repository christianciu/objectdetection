from django.urls import path
from . import views

app_name = 'yolov12_detect'

urlpatterns = [
    path('', views.upload_model, name='home'),  # Start with model upload
    path('upload-model/', views.upload_model, name='upload_model'),
    path('select-model/', views.upload_model, name='select_model'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('select-image/', views.upload_image, name='select_image'),
    path('detect/', views.detect_objects, name='detect_objects'),
    path('result/<int:detection_id>/', views.detection_result, name='detection_result'),
]
