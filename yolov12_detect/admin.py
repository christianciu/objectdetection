from django.contrib import admin

# Register your models here.

from .models import YOLOModel, YOLODetection, DetectionImage


@admin.register(YOLOModel)
class YoloModelAdmin(admin.ModelAdmin):
    pass

@admin.register(YOLODetection)
class YOLODetectionAdmin(admin.ModelAdmin):
    pass

@admin.register(DetectionImage)
class DetectionImageAdmin(admin.ModelAdmin):
    pass
