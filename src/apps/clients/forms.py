from __future__ import annotations

from django import forms

from .enums import ClientStatusEnum
from .models import Client


class ClientForm(forms.ModelForm):
    """Form for creating and updating `Client` instances."""

    client_type: forms.ChoiceField = forms.ChoiceField(
        choices=ClientStatusEnum.choices,
        required=False,
        initial="regular",
        widget=forms.Select(
            attrs={
                "class": "w-full px-4 py-2 border border-gray-300 "
                "rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-transparent"
            }
        ),
    )

    class Meta:
        model = Client
        fields = ["first_name", "last_name", "phone", "email", "address", "city", "notes"]
        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                    "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                    "placeholder": "Ім'я",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                    "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                    "placeholder": "Прізвище",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                    "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                    "placeholder": "+380 XX XXX XXXX",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                    "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                    "placeholder": "email@example.com",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                    "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                    "placeholder": "Адреса доставки",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                    "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                    "placeholder": "Місто",
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                    "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                    "rows": 3,
                    "placeholder": "Додаткова інформація...",
                }
            ),
        }
