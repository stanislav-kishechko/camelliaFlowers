from __future__ import annotations

from datetime import timedelta

from django.db import models
from django.db.models import Q, QuerySet
from django.utils import timezone


class ClientQuerySet(models.QuerySet):
    """Reusable filters and sorters for client queries."""

    def search(self, query: str | None) -> ClientQuerySet | QuerySet:
        """
        Filters and searches for objects within the current queryset based on the provided
        query. If no query is provided, the original queryset is returned.

        :param query: A string containing the search criteria or None. If provided, the filter
          will search for objects where the first name, last name, phone, or email contains
          the query string.
        :return: A filtered queryset containing objects that match the search criteria, or the
          original queryset if no query is provided.
        :rtype: ClientQuerySet | QuerySet
        """
        if not query:
            return self

        return self.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(phone__icontains=query)
            | Q(email__icontains=query)
        )

    def by_type(self, client_type: str) -> "ClientQuerySet":
        """
        Filters the queryset based on the specified client type. The client types include
        'active', 'vip', 'new', and 'inactive'. Each type applies a different filter logic
        to the queryset. If no valid type is provided, the original queryset is returned.

        :param client_type: The type of clients to filter by. Should be one of 'active',
            'vip', 'new', or 'inactive'.
        :type client_type: str
        :return: A queryset filtered according to the specified client type. If the
            provided type does not match any predefined types, the unfiltered queryset
            is returned.
        :rtype: ClientQuerySet
        """
        if client_type == "active":
            return self.filter(is_active=True)
        elif client_type == "vip":
            return self.filter(is_vip=True)
        elif client_type == "new":
            thirty_days_ago = timezone.now() - timedelta(days=30)

            return self.filter(created_at__gte=thirty_days_ago)
        elif client_type == "inactive":
            return self.filter(is_active=False)

        return self

    def by_city(self, city: str | None) -> "ClientQuerySet":
        """
        Filters the queryset by the specified city. If the city parameter is not provided
        or is None, the method returns the original queryset unfiltered. Otherwise, it
        returns a queryset filtered to include only entries where the city matches exactly,
        case-insensitively.

        :param city: The name of the city to filter the queryset by. If None, no filtering
                     is applied.
        :type city: str | None
        :return: A filtered queryset if a city is specified, otherwise the original queryset.
        :rtype: ClientQuerySet
        """
        if not city:
            return self

        return self.filter(city__iexact=city)

    def sort_by(self, sort_option: str) -> "ClientQuerySet":
        """
        Sorts a queryset of clients based on the given sort option.

        The method allows sorting clients by their name, the number of orders,
        the total amount spent, or the date they joined. If the provided sort
        option is invalid or unavailable, the queryset will default to sorting
        by the date of creation.

        :param sort_option: A string indicating the sorting criteria. Acceptable
            values are:
            - "name": Sorts clients alphabetically by first and last name.
            - "orders": Sorts clients in descending order of the number of orders.
            - "spent": Sorts clients in descending order of total amount spent.
            - "date": Sorts clients in descending order of account creation date.
        :return: A `ClientQuerySet` instance, ordered according to the specified
            sort criteria.
        :rtype: ClientQuerySet
        """
        if sort_option == "name":
            return self.order_by("first_name", "last_name")

        elif sort_option == "orders":
            return self.order_by("-orders_count")

        elif sort_option == "spent":
            return self.order_by("-total_spent")

        elif sort_option == "date":
            return self.order_by("-created_at")

        return self.order_by("-created_at")

    def active(self) -> "ClientQuerySet":
        """
        Filters the query to return only active objects.

        :return: Queryset containing only the objects where the `is_active` field
            is set to True.
        :rtype: ClientQuerySet
        """
        return self.filter(is_active=True)

    def vip(self) -> "ClientQuerySet":
        """
        Filters and returns only VIP clients from the queryset.

        :rtype: ClientQuerySet
        :return: A queryset containing clients marked as VIP.
        """
        return self.filter(is_vip=True)

    def regular(self) -> "ClientQuerySet":
        """
        Filters and returns a queryset containing only regular (non-VIP) clients.

        This method applies a filter to exclude any client entries marked as VIP
        and returns the resulting queryset. It provides a convenient way to focus
        on regular clients when working with the dataset.

        :return: A queryset of clients filtered to include only regular (non-VIP) ones.
        :rtype: ClientQuerySet
        """
        return self.filter(is_vip=False)

    def with_orders(self) -> "ClientQuerySet":
        """
        Filters a queryset to include only the objects that have one or more associated
        orders. This method acts as a helper to refine the dataset by applying a
        condition that checks the `orders_count` field.

        :return: A filtered `ClientQuerySet` containing only objects where the
            `orders_count` field is greater than 0.
        :rtype: ClientQuerySet
        """
        return self.filter(orders_count__gt=0)

    def without_orders(self) -> "ClientQuerySet":
        """
        Filters the queryset to include only clients who have no orders.

        :return: A queryset containing clients with zero orders.
        :rtype: ClientQuerySet
        """
        return self.filter(orders_count=0)

    def top_buyers(self, limit: int = 10) -> "ClientQuerySet":
        """
        Fetches the top buyers based on their total spending, ordered in descending order.

        This method retrieves a list of clients who have spent more than 0 and orders them by
        their total spending in descending order. A maximum of `limit` clients will be returned.

        :param limit: The maximum number of top buyers to retrieve. Defaults to 10.
        :type limit: int
        :return: A queryset containing the top buyers, ordered by total spending.
        :rtype: ClientQuerySet
        """
        return self.filter(total_spent__gt=0).order_by("-total_spent")[:limit]

    def recent(self, days: int = 30) -> "ClientQuerySet":
        """
        Filter and return a queryset of objects created within the specified number of days from the current date. This method
        relies on the `created_at` field to perform the filtering. If no value is provided for the number of days, it defaults
        to 30.

        :param days: The number of days to look back from the current date to include objects in the queryset.
        :type days: int
        :return: A queryset of objects created within the specified number of days.
        :rtype: ClientQuerySet
        """
        date_from = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=date_from)

    def by_spending_range(
        self, min_amount: float | int | None = None, max_amount: float | int | None = None
    ) -> "ClientQuerySet":
        """
        Filters the queryset based on a specified spending range. Allows filtering clients whose
        total spending is greater than or equal to a minimum amount and/or less than or equal to
        a maximum amount. If one of the parameters is omitted, filtering is applied only based
        on the other parameter. If both parameters are omitted, no filtering is applied, and the
        original queryset is returned unchanged.

        :param min_amount: The minimum spending amount to filter clients by. If None, no lower
                           spending limit is applied.
        :param max_amount: The maximum spending amount to filter clients by. If None, no upper
                           spending limit is applied.
        :return: A filtered queryset of clients within the specified spending range.
        :rtype: ClientQuerySet
        """
        queryset: ClientQuerySet = self

        if min_amount is not None:
            queryset = queryset.filter(total_spent__gte=min_amount)

        if max_amount is not None:
            queryset = queryset.filter(total_spent__lte=max_amount)

        return queryset

    def with_email(self) -> "ClientQuerySet":
        """
        Filters the queryset to include only instances that have a non-null and non-empty email field.

        :return: A queryset containing objects with a valid email field.
        :rtype: ClientQuerySet
        """
        return self.exclude(Q(email__isnull=True) | Q(email=""))
