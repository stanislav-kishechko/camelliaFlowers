from decimal import Decimal
from typing import Any, Dict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, Page, PageNotAnInteger, Paginator
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.clients.forms import ClientForm
from apps.clients.models import Client


class ClientListView(LoginRequiredMixin, ListView):
    """List view for clients with search, filter, and sort options.

    Attributes:
        model: The model this view operates on.
        template_name: Path to the template used for rendering the list.
        context_object_name: The context key for the queryset.
        paginate_by: Number of items per page.
    """

    model = Client
    template_name = "clients/client_list.html"
    context_object_name = "clients"
    paginate_by = 8

    def get_queryset(self) -> QuerySet[Client]:
        """Return filtered and sorted queryset based on query parameters.

        Query params:
            search: Full-text search string.
            type: Client type filter (e.g., "all", "vip", etc.).
            sort: Sort key (e.g., "date").

        Returns:
            QuerySet[Client]: The filtered and sorted queryset.
        """
        queryset: QuerySet[Client] = Client.objects.all()

        search_query: str = self.request.GET.get("search", "")
        if search_query:
            queryset = queryset.search(search_query)

        client_type: str = self.request.GET.get("type", "all")
        if client_type != "all":
            queryset = queryset.by_type(client_type)

        sort_by: str = self.request.GET.get("sort", "date")
        queryset = queryset.sort_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add statistics and filter/sort values to context.

        Args:
            **kwargs: Base context from the parent implementation.

        Returns:
            dict: The updated template context.
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)

        stats: Dict[str, Any] = Client.objects.get_statistics()
        context.update(stats)

        context["search_query"] = self.request.GET.get("search", "")
        context["client_type"] = self.request.GET.get("type", "all")
        context["sort_by"] = self.request.GET.get("sort", "date")

        return context


class ClientDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a single client, including paginated orders and stats."""

    model = Client
    template_name = "clients/client_detail.html"
    context_object_name = "client"
    paginate_by = 2

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Provide client details with a paginated list of orders and stats.

        Args:
            **kwargs: Base context from the parent implementation.

        Returns:
            dict: The context including paginated orders and simple stats.
        """
        context: Dict[str, Any] = super().get_context_data(**kwargs)

        client: Client = self.get_object()  # type: ignore[assignment]

        all_orders = client.orders.select_related().order_by("-created_at")

        page_param: str | int = self.request.GET.get("page", 1)
        paginator: Paginator = Paginator(all_orders, self.paginate_by)

        try:
            orders_page: Page = paginator.page(page_param)
        except PageNotAnInteger:
            orders_page = paginator.page(1)
        except EmptyPage:
            orders_page = paginator.page(paginator.num_pages)

        context["page_obj"] = orders_page
        context["orders"] = orders_page

        total_orders: int = client.orders_count
        total_spent: Decimal = client.total_spent

        if total_orders > 0:
            average_order: Decimal = total_spent / Decimal(total_orders)
        else:
            average_order = Decimal("0.00")

        context["orders_stats"] = {
            "average_order": average_order,
        }

        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    """Create view for clients with VIP auto-flag and user feedback messages."""

    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("clients:clients")

    def form_valid(self, form: ClientForm) -> HttpResponse:
        """Handle valid form submission.

        If the submitted client type is "vip", automatically set the `is_vip` flag
        on the instance, then delegate to the parent and add a success message.

        Args:
            form: Bound and valid `ClientForm` instance.

        Returns:
            HttpResponse: Redirect to the success URL.
        """
        if form.cleaned_data.get("client_type") == "vip":
            form.instance.is_vip = True

        response = super().form_valid(form)
        messages.success(self.request, f"Клієнта {self.object.full_name} успішно додано!")
        return response

    def form_invalid(self, form: ClientForm) -> HttpResponse:
        """Handle invalid form submission with an error message.

        Args:
            form: Bound but invalid form instance.

        Returns:
            HttpResponse: Redirect back to clients list.
        """
        messages.error(
            self.request,
            "Помилка при додаванні клієнта. Перевірте введені дані.",
        )
        return redirect("clients:clients")


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """Update view for clients with VIP toggle derived from form data."""

    model = Client
    form_class = ClientForm
    template_name = "clients/partials/client_edit_partial.html"
    context_object_name = "client"

    def get_success_url(self) -> str:
        """Return the URL to redirect to after successful update."""
        return str(reverse_lazy("clients:client_detail", kwargs={"pk": self.object.pk}))

    def form_valid(self, form: ClientForm) -> HttpResponse:
        """Handle valid form submission and update VIP status.

        Args:
            form: Bound and valid `ClientForm` instance.

        Returns:
            HttpResponse: Redirect to the client detail page.
        """
        if form.cleaned_data.get("client_type") == "vip":
            form.instance.is_vip = True
        else:
            form.instance.is_vip = False

        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Дані клієнта {self.object.full_name} успішно оновлено!",
        )
        return response

    def form_invalid(self, form: ClientForm) -> HttpResponse:
        """Handle invalid form submission with an error message."""
        messages.error(self.request, "Помилка при оновленні даних клієнта.")
        return super().form_invalid(form)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    """Delete view for clients with a success message on completion."""

    model = Client
    template_name = "clients/partials/client_delete_partial.html"
    context_object_name = "client"
    success_url = reverse_lazy("clients:clients")

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Delete the client and notify the user.

        Args:
            request: Current HTTP request.
            *args: Positional args passed to the parent implementation.
            **kwargs: Keyword args passed to the parent implementation.

        Returns:
            HttpResponse: Redirect to the list page.
        """
        client: Client = self.get_object()
        client_name = client.full_name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Клієнта {client_name} успішно видалено!")
        return response


class ClientToggleVIPView(LoginRequiredMixin, View):
    """Handle toggling of a client's VIP status via POST requests."""

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Toggle VIP status for the given client.

        Args:
            request: Current HTTP request.
            pk: Primary key of the client to toggle.

        Returns:
            HttpResponse: Redirect back to the referrer or clients list.
        """
        client: Client = get_object_or_404(Client, pk=pk)

        if client.is_vip:
            client.remove_vip()
            status = "звичайним"
        else:
            client.make_vip()
            status = "VIP"

        messages.success(request, f"Клієнт {client.full_name} тепер має статус {status}")

        return redirect(request.META.get("HTTP_REFERER", "clients:clients"))
