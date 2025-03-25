from django import forms
from .models import YOLODetection

class YOLODetectionForm(forms.ModelForm):
    CLASSES_CHOICES = [
        ('all', 'Detect All Classes'),
        # Add your specific classes here
    ]

    selected_class = forms.ChoiceField(
        choices=CLASSES_CHOICES, 
        required=False, 
        initial='all'
    )

    class Meta:
        model = YOLODetection
        fields = ['model_weight', 'input_image', 'confidence', 'overlap']
        widgets = {
            'confidence': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'max': '1',
                'default': '0.5'
            }),
            'overlap': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'max': '1',
                'default': '0.45'
            })
        }
