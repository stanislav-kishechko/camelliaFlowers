from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Optional

from django.db import models
from django.db.models import QuerySet, Sum
from django.utils import timezone

from apps.clients.querysets import ClientQuerySet


class ClientManager(models.Manager):
    """
    Provides additional methods for querying and managing Client objects.

    This manager is used to encapsulate query logic and provide methods that
    allow filtering, searching, sorting, and statistical computations for
    Client objects. It extends the functionality of Django's default manager
    by adding domain-specific queries and operations.

    :ivar model: The model associated with this manager.
    :type model: models.Model
    :ivar _db: The database used for the queries.
    :type _db: str
    """

    def get_queryset(self) -> ClientQuerySet:
        """
        Constructs and returns a new instance of the `ClientQuerySet` initialized with the
        current model and database connection.

        :return: The `ClientQuerySet` instance initialized with the model
            and database connection.
        :rtype: ClientQuerySet
        """
        return ClientQuerySet(self.model, using=self._db)

    def search(self, query: str) -> QuerySet["Client"]:
        """
        Searches for clients using the given query and returns a filtered query
        set based on the search terms. This method is designed to operate on
        the queryset of the `Client` model and applies the search logic.

        :param query: The search string used to filter the client queryset.
        :type query: str

        :return: A queryset containing the filtered results matching the search query.
        :rtype: QuerySet[Client]
        """
        return self.get_queryset().search(query)

    def by_type(self, client_type: str) -> QuerySet["Client"]:
        """
        Retrieve all Client objects filtered by their type.

        This method filters the queryset of Client objects based on the type
        specified. The expected input is a string representing the type of
        client, and it will return a QuerySet containing all the clients that
        match this type.

        :param client_type: The type of client to filter by.
        :type client_type: str
        :return: A QuerySet of Client objects filtered by the specified type.
        :rtype: QuerySet["Client"]
        """
        return self.get_queryset().by_type(client_type)

    def sort_by(self, sort_option: str) -> QuerySet["Client"]:
        """
        Sorts the queryset of clients based on the provided sorting option.

        This method allows the caller to define a sorting strategy by specifying
        a sort option string, which will be applied to the queryset. The method
        returns a sorted queryset of clients.

        :param sort_option: The sorting option to be applied to the queryset.
        :type sort_option: str
        :return: A queryset of clients sorted by the specified option.
        :rtype: QuerySet["Client"]
        """
        return self.get_queryset().sort_by(sort_option)

    def active(self) -> QuerySet["Client"]:
        """
        Retrieves the active objects from the queryset.

        :return: A queryset containing only active `Client` objects.
        :rtype: QuerySet[Client]
        """
        return self.get_queryset().active()

    def vip(self) -> QuerySet["Client"]:
        """
        Retrieve a QuerySet containing clients marked as VIP.

        :return: A QuerySet of clients categorized as VIP.
        :rtype: QuerySet[Client]
        """
        return self.get_queryset().vip()

    def regular(self) -> QuerySet["Client"]:
        """
        Retrieves a queryset containing regular clients.

        This method provides access to a filtered queryset of clients marked as
        regular. It calls the `regular` method on the base queryset to apply the
        filtering logic.

        :return: A queryset of regular clients.
        :rtype: QuerySet[Client]
        """
        return self.get_queryset().regular()

    def with_orders(self) -> QuerySet["Client"]:
        """
        Returns a QuerySet containing Clients with related orders.

        This method fetches the Clients along with their associated orders
        from the database, providing an extended QuerySet for further
        manipulations or filtering.

        :return: A QuerySet instance including the Clients with their
                 respective orders.
        :rtype: QuerySet["Client"]
        """
        return self.get_queryset().with_orders()

    def without_orders(self) -> QuerySet["Client"]:
        """
        Filters and retrieves a queryset of all clients who have not placed any orders.

        :return: QuerySet of `Client` objects without any orders
        :rtype: QuerySet
        """
        return self.get_queryset().without_orders()

    def top_buyers(self, limit: int = 10) -> QuerySet["Client"]:
        """
        Returns the top buyers from the client queryset based on the given limit.

        This method retrieves a queryset containing the top buyers from the Client
        model. It helps in filtering and fetching a specific number of top buyers
        based on their purchase ranking.

        :param limit: The maximum number of top buyers to retrieve. The default is 10.
        :type limit: int
        :return: A queryset containing the top clients ranked by their purchase history.
        :rtype: QuerySet[Client]
        """
        return self.get_queryset().top_buyers(limit)

    def recent(self, days: int = 30) -> QuerySet["Client"]:
        """
        Retrieve clients added within the specified number of days.

        This method returns a queryset of clients added within the last `days` days.
        If no value is specified for `days`, it defaults to 30 days.

        :param days: The number of most recent days within which clients were added.
        :type days: int
        :return: Queryset containing clients added in the specified timeframe.
        :rtype: QuerySet[Client]
        """
        return self.get_queryset().recent(days)

    def by_spending_range(
        self, min_amount: float | int | None = None, max_amount: float | int | None = None
    ) -> QuerySet["Client"]:
        """
        Filter clients based on their spending range. This method allows you to query clients
        whose spending falls within a specified minimum and/or maximum amount. If no range is
        provided, all clients are returned.

        :param min_amount: Minimum spending amount to filter clients. Can be a float, int,
            or None to include all clients without a lower bound.
        :param max_amount: Maximum spending amount to filter clients. Can be a float, int,
            or None to include all clients without an upper bound.
        :return: QuerySet of clients matching the specified spending range.
        :rtype: QuerySet[Client]
        """
        return self.get_queryset().by_spending_range(min_amount, max_amount)

    def with_email(self) -> QuerySet["Client"]:
        """
        Filters the queryset to include only clients with a specified email associated
        with them. This should be used in cases where email filtering is explicitly
        required.

        :return: A filtered QuerySet including only clients with an email.
        :rtype: QuerySet["Client"]
        """
        return self.get_queryset().with_email()

    def get_statistics(self) -> Dict[str, Any]:
        """Compute basic statistics for clients collection.

        Returns:
            dict: Basic aggregate metrics such as totals and averages.
        """
        total = self.count()
        active = self.active().count()
        vip = self.vip().count()

        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_this_month = self.filter(created_at__gte=thirty_days_ago).count()

        total_spent = self.aggregate(total=Sum("total_spent"))["total"] or 0
        avg_spent = total_spent / total if total > 0 else 0

        return {
            "total_clients": total,
            "active_clients": active,
            "vip_clients": vip,
            "new_clients_month": new_this_month,
            "average_order": round(avg_spent, 2),
            "total_revenue": total_spent,
        }
