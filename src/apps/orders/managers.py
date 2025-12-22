from django.db import models
from django.db.models import Avg, Sum

from apps.orders.querysets import OrderQuerySet


class OrderManager(models.Manager):
    """
    Manages queries on Order objects.

    This class extends Django's models.Manager and is tailored for handling and
    managing the queries related to orders. It provides methods for filtering
    orders based on various criteria including statuses, dates, clients, products,
    pricing ranges, and other specific conditions. Additionally, it allows for
    fetching statistical data and kanban board-related data for orders.

    :ivar model: The model class the manager is managing.
    :type model: Type[Model]
    """
    def get_queryset(self) -> OrderQuerySet:
        return OrderQuerySet(self.model, using=self._db)

    def search(self, query: str) -> OrderQuerySet:
        return self.get_queryset().search(query)

    def by_status(self, status: str) -> OrderQuerySet:
        return self.get_queryset().by_status(status)

    def by_date_range(self, date_range: str) -> OrderQuerySet:
        return self.get_queryset().by_date_range(date_range)

    def by_delivery_date(self, delivery_date: str) -> OrderQuerySet:
        return self.get_queryset().by_delivery_date(delivery_date)

    def by_client(self, client_id: int) -> OrderQuerySet:
        return self.get_queryset().by_client(client_id)

    def by_product(self, product_id: int) -> OrderQuerySet:
        return self.get_queryset().by_product(product_id)

    def sort_by(self, sort_option: str) -> OrderQuerySet:
        return self.get_queryset().sort_by(sort_option)

    def new(self) -> OrderQuerySet:
        return self.get_queryset().new()

    def processing(self) -> OrderQuerySet:
        """В обробці"""
        return self.get_queryset().processing()

    def delivery(self) -> OrderQuerySet:
        return self.get_queryset().delivery()

    def completed(self) -> OrderQuerySet:
        return self.get_queryset().completed()

    def cancelled(self) -> OrderQuerySet:
        return self.get_queryset().cancelled()

    def active(self) -> OrderQuerySet:
        return self.get_queryset().active()

    def today(self) -> OrderQuerySet:
        return self.get_queryset().today()

    def this_week(self) -> OrderQuerySet:
        return self.get_queryset().this_week()

    def this_month(self) -> OrderQuerySet:
        return self.get_queryset().this_month()

    def recent(self, days: int = 7) -> OrderQuerySet:
        return self.get_queryset().recent(days)

    def delivery_today(self) -> OrderQuerySet:
        return self.get_queryset().delivery_today()

    def delivery_tomorrow(self) -> OrderQuerySet:
        return self.get_queryset().delivery_tomorrow()

    def delivery_this_week(self) -> OrderQuerySet:
        return self.get_queryset().delivery_this_week()

    def overdue(self) -> OrderQuerySet:
        return self.get_queryset().overdue()

    def by_price_range(self, min_price=None, max_price=None) -> OrderQuerySet:
        return self.get_queryset().by_price_range(min_price, max_price)

    def high_value(self, threshold: int = 5000) -> OrderQuerySet:
        return self.get_queryset().high_value(threshold)

    def get_statistics(self):
        total = self.count()

        new = self.new().count()
        processing = self.processing().count()
        delivery_count = self.delivery().count()
        completed = self.completed().count()
        cancelled = self.cancelled().count()

        today_count = self.today().count()
        week_count = self.this_week().count()
        month_count = self.this_month().count()

        delivery_today_count = self.delivery_today().count()
        delivery_tomorrow_count = self.delivery_tomorrow().count()
        overdue_count = self.overdue().count()

        total_revenue = self.aggregate(total=Sum("total_price"))["total"] or 0
        avg_order_value = self.aggregate(avg=Avg("total_price"))["avg"] or 0

        completed_revenue = self.completed().aggregate(total=Sum("total_price"))["total"] or 0

        return {
            "total_orders": total,
            "new_orders": new,
            "processing_orders": processing,
            "delivery_orders": delivery_count,
            "completed_orders": completed,
            "cancelled_orders": cancelled,
            "today_orders": today_count,
            "week_orders": week_count,
            "month_orders": month_count,
            "delivery_today": delivery_today_count,
            "delivery_tomorrow": delivery_tomorrow_count,
            "overdue": overdue_count,
            "total_revenue": total_revenue,
            "avg_order_value": avg_order_value,
            "completed_revenue": completed_revenue,
        }

    def get_kanban_data(self):
        return {
            "new": self.new(),
            "processing": self.processing(),
            "delivery": self.delivery(),
            "completed": self.completed(),
        }
