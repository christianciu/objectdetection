from django.db import models

class YOLODetection(models.Model):
    model_weight = models.FileField(upload_to='yolo_weights/')
    input_image = models.ImageField(upload_to='input_images/')
    output_image = models.ImageField(upload_to='output_images/', null=True, blank=True)
    confidence = models.FloatField(default=0.5)
    overlap = models.FloatField(default=0.45)
    total_detections = models.IntegerField(default=0)
    class_counts = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Detection {self.id}"
