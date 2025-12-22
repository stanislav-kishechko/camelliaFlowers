from django.db import models
from django.db.models import Q, QuerySet

from apps.products.enums import ProductStatusEnum


class ProductQuerySet(models.QuerySet):
    def search(self, query: str) -> QuerySet["Product"]:
        if not query:
            return self

        return self.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )

    def by_category(self, category_id: int) -> QuerySet["Product"]:
        if not category_id:
            return self

        return self.filter(category_id=category_id)

    def by_stock_status(self, status: str) -> QuerySet["Product"]:
        match status:
            case ProductStatusEnum.AVAILABLE:
                return self.filter(stock__gt=10)
            case ProductStatusEnum.LOW_STOCK:
                return self.filter(stock__lte=10, stock__gt=0)

            case ProductStatusEnum.OUT_OF_STOCK:
                return self.filter(stock=0)

        return self

    def sort_by(self, sort_option: str) -> QuerySet["Product"]:
        if sort_option == "name":
            return self.order_by("name")

        elif sort_option == "price_asc":
            return self.order_by("price")

        elif sort_option == "price_desc":
            return self.order_by("-price")

        elif sort_option == "popularity":
            return self.order_by("-sold")

        return self.order_by("-created_at")
