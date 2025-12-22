from django.db import models


class ProductStatusEnum(models.TextChoices):
    AVAILABLE = "in_stock", "В наявності"
    LOW_STOCK = "low_stock", "Закінчується"
    OUT_OF_STOCK = "out_of_stock", "Немає в наявності"
