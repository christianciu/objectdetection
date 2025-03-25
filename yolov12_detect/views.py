import os
import json
from django.shortcuts import render
from django.conf import settings
from django.core.files import File
from ultralytics import YOLO
from .forms import YOLODetectionForm
from .models import YOLODetection

def detect_objects(request):
    if request.method == 'POST':
        form = YOLODetectionForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                # Save the model instance
                detection = form.save()
                # Load YOLO model
                model = YOLO(detection.model_weight.path)
                # Perform detection
                results = model(
                    detection.input_image.path, 
                    conf=detection.confidence, 
                    iou=detection.overlap
                )
                
                # Count detections
                total_detections = 0
                class_counts = {}
                
                for result in results:
                    # Count total number of detections
                    boxes = result.boxes
                    total_detections = len(boxes)
                    
                    # Count detections by class
                    for box in boxes:
                        class_id = int(box.cls[0])
                        class_name = model.names[class_id]
                        class_counts[class_name] = class_counts.get(class_name, 0) + 1
                
                # Generate output image path
                output_img_path = os.path.join(
                    settings.MEDIA_ROOT, 
                    'output_images', 
                    f'output_{detection.id}.jpg'
                )
                
                # Save result
                results[0].save(output_img_path)
                
                # Update model with detection details
                detection.total_detections = total_detections
                detection.class_counts = class_counts
                
                # Save output image
                with open(output_img_path, 'rb') as f:
                    detection.output_image.save(
                        f'output_{detection.id}.jpg', 
                        File(f)
                    )
                
                return render(request, 'detect.html', {
                    'form': form, 
                    'detection': detection,
                })
            
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = YOLODetectionForm()
    
    return render(request, 'detect.html', {'form': form})
