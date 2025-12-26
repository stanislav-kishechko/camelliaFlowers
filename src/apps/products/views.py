from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.products.forms import ProductForm
from apps.products.models import Product, ProductCategory


class ProductListView(LoginRequiredMixin, ListView):
    """
    Represents a view to display a list of products.

    This class is responsible for displaying a paginated list of products while allowing
    filtering, searching, sorting, and categorization of products. It requires a user
    to be logged in to access the view.

    :ivar model: The model associated with this view.
    :type model: Product
    :ivar template_name: The template to use for rendering the view.
    :type template_name: str
    :ivar context_object_name: The name of the context variable containing the list of products.
    :type context_object_name: str
    :ivar paginate_by: The number of products to display per page.
    :type paginate_by: int
    """
    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 8

    def get_queryset(self):
        queryset = Product.objects.select_related("category")

        search_query = self.request.GET.get("search", "").strip()
        queryset = queryset.search(search_query)

        category_id = self.request.GET.get("category")
        queryset = queryset.by_category(category_id)

        status_filter = self.request.GET.get("status")
        queryset = queryset.by_stock_status(status_filter)

        sort_by = self.request.GET.get("sort", "name")
        queryset = queryset.sort_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["total_products"] = Product.objects.count()
        context["in_stock"] = Product.objects.filter(stock__gt=0).count()
        context["low_stock"] = Product.objects.filter(stock__lte=10, stock__gt=0).count()

        avg_price = Product.objects.aggregate(avg=Avg("price"))["avg"]
        context["avg_price"] = f"{avg_price:,.2f}" if avg_price else "0.00"

        context["categories"] = ProductCategory.objects.all()

        context["current_search"] = self.request.GET.get("search", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_status"] = self.request.GET.get("status", "")
        context["current_sort"] = self.request.GET.get("sort", "name")

        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    """
    Handles the creation of new Product instances.

    This class provides the functionality to create and save new instances of
    Product using a form. It ensures that the user creating the product is
    authenticated and redirects to a success URL on successful submission or
    displays appropriate error messages on invalid submission.

    :ivar model: The model associated with this view.
    :type model: type[Product]
    :ivar form_class: The form class used to create a new product.
    :type form_class: type[ProductForm]
    :ivar success_url: The URL to redirect to upon successful product creation.
    :type success_url: str
    """
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("products:products")

    def form_valid(self, form):
        messages.success(
            self.request,
            f"✅ Продукт \"{form.instance.name}\" успішно додано!"
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "❌ Помилка при додаванні продукту. Перевірте дані.")
        return super().form_invalid(form)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating an existing product.

    This class-based view allows users to update the details of an existing
    product in the database. It enforces login requirements to ensure only
    authenticated users can access the update functionality. The view handles
    both displaying the update form and processing the submitted data.
    If the update is successful, the user is redirected to the products
    list page.

    :ivar model: The model that this view will operate on.
    :type model: type
    :ivar form_class: The form class used for product update.
    :type form_class: type
    :ivar success_url: The URL where the user will be redirected to upon
        successful product update.
    :type success_url: str
    """
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy("products:products")


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    """
    Handles the logic for deleting a product.

    This class-based view ensures that only authenticated users can delete
    products. It provides a confirmation page for deletion and redirects to the
    specified success URL upon successful deletion. The `model` attribute
    specifies which model is being deleted, while the `success_url` defines the
    URL to redirect to after deletion.

    :ivar model: The specific model this view interacts with.
    :type model: type[Model]
    :ivar success_url: The URL to redirect to after successful deletion.
    :type success_url: str
    """
    model = Product
    success_url = reverse_lazy("products:products")


class ProductDetailView(LoginRequiredMixin, DetailView):
    """
    Handles the display of detailed information about a specific product.

    This class provides the necessary functionality to render a detailed view
    of a single product. It is designed to be used in conjunction with a login
    requirement, ensuring that only authenticated users have access. The view
    pulls in associated order information, providing insights into the product's
    sales and history.

    :ivar model: The model class associated with this view.
    :type model: Product
    :ivar template_name: The template used to render the product detail view.
    :type template_name: str
    :ivar context_object_name: The context variable name representing the
        product in the template.
    :type context_object_name: str
    """
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order_items = (
            self.object.order_items
            .select_related("order", "order__client")
            .only(
                "quantity",
                "unit_price",
                "subtotal",
                "created_at",
                "order__id",
                "order__status",
                "order__created_at",
                "order__client"
            )
            .order_by("-order__created_at")
        )

        context["order_items"] = order_items
        context["orders_count"] = order_items.count()
        context["total_sold"] = sum(item.quantity for item in order_items)

        context["categories"] = ProductCategory.objects.all()

        return context