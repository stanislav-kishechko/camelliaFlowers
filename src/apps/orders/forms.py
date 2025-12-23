from __future__ import annotations

from datetime import date
from typing import Any

from django import forms
from django.core.exceptions import ValidationError

from apps.clients.models import Client
from apps.orders.enums import OrderStatusEnum
from apps.orders.models import Order, OrderItem
from apps.products.models import Product


class OrderForm(forms.ModelForm):
    """
    Form for managing order data.

    The `OrderForm` class is used to create and validate forms related
    to an `Order` instance. It provides a user-friendly interface with
    widget settings for each field, supports validation logic for
    delivery data, and ensures that the input data is properly
    processed according to the business rules.

    :ivar Meta.model: The model on which the form is based (`Order`).
    :type Meta.model: Type[Order]
    :ivar Meta.fields: List of fields included in the form.
    :type Meta.fields: list[str]
    :ivar Meta.widgets: Dictionary defining the widgets for specific fields.
    :type Meta.widgets: dict[str, forms.Widget]
    """
    class Meta:
        model = Order
        fields = [
            "client", "needs_delivery", "delivery_address", "delivery_date",
            "delivery_time", "status", "notes"
        ]
        widgets = {
            "client": forms.Select(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500 focus:border-transparent"
            }),
            "needs_delivery": forms.CheckboxInput(attrs={
                "class": "w-4 h-4 text-pink-600 focus:ring-pink-500 rounded",
                "onchange": "toggleDeliveryFields(this.checked)"
            }),
            "delivery_address": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                         "focus:ring-pink-500 focus:border-transparent",
                "placeholder": "вул. Хрещатик, 22"
            }),
            "delivery_date": forms.DateInput(attrs={
                "type": "date",
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                         "focus:ring-pink-500 focus:border-transparent"
            }),
            "delivery_time": forms.TimeInput(attrs={
                "type": "time",
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                         "focus:ring-pink-500 focus:border-transparent"
            }),
            "status": forms.Select(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                         "focus:ring-pink-500 focus:border-transparent"
            }),
            "notes": forms.Textarea(attrs={
                "rows": 3,
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                         "focus:ring-pink-500 focus:border-transparent",
                "placeholder": "Додаткова інформація про замовлення..."
            }),
        }

    def clean(self) -> dict[str, Any]:
        """Validate delivery fields when delivery is required.

        Returns:
            dict: The cleaned data.
        """
        cleaned_data = super().clean()
        needs_delivery = cleaned_data.get("needs_delivery")
        delivery_address = cleaned_data.get("delivery_address")
        delivery_date = cleaned_data.get("delivery_date")

        if needs_delivery:
            if not delivery_address:
                raise ValidationError({
                    "delivery_address": "Адреса доставки обов'язкова, якщо потрібна доставка"
                })
            if not delivery_date:
                raise ValidationError({
                    "delivery_date": "Дата доставки обов'язкова, якщо потрібна доставка"
                })
            if delivery_date and delivery_date < date.today():
                raise ValidationError({
                    "delivery_date": "Дата доставки не може бути в минулому"
                })

        return cleaned_data


class OrderItemForm(forms.ModelForm):
    """
    Represents a form for ordering items, based on the `OrderItem` model.

    This form allows users to select a product and specify its quantity while ensuring
    validation constraints are adhered to. It customizes input widgets for better
    frontend presentation and implements dynamic label customization for the product
    field if the `Product` model contains an `emoji` field.

    :ivar product: The product to be ordered, filtered to display only those with stock
                    greater than zero.
    :ivar quantity: The quantity of the product to be ordered, with a minimum of 1.
    """
    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]
        widgets = {
            "product": forms.Select(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500 focus:border-transparent"
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                         "focus:ring-2 focus:ring-pink-500 focus:border-transparent",
                "min": 1,
                "value": 1
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(Product.objects.first(), "emoji"):
            self.fields["product"].queryset = Product.objects.filter(
                stock__gt=0
            ).select_related("category")
            self.fields["product"].label_from_instance = lambda \
                obj: f"{obj.emoji} {obj.name} - ₴{obj.price}"

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        product = self.cleaned_data.get("product")

        if quantity < 1:
            raise ValidationError("Кількість має бути більше 0")

        if product and hasattr(product, "stock"):
            if quantity > product.stock:
                raise ValidationError(
                    f"Недостатньо товару на складі. Доступно: {product.stock}"
                )

        return quantity


class OrderItemInlineFormSet(forms.BaseInlineFormSet):
    """
    Manages the validation and processing of inline formsets for order items.

    This class extends the base inline formset provided by Django, specifically for
    handling the context of order items. It ensures custom validation of the provided
    forms, such as ensuring at least one item is added when submitting the order.

    """
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        if not any(form.cleaned_data and not form.cleaned_data.get("DELETE", False)
                   for form in self.forms):
            raise ValidationError("Додайте хоча б один товар до замовлення")


class ClientQuickAddForm(forms.ModelForm):
    """
    A form for quickly adding a new client with validation capabilities.

    This form is based on the `Client` model and used to collect basic client
    information, including first name, last name, and phone number. It includes
    custom widgets for enhanced user input and performs validation to ensure
    phone number uniqueness.

    :ivar Meta.model: The model associated with the form.
    :type Meta.model: type[Client]
    :ivar Meta.fields: The list of fields to be included in the form.
    :type Meta.fields: list[str]
    :ivar Meta.widgets: Customized widget configurations for form fields.
    :type Meta.widgets: dict
    """
    class Meta:
        model = Client
        fields = ["first_name", "last_name", "phone"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                         "focus:ring-pink-500 focus:border-transparent",
                "placeholder": "Іван"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                         "focus:ring-pink-500 focus:border-transparent",
                "placeholder": "Іванов"
            }),
            "phone": forms.TextInput(attrs={
                "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                         "focus:ring-pink-500 focus:border-transparent",
                "placeholder": "+380 XX XXX XXXX"
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")

        if Client.objects.filter(phone=phone).exists():
            raise ValidationError("Клієнт з таким телефоном вже існує")

        return phone


class OrderCreateForm(forms.Form):
    existing_client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        label="Існуючий клієнт",
        widget=forms.Select(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                     "focus:ring-pink-500"
        })
    )

    client_first_name = forms.CharField(
        max_length=100,
        required=False,
        label="Ім'я",
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                     "focus:ring-pink-500",
            "placeholder": "Іван"
        })
    )

    client_last_name = forms.CharField(
        max_length=100,
        required=False,
        label="Прізвище",
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                     "focus:ring-pink-500",
            "placeholder": "Іванов"
        })
    )

    client_phone = forms.CharField(
        max_length=20,
        required=False,
        label="Телефон",
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                     "focus:ring-pink-500",
            "placeholder": "+380 XX XXX XXXX"
        })
    )

    needs_delivery = forms.BooleanField(
        required=False,
        initial=False,
        label="Потрібна доставка",
        widget=forms.CheckboxInput(attrs={
            "class": "w-4 h-4 text-pink-600 focus:ring-pink-500 rounded",
            "onchange": "toggleDeliveryFields(this.checked)"
        })
    )

    delivery_address = forms.CharField(
        required=False,
        max_length=255,
        label="Адреса доставки",
        widget=forms.TextInput(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500",
            "placeholder": "вул. Хрещатик, 22"
        })
    )

    delivery_date = forms.DateField(
        required=False,
        label="Дата доставки",
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500"
        })
    )

    delivery_time = forms.TimeField(
        required=False,
        label="Час доставки",
        widget=forms.TimeInput(attrs={
            "type": "time",
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500"
        })
    )

    notes = forms.CharField(
        required=False,
        label="Примітки",
        widget=forms.Textarea(attrs={
            "rows": 3,
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg "
                     "focus:ring-2 focus:ring-pink-500",
            "placeholder": "Додаткова інформація..."
        })
    )

    def clean(self):
        cleaned_data = super().clean()

        existing_client = cleaned_data.get("existing_client")
        client_phone = cleaned_data.get("client_phone")
        client_first_name = cleaned_data.get("client_first_name")

        if not existing_client:
            if not client_phone or not client_first_name:
                raise ValidationError(
                    "Оберіть існуючого клієнта або вкажіть телефон та ім'я для нового клієнта"
                )

        needs_delivery = cleaned_data.get("needs_delivery")
        if needs_delivery:
            delivery_address = cleaned_data.get("delivery_address")
            delivery_date = cleaned_data.get("delivery_date")

            if not delivery_address:
                raise ValidationError({
                    "delivery_address": "Адреса доставки обов'язкова, якщо потрібна доставка"
                })
            if not delivery_date:
                raise ValidationError({
                    "delivery_date": "Дата доставки обов'язкова, якщо потрібна доставка"
                })
            if delivery_date and delivery_date < date.today():
                raise ValidationError({
                    "delivery_date": "Дата доставки не може бути в минулому"
                })

        return cleaned_data

    def save(self):
        client = self.cleaned_data.get("existing_client")

        if not client:
            client, created = Client.objects.get_or_create(
                phone=self.cleaned_data["client_phone"],
                defaults={
                    "first_name": self.cleaned_data["client_first_name"],
                    "last_name": self.cleaned_data.get("client_last_name", "")
                }
            )

        order = Order(
            client=client,
            needs_delivery=self.cleaned_data.get("needs_delivery", False),
            notes=self.cleaned_data.get("notes", "")
        )

        if order.needs_delivery:
            order.delivery_address = self.cleaned_data.get("delivery_address")
            order.delivery_date = self.cleaned_data.get("delivery_date")
            order.delivery_time = self.cleaned_data.get("delivery_time")

        order.save()
        return order


class OrderStatusChangeForm(forms.Form):
    new_status = forms.ChoiceField(
        choices=OrderStatusEnum.choices,
        label="Новий статус",
        widget=forms.Select(attrs={
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                     "focus:ring-pink-500"
        })
    )

    notes = forms.CharField(
        required=False,
        label="Примітка",
        widget=forms.Textarea(attrs={
            "rows": 2,
            "class": "w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 "
                     "focus:ring-pink-500",
            "placeholder": "Примітка до зміни статусу..."
        })
    )

    def __init__(self, *args, order=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.order = order

        if order:
            allowed_statuses = []
            for status_value, status_label in OrderStatusEnum.choices:
                if order.can_transition_to(status_value):
                    allowed_statuses.append((status_value, status_label))

            if allowed_statuses:
                self.fields["new_status"].choices = allowed_statuses
            else:
                self.fields["new_status"].choices = [(order.status, order.get_status_display())]
                self.fields["new_status"].widget.attrs["disabled"] = True

    def clean_new_status(self):
        new_status = self.cleaned_data.get("new_status")

        if self.order and not self.order.can_transition_to(new_status):
            raise ValidationError(
                f"Неможливо перейти зі статусу \"{self.order.get_status_display()}\" "
                f"до \"{OrderStatusEnum(new_status).label}\""
            )

        return new_status

    def save(self, user=None):
        """Застосування зміни статусу"""
        if self.order:
            self.order.transition_to(
                self.cleaned_data["new_status"],
                user=user,
                notes=self.cleaned_data.get("notes", "")
            )
            return self.order


class OrderFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[("", "Всі статуси")] + list(OrderStatusEnum.choices),
        required=False,
        label="Статус",
        widget=forms.Select(attrs={
            "class": "px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500"
        })
    )

    delivery_type = forms.ChoiceField(
        choices=[
            ("", "Всі типи"),
            ("delivery", "Тільки доставка"),
            ("pickup", "Тільки самовивіз")
        ],
        required=False,
        label="Тип замовлення",
        widget=forms.Select(attrs={
            "class": "px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500"
        })
    )

    client = forms.ModelChoiceField(
        queryset=Client.objects.all(),
        required=False,
        label="Клієнт",
        widget=forms.Select(attrs={
            "class": "px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500"
        })
    )

    date_from = forms.DateField(
        required=False,
        label="Дата від",
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500"
        })
    )

    date_to = forms.DateField(
        required=False,
        label="Дата до",
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500"
        })
    )

    search = forms.CharField(
        required=False,
        label="Пошук",
        widget=forms.TextInput(attrs={
            "class": "px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500",
            "placeholder": "Пошук за адресою, примітками..."
        })
    )
