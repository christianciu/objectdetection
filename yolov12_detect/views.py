import math
import os

from django.conf import settings
from django.contrib import messages
from django.core.files import File
from django.shortcuts import get_object_or_404, redirect, render
from ultralytics import YOLO

from .forms import (DetectionForm, ImageUploadForm, ModelUploadForm,
                    MultiWeightDetectionForm, WeightConfigFormSet)
from .models import (DetectionImage, MultiWeightDetection,
                     MultiWeightDetectionResult, YOLODetection, YOLOModel)


def get_stride_adjusted_size(input_size, stride=32):
    """Adjust size to be multiple of stride"""
    return int(math.ceil(input_size / stride)) * stride


def home(request):
    return render(request, 'home.html')


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
                # HEIGHT x WIDTH
                size = (get_stride_adjusted_size(form.cleaned_data['resize_height']),
                        get_stride_adjusted_size(form.cleaned_data['resize_width']))
                results = model(
                    image_path,
                    conf=detection.confidence,
                    iou=detection.overlap,
                    imgsz=size
                )
                print(size)

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
            # HEIGHT x WIDTH
            image_resize = (get_stride_adjusted_size(image_form.cleaned_data['resize_height']),
                            get_stride_adjusted_size(image_form.cleaned_data['resize_width']))

            # Create parent detection record
            parent_detection = MultiWeightDetection.objects.create(
                input_image=input_image, resize_width=image_resize[1], resize_height=image_resize[0]
            )

            order = 0
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
                            iou=overlap,
                            imgsz=image_resize
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

                        # Save output image
                        output_img_path = os.path.join(
                            settings.MEDIA_ROOT,
                            'output_images',
                            f'multi_output_{parent_detection.id}_{weight.id}.jpg'
                        )
                        results[0].save(output_img_path)

                        # Create YOLODetection record
                        detection = YOLODetection.objects.create(
                            model=weight,
                            input_image=input_image,
                            confidence=confidence,
                            overlap=overlap,
                            total_detections=total_detections,
                            class_counts=class_counts
                        )

                        with open(output_img_path, 'rb') as f:
                            detection.output_image.save(
                                f'multi_output_{parent_detection.id}_{weight.id}.jpg',
                                File(f)
                            )

                        # Create result record
                        MultiWeightDetectionResult.objects.create(
                            parent_detection=parent_detection,
                            detection=detection,
                            weight=weight,
                            order=order
                        )

                        order += 1

                    except Exception as e:
                        messages.error(request, f"Error processing {weight.name}: {str(e)}")

            return redirect('yolov12_detect:multi_weight_result', detection_id=parent_detection.id)

    else:
        image_form = MultiWeightDetectionForm()
        formset = WeightConfigFormSet()

    return render(request, 'multi_weight_detect.html', {
        'image_form': image_form,
        'formset': formset
    })


def multi_weight_result(request, detection_id):
    parent_detection = get_object_or_404(MultiWeightDetection, id=detection_id)
    results = parent_detection.results.select_related('detection', 'weight')

    return render(request, 'multi_weight_result.html', {
        'parent_detection': parent_detection,
        'results': results,
        'input_image': parent_detection.input_image
    })


def detection_history(request):
    single_detections = YOLODetection.objects.select_related('input_image', 'model').filter(multiweightdetectionresult__isnull=True).order_by('-id')
    multi_detections = MultiWeightDetection.objects.select_related('input_image').prefetch_related('results__weight').order_by('-id')

    return render(request, 'detection_history.html', {
        'single_detections': single_detections,
        'multi_detections': multi_detections
    })
