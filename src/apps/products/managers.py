from django.db import models
from django.db.models import QuerySet

from apps.products.enums import ProductStatusEnum
from apps.products.querysets import ProductQuerySet


class ProductManager(models.Manager):
    def get_queryset(self) -> ProductQuerySet:
        return ProductQuerySet(self.model, using=self._db)

    def search(self, query: str) -> QuerySet["Product"]:
        return self.get_queryset().search(query)

    def by_category(self, category_id: int) -> QuerySet["Product"]:
        return self.get_queryset().by_category(category_id)

    def by_stock_status(self, status: ProductStatusEnum) -> QuerySet["Product"]:
        return self.get_queryset().by_stock_status(status)

    def sort_by(self, sort_option: str) -> QuerySet["Product"]:
        return self.get_queryset().sort_by(sort_option)
