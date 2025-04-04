from django.urls import path

from . import views

app_name = 'yolov12_detect'

urlpatterns = [
    path('', views.upload_model, name='home'),  # Start with model upload

    path('upload-model/', views.upload_model, name='upload_model'),
    path('select-model/', views.upload_model, name='select_model'),
    path('upload-image/', views.upload_image, name='upload_image'),
    path('select-image/', views.upload_image, name='select_image'),

    path('single/', views.detect_objects, name='detect_objects'),
    path('single/result/<int:detection_id>/', views.detection_result, name='detection_result'),

    path('multi/', views.multi_weight_detection, name='multi_weight_detection'),
    path('multi/result/<int:detection_id>/', views.multi_weight_result, name='multi_weight_result'),
    
    path('history/', views.detection_history, name='detection_history'),

    # path('detect/', views.detect_objects, name='detect_objects'),
    # path('result/<int:detection_id>/', views.detection_result, name='detection_result'),
# 
    # path('multi-weight/', views.multi_weight_detection, name='multi_weight_detection'),
]
