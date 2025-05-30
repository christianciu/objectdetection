# Generated by Django 5.1.7 on 2025-03-25 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='YOLODetection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model_weight', models.FileField(upload_to='yolo_weights/')),
                ('input_image', models.ImageField(upload_to='input_images/')),
                ('output_image', models.ImageField(blank=True, null=True, upload_to='output_images/')),
                ('confidence', models.FloatField(default=0.5)),
                ('overlap', models.FloatField(default=0.45)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
