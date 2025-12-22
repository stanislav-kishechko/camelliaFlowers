from django import forms

from apps.products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "image",
            "category",
            "price",
            "stock",
            "rating",
            "is_active"
        ]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                "placeholder": "Назва продукту"
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                "rows": 3,
                "placeholder": "Короткий опис продукту"
            }),
            "category": forms.Select(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500 focus:border-transparent"
            }),
            "price": forms.NumberInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                "step": "0.01",
                "min": "0"
            }),
            "stock": forms.NumberInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                "min": "0"
            }),
            "rating": forms.NumberInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                "step": "0.1",
                "min": "0",
                "max": "5"
            }),
            "image": forms.FileInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                "accept": "image/*"
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "w-4 h-4 text-pink-600 border-gray-300 rounded focus:ring-pink-500"
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False
        self.fields["rating"].required = False
        self.fields["image"].required = False
