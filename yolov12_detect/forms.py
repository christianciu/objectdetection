from django import forms

from .models import DetectionImage, YOLODetection, YOLOModel


class ModelUploadForm(forms.ModelForm):
    class Meta:
        model = YOLOModel
        fields = ['name', 'weight_file']


class ImageUploadForm(forms.ModelForm):
    class Meta:
        model = DetectionImage
        fields = ['name', 'image_file']


class DetectionForm(forms.ModelForm):
    class Meta:
        model = YOLODetection
        fields = ['model', 'input_image', 'confidence', 'overlap']
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

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields['model'].queryset = YOLOModel.objects.order_by('-uploaded_at')
        self.fields['input_image'].queryset = DetectionImage.objects.order_by('-uploaded_at')


class MultiWeightDetectionForm(forms.Form):
    input_image = forms.ModelChoiceField(
        queryset=DetectionImage.objects.order_by('-uploaded_at'),
        label="Select Image"
    )

class WeightConfigForm(forms.Form):
    weight = forms.ModelChoiceField(queryset=YOLOModel.objects.order_by('-uploaded_at'))
    confidence = forms.FloatField(
        initial=0.5,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'max': '1',
            'class': 'form-control'
        })
    )
    overlap = forms.FloatField(
        initial=0.45,
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'min': '0',
            'max': '1',
            'class': 'form-control'
        })
    )

WeightConfigFormSet = forms.formset_factory(
    WeightConfigForm,
    extra=1,
    can_delete=True
)