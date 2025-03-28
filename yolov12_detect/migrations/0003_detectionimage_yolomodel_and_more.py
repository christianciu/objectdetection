# Generated by Django 5.1.7 on 2025-03-26 03:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yolov12_detect', '0002_yolodetection_class_counts_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetectionImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image_file', models.ImageField(upload_to='input_images/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='YOLOModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('weight_file', models.FileField(upload_to='yolo_weights/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='yolodetection',
            name='model_weight',
        ),
        migrations.AlterField(
            model_name='yolodetection',
            name='input_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='yolov12_detect.detectionimage'),
        ),
        migrations.AddField(
            model_name='yolodetection',
            name='model',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='yolov12_detect.yolomodel'),
        ),
    ]
