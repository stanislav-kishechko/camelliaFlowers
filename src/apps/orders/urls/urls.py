from django.urls import path

from apps.orders.views import views

app_name = "orders"

urlpatterns = [
    path("", views.OrderListView.as_view(), name="orders"),
    path("<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("<int:pk>/delete/", views.OrderDeleteView.as_view(), name="order_delete"),
]
