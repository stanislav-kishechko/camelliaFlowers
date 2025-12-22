from datetime import timedelta

from django.db import models
from django.db.models import Q
from django.utils import timezone


class OrderQuerySet(models.QuerySet):
    """
    Provides custom filtering, searching, and sorting functionality for orders.

    This class extends the base Django QuerySet to include additional methods
    tailored for querying specific attributes of orders in an application.
    It includes utilities to filter orders by various criteria such as
    status, date, client, product, delivery date, price range, and more.
    Additionally, it provides methods to sort orders in various ways.

    :ivar model: The model associated with this QuerySet.
    :type model: Type[Model]
    """
    def search(self, query):
        if not query:
            return self

        return self.filter(
            Q(id__icontains=query) |
            Q(client__first_name__icontains=query) |
            Q(client__last_name__icontains=query) |
            Q(client__phone__icontains=query) |
            Q(delivery_address__icontains=query)
        )

    def by_status(self, status):
        if not status or status == "all":
            return self

        return self.filter(status=status)

    def by_date_range(self, date_range):
        today = timezone.now().date()

        if date_range == "today":
            return self.filter(created_at__date=today)
        elif date_range == "week":
            week_ago = today - timedelta(days=7)
            return self.filter(created_at__date__gte=week_ago)
        elif date_range == "month":
            month_ago = today - timedelta(days=30)
            return self.filter(created_at__date__gte=month_ago)
        elif date_range == "year":
            year_ago = today - timedelta(days=365)
            return self.filter(created_at__date__gte=year_ago)

        return self

    def by_delivery_date(self, delivery_date):
        if not delivery_date:
            return self

        if delivery_date == "today":
            return self.filter(delivery_date=timezone.now().date())

        elif delivery_date == "tomorrow":
            tomorrow = timezone.now().date() + timedelta(days=1)

            return self.filter(delivery_date=tomorrow)

        elif delivery_date == "this_week":
            today = timezone.now().date()
            week_end = today + timedelta(days=7)

            return self.filter(delivery_date__range=[today, week_end])

        return self

    def by_client(self, client_id):
        if not client_id:
            return self

        return self.filter(client_id=client_id)

    def by_product(self, product_id):
        if not product_id:
            return self

        return self.filter(product_id=product_id)

    def sort_by(self, sort_option):
        sort_options = {
            "date_desc": "-created_at",
            "date_asc": "created_at",
            "price_desc": "-total_price",
            "price_asc": "total_price",
            "delivery": "delivery_date",
            "client": "client__first_name",
        }
        return self.order_by(sort_options.get(sort_option, "-created_at"))

    def new(self):
        return self.filter(status="new")

    def processing(self):
        return self.filter(status="processing")

    def delivery(self):
        return self.filter(status="delivery")

    def completed(self):
        return self.filter(status="completed")

    def cancelled(self):
        return self.filter(status="cancelled")

    def active(self):
        return self.exclude(status__in=["completed", "cancelled"])

    def today(self):
        return self.filter(created_at__date=timezone.now().date())

    def this_week(self):
        week_ago = timezone.now() - timedelta(days=7)

        return self.filter(created_at__gte=week_ago)

    def this_month(self):
        month_ago = timezone.now() - timedelta(days=30)

        return self.filter(created_at__gte=month_ago)

    def recent(self, days=7):
        date_from = timezone.now() - timedelta(days=days)

        return self.filter(created_at__gte=date_from)

    def delivery_today(self):
        return self.filter(delivery_date=timezone.now().date())

    def delivery_tomorrow(self):
        tomorrow = timezone.now().date() + timedelta(days=1)

        return self.filter(delivery_date=tomorrow)

    def delivery_this_week(self):
        today = timezone.now().date()
        week_end = today + timedelta(days=7)

        return self.filter(delivery_date__range=[today, week_end])

    def overdue(self):
        return self.filter(
            delivery_date__lt=timezone.now().date(),
            status__in=["new", "processing", "delivery"]
        )

    def by_price_range(self, min_price=None, max_price=None):
        queryset = self

        if min_price is not None:
            queryset = queryset.filter(total_price__gte=min_price)

        if max_price is not None:
            queryset = queryset.filter(total_price__lte=max_price)

        return queryset

    def high_value(self, threshold=5000):
        return self.filter(total_price__gte=threshold)
