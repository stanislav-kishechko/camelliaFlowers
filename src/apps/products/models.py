from cloudinary.models import CloudinaryField
from django.db import models

from apps.abstract_models import AbstractDatetimeModel
from apps.products.enums import ProductStatusEnum
from apps.products.managers import ProductManager
from apps.products.state_mashine.state_factory import get_product_state


class ProductCategory(AbstractDatetimeModel):
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name = "Категорія товару"
        verbose_name_plural = "Категорії товару"
        db_table = "product_categories"

    def __str__(self):
        return self.name


class Product(AbstractDatetimeModel):
    name = models.CharField(
        max_length=255,
        verbose_name="Назва",
        unique=True
    )

    description = models.CharField(
        max_length=255,
        verbose_name="Короткий опис",
        blank=True
    )

    image = CloudinaryField(
        "products"
    )

    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name="products"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Ціна",
    )

    stock = models.PositiveIntegerField(
        verbose_name="На складі (шт)",
        default=0,
    )

    sold = models.PositiveIntegerField(
        verbose_name="Продано",
        default=0,
    )

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        verbose_name="Рейтинг",
        default=0.0,
    )

    status = models.CharField(
        max_length=20,
        choices=ProductStatusEnum.choices,
        default=ProductStatusEnum.AVAILABLE,
        verbose_name="Статус",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активний товар",
    )

    objects = ProductManager()

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        db_table = "products"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def get_state(self):
        return get_product_state(self)

    @property
    def can_be_purchased(self) -> bool:
        return self.get_state().can_be_purchased()
