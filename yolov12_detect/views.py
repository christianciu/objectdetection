import json
import os

from django.conf import settings
from django.contrib import messages
from django.core.files import File
from django.shortcuts import redirect, render
from ultralytics import YOLO

from .forms import (DetectionForm, ImageUploadForm, ModelUploadForm,
                    MultiWeightDetectionForm, WeightConfigFormSet)
from .models import DetectionImage, YOLODetection, YOLOModel


def upload_model(request):
    if request.method == 'POST':
        form = ModelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('yolov12_detect:select_model')
    else:
        form = ModelUploadForm()

    models = YOLOModel.objects.all()
    return render(request, 'upload_model.html', {
        'form': form,
        'models': models
    })


def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('yolov12_detect:select_image')
    else:
        form = ImageUploadForm()

    images = DetectionImage.objects.all()
    return render(request, 'upload_image.html', {
        'form': form,
        'images': images
    })


def detect_objects(request):
    if request.method == 'POST':
        form = DetectionForm(request.POST)
        if form.is_valid():
            detection = form.save(commit=False)

            try:
                # Get model and image paths
                model_path = form.cleaned_data['model'].weight_file.path
                image_path = form.cleaned_data['input_image'].image_file.path

                # Load YOLO model and perform detection
                model = YOLO(model_path)
                results = model(
                    image_path, 
                    conf=detection.confidence, 
                    iou=detection.overlap
                )

                # Count detections
                total_detections = 0
                class_counts = {}

                for result in results:
                    boxes = result.boxes
                    total_detections = len(boxes)

                    for box in boxes:
                        class_id = int(box.cls[0])
                        class_name = model.names[class_id]
                        class_counts[class_name] = class_counts.get(class_name, 0) + 1

                # Save results
                output_img_path = os.path.join(
                    settings.MEDIA_ROOT, 
                    'output_images', 
                    f'output_{detection.id}.jpg'
                )

                results[0].save(output_img_path)

                detection.total_detections = total_detections
                detection.class_counts = class_counts

                with open(output_img_path, 'rb') as f:
                    detection.output_image.save(
                        f'output_{detection.id}.jpg', 
                        File(f)
                    )

                detection.save()
                return redirect('yolov12_detect:detection_result', detection_id=detection.id)

            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = DetectionForm()

    return render(request, 'detect.html', {'form': form})


def detection_result(request, detection_id):
    detection = YOLODetection.objects.get(id=detection_id)
    return render(request, 'result.html', {'detection': detection})


def multi_weight_detection(request):
    if request.method == 'POST':
        image_form = MultiWeightDetectionForm(request.POST)
        formset = WeightConfigFormSet(request.POST)

        if image_form.is_valid() and formset.is_valid():
            input_image = image_form.cleaned_data['input_image']
            detections = []

            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    weight = form.cleaned_data['weight']
                    confidence = form.cleaned_data['confidence']
                    overlap = form.cleaned_data['overlap']

                    try:
                        # Perform detection
                        model = YOLO(weight.weight_file.path)
                        results = model(
                            input_image.image_file.path,
                            conf=confidence,
                            iou=overlap
                        )

                        # Process results
                        total_detections = 0
                        class_counts = {}

                        for result in results:
                            boxes = result.boxes
                            total_detections = len(boxes)

                            for box in boxes:
                                class_id = int(box.cls[0])
                                class_name = model.names[class_id]
                                class_counts[class_name] = class_counts.get(class_name, 0) + 1

                        # Save results
                        output_img_path = os.path.join(
                            settings.MEDIA_ROOT,
                            'output_images',
                            f'output_{weight.id}_{input_image.id}.jpg'
                        )
                        results[0].save(output_img_path)

                        detection = YOLODetection(
                            model=weight,
                            input_image=input_image,
                            confidence=confidence,
                            overlap=overlap,
                            total_detections=total_detections,
                            class_counts=class_counts
                        )

                        with open(output_img_path, 'rb') as f:
                            detection.output_image.save(
                                f'output_{weight.id}_{input_image.id}.jpg',
                                File(f)
                            )

                        detection.save()
                        detections.append(detection)

                    except Exception as e:
                        messages.error(request, f"Error processing {weight.name}: {str(e)}")

            if detections:
                return render(request, 'multi_weight_result.html', {
                    'detections': detections,
                    'input_image': input_image
                })
    else:
        image_form = MultiWeightDetectionForm()
        formset = WeightConfigFormSet()
    
    return render(request, 'multi_weight_detect.html', {
        'image_form': image_form,
        'formset': formset
    })
