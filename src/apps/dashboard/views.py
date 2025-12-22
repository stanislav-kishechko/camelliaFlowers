from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Sum
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView

from apps.clients.models import Client
from apps.orders.models import Order, OrderItem
from apps.products.models import Product


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Provides the functionality to generate a user dashboard view
    with various statistical data.

    This class extends `LoginRequiredMixin` and `TemplateView` to
    ensure that only authenticated users can access the view. The
    dashboard includes features for generating date ranges,
    calculating sales statistics, hourly statistics, order statistics,
    and client data.

    """
    template_name = "dashboard/dashboard.html"

    def get_date_ranges(self, period="week"):
        """
        Determines date ranges and additional information for a specified period such as
        "day", "week", "month", or "year". If no valid period is provided, a default
        range for the last week will be used. Each range includes details about the
        start date, period name, and the number of relevant days for charting purposes.

        :param period: Specifies the time range to calculate. Acceptable values are
            "day", "week", "month", or "year". Defaults to "week".
        :type period: str
        :return: A dictionary containing the calculated date ranges and related details:
            - now: Current timestamp.
            - today: The current date.
            - yesterday: Yesterday's date.
            - period_start: Start date of the specified period.
            - period_name: Name of the period in Ukrainian.
            - chart_days: The number of days for charting the period.
            - period: The input period value.
        :rtype: dict
        """
        now = timezone.now()
        today = now.date()

        ranges = {
            "now": now,
            "today": today,
            "yesterday": today - timedelta(days=1),
        }

        if period == "day":
            ranges["period_start"] = today
            ranges["period_name"] = "Сьогодні"
            ranges["chart_days"] = 1

        elif period == "week":
            ranges["period_start"] = today - timedelta(days=7)
            ranges["period_name"] = "Цей тиждень"
            ranges["chart_days"] = 7

        elif period == "month":
            ranges["period_start"] = today - timedelta(days=30)
            ranges["period_name"] = "Цей місяць"
            ranges["chart_days"] = 30

        elif period == "year":
            ranges["period_start"] = today - timedelta(days=365)
            ranges["period_name"] = "Цей рік"
            ranges["chart_days"] = 365

        else:
            ranges["period_start"] = today - timedelta(days=7)
            ranges["period_name"] = "Цей тиждень"
            ranges["chart_days"] = 7

        ranges["period"] = period

        return ranges

    def get_sales_statistics(self, dates: dict):
        """
        Calculates and returns sales statistics for a given period, including total sales,
        sales for today and yesterday, percentage growth compared to yesterday,
        and the total number of orders within the period.

        :param dates: Dictionary containing date-related keys:
            - "period_start" (datetime): Start datetime of the period to calculate sales statistics.
            - "today" (date): Date representing today's date.
            - "yesterday" (date): Date representing yesterday's date.
        :type dates: dict
        :return: A dictionary with the following keys:
            - "period_sales" (Decimal): Total sales amount for the given period.
            - "today_sales" (Decimal): Total sales amount for today.
            - "yesterday_sales" (Decimal): Total sales amount for yesterday.
            - "growth_percent" (float): Percentage growth in sales compared to yesterday.
            - "orders_count" (int): Total number of orders within the given period.
        :rtype: dict
        """
        period_orders = Order.objects.filter(
            created_at__gte=dates["period_start"],
            status__in=["completed", "delivered"]
        )
        period_sales = period_orders.aggregate(total=Sum("total_price"))["total"] or Decimal("0")

        today_sales = Order.objects.filter(
            created_at__date=dates["today"],
            status__in=["completed", "delivered"]
        ).aggregate(total=Sum("total_price"))["total"] or Decimal("0")

        yesterday_sales = Order.objects.filter(
            created_at__date=dates["yesterday"],
            status__in=["completed", "delivered"]
        ).aggregate(total=Sum("total_price"))["total"] or Decimal("0")

        if yesterday_sales > 0:
            growth_percent = ((today_sales - yesterday_sales) / yesterday_sales) * 100
        else:
            growth_percent = 100 if today_sales > 0 else 0

        return {
            "period_sales": period_sales,
            "today_sales": today_sales,
            "yesterday_sales": yesterday_sales,
            "growth_percent": round(growth_percent, 1),
            "orders_count": period_orders.count(),
        }

    def get_hourly_statistics(self, dates):
        """
        Generates hourly sales and order statistics for a given day.

        This function calculates the total sales and order counts for each hour of
        the specified day, identifies the peak hour and its statistics, and returns
        the results.

        :param dates: A dictionary containing the date for which the statistics are
                      computed. It must have a key 'today' with a value of type
                      datetime.date representing the date.
        :return: A dictionary containing hourly sales and order statistics as well
                 as data about the peak hour.
        :rtype: dict
        """
        today_start = timezone.make_aware(
            datetime.combine(dates["today"], datetime.min.time())
        )

        hourly_data = []
        max_sales = Decimal("0")
        peak_hour_data = None

        for hour in range(24):
            hour_start = today_start + timedelta(hours=hour)
            hour_end = hour_start + timedelta(hours=1)

            hour_orders = Order.objects.filter(
                created_at__gte=hour_start,
                created_at__lt=hour_end,
                status__in=["completed", "delivered"]
            )

            hour_sales = hour_orders.aggregate(total=Sum("total_price"))["total"] or Decimal("0")
            hour_count = hour_orders.count()

            hour_info = {
                "hour": hour,
                "sales": hour_sales,
                "orders": hour_count,
            }

            hourly_data.append(hour_info)

            if hour_sales > max_sales:
                max_sales = hour_sales
                peak_hour_data = hour_info

        return {
            "hourly_data": hourly_data,
            "peak_hour": peak_hour_data,
        }

    def get_orders_statistics(self, dates):
        """
        Retrieves and calculates statistics related to orders based on specific date ranges
        and filters. It analyzes orders within a given period and counts orders in different
        statuses including active, new, completed, processing, and delivery.

        :param dates: A dictionary containing:
                      - "period_start": The start date of the period to filter orders.
                      - "today": The specific date to count new orders.
        :type dates: dict
        :return: A dictionary containing the following statistics:
                 - "active_orders_count": Count of active orders currently in
                   "new", "processing", or "delivery" statuses.
                 - "new_orders_count": Count of new orders created on the
                   specified date.
                 - "period_orders_count": Count of orders created from the
                   specified start period.
                 - "completed_orders": Count of completed orders during the
                   specified period.
                 - "processing_orders": Count of orders in the "processing"
                   status currently.
                 - "delivery_orders": Count of orders in the "delivery" status
                   currently.
        :rtype: dict
        """
        period_orders = Order.objects.filter(created_at__gte=dates["period_start"])

        active_orders = Order.objects.filter(
            status__in=["new", "processing", "delivery"]
        )

        new_orders_count = Order.objects.filter(
            created_at__date=dates["today"],
            status="new"
        ).count()

        completed = period_orders.filter(status="completed").count()
        processing = active_orders.filter(status="processing").count()
        delivery = active_orders.filter(status="delivery").count()

        return {
            "active_orders_count": active_orders.count(),
            "new_orders_count": new_orders_count,
            "period_orders_count": period_orders.count(),
            "completed_orders": completed,
            "processing_orders": processing,
            "delivery_orders": delivery,
        }

    def get_clients_statistics(self, dates):
        """
        Calculates and returns statistics related to clients for a specified date range.

        The statistics include the total number of clients, the count of new clients
        within a specified period, and the count of VIP clients.

        :param dates: A dictionary containing the date range for calculating the
                      statistics. The key "period_start" in the dictionary specifies
                      the start date.

        :return: A dictionary containing the following statistics:
                 - "total_clients": Total number of clients.
                 - "new_clients_count": Number of clients created after the specified
                   start date in the `dates` parameter.
                 - "vip_clients": Total number of clients marked as VIP.
        """
        new_clients = Client.objects.filter(
            created_at__gte=dates["period_start"]
        ).count()

        total_clients = Client.objects.count()

        vip_clients = Client.objects.filter(is_vip=True).count()

        return {
            "total_clients": total_clients,
            "new_clients_count": new_clients,
            "vip_clients": vip_clients,
        }

    def get_average_check(self, dates):
        """
        Calculates the average check and total count of completed orders within a given
        date range. The result is based on filtering orders with a start date greater
        than or equal to the specified period start and having the status "completed".

        :param dates: A dictionary containing the "period_start" key with a datetime
                      value representing the start of the filtering period.
        :type dates: dict
        :return: A dictionary containing:
                 - average_check: The average total price of the filtered completed orders.
                 - orders_count: The count of the filtered completed orders.
        :rtype: dict
        """
        period_orders = Order.objects.filter(
            created_at__gte=dates["period_start"],
            status="completed"
        )

        avg_check = period_orders.aggregate(avg=Avg("total_price"))["avg"] or Decimal("0")

        return {
            "average_check": avg_check,
            "orders_count": period_orders.count(),
        }

    def get_sales_chart_data(self, dates):
        """
        Generates sales chart data for a given period based on order details. The chart data is
        prepared for different time periods, including daily, weekly, monthly, and yearly analysis.

        :param dates: A dictionary containing the details of the required period such as:
                      - "period": A string representing the time period to analyze. It can be
                        "day", "week", "month", or "year".
                      - "today": A datetime instance that indicates the current date or point
                        of reference for creating the chart.
        :return: A dictionary containing:
                 - "data": A list of sales amounts for each time period.
                 - "labels": A corresponding list of labels for each time period.
        """
        sales_data = []
        labels = []

        if dates["period"] == "day":
            today_start = timezone.make_aware(
                datetime.combine(dates["today"], datetime.min.time())
            )

            for hour in range(24):
                hour_start = today_start + timedelta(hours=hour)
                hour_end = hour_start + timedelta(hours=1)

                hourly_sales = Order.objects.filter(
                    created_at__gte=hour_start,
                    created_at__lt=hour_end,
                    status__in=["completed", "delivered"]
                ).aggregate(total=Sum("total_price"))["total"] or Decimal("0")

                sales_data.append(float(hourly_sales))
                labels.append(f"{hour:02d}:00")

        elif dates["period"] == "year":
            for i in range(12):
                month_start = dates["today"].replace(day=1) - timedelta(days=30 * (11 - i))
                month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

                monthly_sales = Order.objects.filter(
                    created_at__date__gte=month_start,
                    created_at__date__lte=month_end,
                    status__in=["completed", "delivered"]
                ).aggregate(total=Sum("total_price"))["total"] or Decimal("0")

                sales_data.append(float(monthly_sales))
                labels.append(month_start.strftime("%b"))

        else:
            chart_days = 7 if dates["period"] == "week" else 30

            for i in range(chart_days):
                day = dates["today"] - timedelta(days=chart_days - 1 - i)
                daily_sales = Order.objects.filter(
                    created_at__date=day,
                    status__in=["completed", "delivered"]
                ).aggregate(total=Sum("total_price"))["total"] or Decimal("0")

                sales_data.append(float(daily_sales))

                if dates["period"] == "week":
                    days_short = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
                    labels.append(days_short[day.weekday()])
                else:
                    labels.append(day.strftime("%d.%m"))

        return {
            "data": sales_data,
            "labels": labels,
        }

    def get_top_products(self, dates):
        """
        Retrieve the top products based on their sales count within a specified date range.

        The function queries `OrderItem` objects to get the most sold product items for
        completed orders within the given date range. It annotates results with the total
        quantity sold and sales count, orders them by the total quantity sold in descending
        order, and limits the result to the top 5 products.

        If no results are found from completed orders, it defaults to retrieving the top 3
        most sold products that are active, based on the `sold` field.

        Additionally, appropriate emojis are assigned to each product based on keywords in
        their names, which represent product categories.

        :param dates: A dictionary with the date range, including a key "period_start"
            specifying the start date for filtering completed orders.
        :type dates: dict

        :return: A list of dictionaries, each containing the product name, sales count,
            and its corresponding emoji.
        :rtype: list[dict[str, Any]]
        """
        top_products_data = OrderItem.objects.filter(
            order__created_at__gte=dates["period_start"],
            order__status="completed"
        ).values("product_id").annotate(
            sales_count=Count("id"),
            total_quantity=Sum("quantity")
        ).order_by("-total_quantity")[:5]

        products_with_sales = []
        for item in top_products_data:
            try:
                product = Product.objects.get(id=item["product_id"])
                products_with_sales.append({
                    "product": product,
                    "sales_count": item["total_quantity"]
                })
            except Product.DoesNotExist:
                continue

        if not products_with_sales:
            products = Product.objects.filter(
                is_active=True,
                sold__gt=0
            ).order_by("-sold")[:3]

            products_with_sales = [
                {"product": p, "sales_count": p.sold}
                for p in products
            ]

        emoji_map = {
            "троянд": "🌹", "тюльпан": "🌷", "лілі": "🌺",
            "орхідей": "🌸", "композиці": "💐", "букет": "💐",
            "піон": "🌺", "хризантем": "🌼", "гортензі": "💮",
        }

        result = []
        for item in products_with_sales:
            product = item["product"]
            emoji = "🌸"

            for keyword, prod_emoji in emoji_map.items():
                if keyword in product.name.lower():
                    emoji = prod_emoji
                    break

            result.append({
                "name": product.name,
                "sales_count": item["sales_count"],
                "emoji": emoji,
            })

        return result

    def get_recent_orders(self, limit=5):
        """
        Retrieve a list of recent orders with detailed information. The number of orders
        retrieved is determined by the specified limit. This function queries the
        database for orders and includes the related client and product details for
        each order.

        :param limit: The maximum number of recent orders to retrieve. Defaults to 5.
        :type limit: int

        :return: A list of dictionaries containing order information, including
            order id, client name, client phone, product name, total price,
            status, and status display value.
        :rtype: list[dict]
        """
        orders = Order.objects.select_related(
            "client"
        ).prefetch_related("items__product").order_by("-created_at")[:limit]

        orders_list = []
        for order in orders:
            first_item = order.items.first()
            product_name = first_item.product.name if first_item else "Немає продуктів"

            orders_list.append({
                "id": order.id,
                "client_name": order.client.full_name,
                "client_phone": order.client.phone,
                "product_name": product_name,
                "total": order.total_price,
                "status": order.status,
                "get_status_display": order.get_status_display(),
            })

        return orders_list

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests for the view. The method processes the request,
        determines the requested period, and either fetches AJAX data or calls
        the parent class's GET method based on the request type.

        :param request: The HTTP request object.
        :type request: HttpRequest
        :param args: Additional positional arguments passed to the method.
        :type args: tuple
        :param kwargs: Additional keyword arguments passed to the method.
        :type kwargs: dict
        :return: The HTTP response object. If the request is a standard request,
            the response is returned by the parent class's GET method.
            If the request is an AJAX request, it returns the AJAX data
            specific to the requested period.
        :rtype: HttpResponse
        """
        period = request.GET.get("period", "week")

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return self.get_ajax_data(period)

        return super().get(request, *args, **kwargs)

    def get_ajax_data(self, period):
        """
        Gets AJAX data for a specified time period and processes it to return various
        statistics, such as sales data, order counts, client statistics, average
        check, charts, and top products. If the requested period is "day", it also
        includes detailed hourly statistics.

        :param period: The time period for which data and statistics are requested.
        :type period: str
        :return: JSON response containing aggregated and processed data for the given
                 period, including statistics and charts. For "day" period,
                 includes hourly statistics and peak hour data.
        :rtype: JsonResponse
        """
        dates = self.get_date_ranges(period)

        sales_stats = self.get_sales_statistics(dates)
        orders_stats = self.get_orders_statistics(dates)
        clients_stats = self.get_clients_statistics(dates)
        check_stats = self.get_average_check(dates)
        chart_data = self.get_sales_chart_data(dates)
        top_products = self.get_top_products(dates)

        data = {
            "period": period,
            "period_name": dates["period_name"],
            "today_sales": float(sales_stats["today_sales"]),
            "sales_growth_percent": sales_stats["growth_percent"],
            "active_orders_count": orders_stats["active_orders_count"],
            "new_orders_count": orders_stats["new_orders_count"],
            "total_clients": clients_stats["total_clients"],
            "new_clients_count": clients_stats["new_clients_count"],
            "average_check": float(check_stats["average_check"]),
            "sales_data": chart_data["data"],
            "sales_labels": chart_data["labels"],
            "top_products": top_products,
        }

        if period == "day":
            hourly_stats = self.get_hourly_statistics(dates)
            data["hourly_statistics"] = [
                {
                    "hour": h["hour"],
                    "sales": float(h["sales"]),
                    "orders": h["orders"]
                } for h in hourly_stats["hourly_data"]
            ]
            if hourly_stats["peak_hour"]:
                data["peak_hour"] = {
                    "hour": hourly_stats["peak_hour"]["hour"],
                    "sales": float(hourly_stats["peak_hour"]["sales"]),
                    "orders": hourly_stats["peak_hour"]["orders"],
                }

        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        """
        Generate context data for a view with various statistics, sales data, and other required
        information based on the specified period.

        :param kwargs: Additional keyword arguments passed to the view context.
        :return: Updated context containing statistics and data, including sales, orders,
            clients, and top products.
        :rtype: dict
        """
        context = super().get_context_data(**kwargs)

        period = self.request.GET.get("period", "week")
        dates = self.get_date_ranges(period)

        sales_stats = self.get_sales_statistics(dates)
        context["today_sales"] = sales_stats["today_sales"]
        context["sales_growth_percent"] = sales_stats["growth_percent"]
        context["period_sales"] = sales_stats["period_sales"]

        orders_stats = self.get_orders_statistics(dates)
        context["active_orders_count"] = orders_stats["active_orders_count"]
        context["new_orders_count"] = orders_stats["new_orders_count"]
        context["period_orders_count"] = orders_stats["period_orders_count"]

        clients_stats = self.get_clients_statistics(dates)
        context["total_clients"] = clients_stats["total_clients"]
        context["new_clients_count"] = clients_stats["new_clients_count"]
        context["vip_clients"] = clients_stats["vip_clients"]

        check_stats = self.get_average_check(dates)
        context["average_check"] = check_stats["average_check"]

        chart_data = self.get_sales_chart_data(dates)
        context["sales_data"] = chart_data["data"]
        context["sales_labels"] = chart_data["labels"]

        context["is_day_period"] = (period == "day")
        if period == "day":
            hourly_stats = self.get_hourly_statistics(dates)
            context["hourly_statistics"] = hourly_stats["hourly_data"]
            context["peak_hour"] = hourly_stats["peak_hour"]
        else:
            context["peak_hour"] = None

        context["top_products"] = self.get_top_products(dates)

        context["recent_orders"] = self.get_recent_orders(limit=5)

        context["current_period"] = period
        context["period_name"] = dates["period_name"]

        return context
