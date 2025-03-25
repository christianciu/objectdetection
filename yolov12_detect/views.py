import os
import cv2
import numpy as np
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files import File
from ultralytics import YOLO
from .forms import YOLODetectionForm
from .models import YOLODetection

def detect_objects(request):
    if request.method == 'POST':
        form = YOLODetectionForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded files
            detection = form.save()
            
            try:
                # Load YOLO model
                model = YOLO(detection.model_weight.path)
                
                # Get configuration
                conf = detection.confidence
                iou = detection.overlap
                
                # Prepare input image path
                input_image_path = detection.input_image.path
                
                # Perform detection
                results = model(
                    input_image_path, 
                    conf=conf, 
                    iou=iou
                )
                
                # Save output image
                output_img_path = os.path.join(
                    settings.MEDIA_ROOT, 
                    'output_images', 
                    f'output_{detection.id}.jpg'
                )
                
                # Get the first result (assuming single image)
                result = results[0]
                
                # Plot results and save
                result.save(output_img_path)
                
                # Update model with output image
                with open(output_img_path, 'rb') as f:
                    detection.output_image.save(
                        f'output_{detection.id}.jpg', 
                        File(f)
                    )
                
                return render(request, 'detect.html', {
                    'form': form, 
                    'detection': detection
                })
            
            except Exception as e:
                # Handle errors
                form.add_error(None, str(e))
    
    else:
        form = YOLODetectionForm()
    
    return render(request, 'detect.html', {'form': form})
