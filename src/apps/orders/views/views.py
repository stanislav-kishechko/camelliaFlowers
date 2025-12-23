from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView

from apps.clients.models import Client
from apps.orders.models import Order
from apps.products.models import Product


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    paginate_by = 20

    def get_queryset(self):
        queryset = Order.objects.select_related("client").prefetch_related(
            "items__product"
        )

        search_query = self.request.GET.get("search", "")
        status_filter = self.request.GET.get("status", "all")
        date_range = self.request.GET.get("date_range", "all")
        sort_option = self.request.GET.get("sort", "date_desc")

        if search_query:
            queryset = queryset.search(search_query)

        if status_filter and status_filter != "all":
            queryset = queryset.by_status(status_filter)

        if date_range and date_range != "all":
            queryset = queryset.by_date_range(date_range)

        queryset = queryset.sort_by(sort_option)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        base_queryset = Order.objects.select_related("client").prefetch_related(
            "items__product"
        )

        search_query = self.request.GET.get("search", "")
        date_range = self.request.GET.get("date_range", "all")

        if search_query:
            base_queryset = base_queryset.search(search_query)

        if date_range and date_range != "all":
            base_queryset = base_queryset.by_date_range(date_range)

        context["new_orders"] = base_queryset.new()
        context["processing_orders"] = base_queryset.processing()
        context["delivery_orders"] = base_queryset.delivery()
        context["completed_orders"] = base_queryset.completed()
        context["cancelled_orders"] = base_queryset.cancelled()

        context["statistics"] = Order.objects.get_statistics()

        context["search_query"] = search_query
        context["status_filter"] = self.request.GET.get("status", "all")
        context["date_range"] = date_range
        context["sort_option"] = self.request.GET.get("sort", "date_desc")

        context["delivery_today"] = base_queryset.delivery_today()
        context["delivery_tomorrow"] = base_queryset.delivery_tomorrow()
        context["overdue_orders"] = base_queryset.overdue()

        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    """
    Handles the detailed representation of an order, including its associated
    data and context-specific information.

    The class is designed to extend the `DetailView` functionality, and it is
    intended to present a focused view on an individual order. The template
    provides data-rich context with details about the order, client, products,
    and other supportive data.

    :ivar model: Specifies the model type for the view.
    :type model: Order
    :ivar template_name: The path to the template file used for rendering
        the detail view.
    :type template_name: str
    :ivar context_object_name: The name under which the context object is
        passed to the template.
    :type context_object_name: str
    """
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.select_related("client").prefetch_related(
            "items__product__category",
            "status_history__changed_by"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object

        context["available_statuses"] = [
            (status_value, status_label)
            for status_value, status_label in order._meta.get_field("status").choices
            if order.can_transition_to(status_value)
        ]

        status_colors = {
            "new": "blue",
            "processing": "yellow",
            "delivery": "purple",
            "completed": "green",
            "cancelled": "red",
        }
        context["status_color"] = status_colors.get(order.status, "gray")

        context["clients"] = Client.objects.filter(is_active=True).order_by("first_name")
        context["products"] = Product.objects.filter(status='in_stock').order_by("name")

        context["status_timeline"] = order.get_status_timeline()

        context["client_stats"] = {
            "total_orders": order.client.orders.count(),
            "completed_orders": order.client.orders.completed().count(),
            "total_spent": order.client.total_spent,
            "avg_order_value": order.client.orders.aggregate(
                avg=Avg('total_price')
            )['avg'] or 0
        }

        return context


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    """
    Handles the deletion of Order instances through a view.

    This view is used to delete Order objects from the database. It ensures that the
    deletion process is accessible only to logged-in users. The view provides a
    customized success message upon successful deletion of the order and displays
    details of the order before its deletion. The class is configured to use a template
    for rendering the confirmation page and supports processing of related and prefetch
    querysets for efficient access to related objects.

    :ivar model: The model class associated with this view.
    :type model: Type[Order]
    :ivar success_url: URL to redirect to after successful deletion of an order.
    :type success_url: str
    :ivar template_name: Path to the template used for the order delete confirmation page.
    :type template_name: str
    """
    model = Order
    success_url = reverse_lazy("orders:orders")
    template_name = "orders/partials/order_delete_partial.html"

    def get_queryset(self):
        return Order.objects.select_related("client").prefetch_related(
            "items__product"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.object

        context["order_info"] = {
            "client_name": order.client.full_name,
            "total_price": order.total_price,
            "items_count": order.items.count(),
            "status": order.get_status_display(),
            "created_at": order.created_at,
        }

        context["order_items"] = order.items.select_related("product").all()

        return context

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        order_id = order.id
        client_name = order.client.full_name
        total_price = order.total_price

        messages.success(
            request,
            f"Замовлення #{order_id} ({client_name}) на суму ₴{total_price} успішно видалено"
        )

        return super().delete(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
