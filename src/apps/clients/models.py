from __future__ import annotations

from django.db import models
from django.urls import reverse

from apps.abstract_models import AbstractDatetimeModel

from .managers import ClientManager


class Client(AbstractDatetimeModel):
    """Client model for storing customer information."""

    first_name = models.CharField("Ім'я", max_length=100)
    last_name = models.CharField("Прізвище", max_length=100)
    phone = models.CharField("Телефон", max_length=20, unique=True)
    email = models.EmailField("Email", blank=True, null=True)
    address = models.CharField("Адреса", max_length=255, blank=True, null=True)
    city = models.CharField("Місто", max_length=100, blank=True, null=True)
    notes = models.TextField("Примітки", blank=True, null=True)

    is_vip = models.BooleanField("VIP клієнт", default=False)
    is_active = models.BooleanField("Активний", default=True)

    orders_count = models.IntegerField("Кількість замовлень", default=0)
    total_spent = models.DecimalField(
        "Загальна сума покупок", max_digits=10, decimal_places=2, default=0
    )

    objects = ClientManager()

    class Meta:
        verbose_name = "Клієнт"
        verbose_name_plural = "Клієнти"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone"]),
            models.Index(fields=["email"]),
            models.Index(fields=["is_vip"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        """Return the client's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def initials(self) -> str:
        """Return the client's initials."""
        return f"{self.first_name[0]}{self.last_name[0]}"

    def get_absolute_url(self) -> str:
        """Return the URL to access this client instance."""
        return reverse("clients:client_detail", args=[str(self.id)])

    def make_vip(self) -> None:
        """Mark the client as VIP and persist the change."""
        self.is_vip = True
        self.save(update_fields=["is_vip"])

    def remove_vip(self) -> None:
        """Remove VIP status and persist the change."""
        self.is_vip = False
        self.save(update_fields=["is_vip"])

    def deactivate(self) -> None:
        """Deactivate the client and persist the change."""
        self.is_active = False
        self.save(update_fields=["is_active"])

    def activate(self) -> None:
        """Activate the client and persist the change."""
        self.is_active = True
        self.save(update_fields=["is_active"])
