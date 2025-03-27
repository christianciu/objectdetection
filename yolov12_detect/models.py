from django.db import models
from django.utils import timezone

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class YOLOModel(models.Model):
    name = models.CharField(max_length=100)
    weight_file = models.FileField(upload_to='yolo_weights/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {timezone.localtime(self.uploaded_at).strftime(TIME_FORMAT)}"


class DetectionImage(models.Model):
    name = models.CharField(max_length=100)
    image_file = models.ImageField(upload_to='input_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {timezone.localtime(self.uploaded_at).strftime(TIME_FORMAT)}"


class YOLODetection(models.Model):
    model = models.ForeignKey(YOLOModel, on_delete=models.CASCADE, blank=True, null=True)
    input_image = models.ForeignKey(DetectionImage, on_delete=models.CASCADE)
    output_image = models.ImageField(upload_to='output_images/', null=True, blank=True)
    confidence = models.FloatField(default=0.5)
    overlap = models.FloatField(default=0.45)
    total_detections = models.IntegerField(default=0)
    class_counts = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Detection {self.id}"
