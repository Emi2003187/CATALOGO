from django import forms
from django.forms import ModelForm
from .models import Platillo

class SushiForm(ModelForm):
    ingredientes = forms.CharField(
        label="Ingredientes del platillo",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )

    class Meta:
        model = Platillo
        fields = ['nombre', 'descripcion', 'precio', 'imagen', 'ingredientes', 'en_promocion']
        labels = {
            'nombre': 'Nombre del platillo',
            'descripcion': 'Descripción del platillo',
            'precio': 'Precio del platillo',
            'imagen': 'Imagen del platillo',
            'ingredientes': 'Ingredientes del platillo',
            'en_promocion': '¿Este platillo entra en la promoción 2 por 289?'
        }
        help_texts = {
            'nombre': 'Ingrese el nombre del platillo',
            'descripcion': 'Ingrese una breve descripción del platillo',
            'precio': 'Ingrese el precio del platillo',
            'imagen': 'Seleccione una imagen para el platillo',
            'ingredientes': 'Lista de ingredientes utilizados en este platillo',
            'en_promocion': 'Marque esta opción si este platillo participa en la promoción 2 por 289'
        }
