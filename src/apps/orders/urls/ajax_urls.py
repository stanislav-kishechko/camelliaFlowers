from django.urls import path

from apps.orders.views import ajax_views

app_name = 'orders_ajax'

urlpatterns = [
    path('clients/search/', ajax_views.SearchClientsView.as_view(), name='search_clients'),
    path('products/search/', ajax_views.SearchProductsView.as_view(), name='search_products'),

    path('create/', ajax_views.CreateOrderAjaxView.as_view(), name='create_order'),
    path('calculate-price/', ajax_views.CalculateOrderPriceView.as_view(), name='calculate_price'),

    path('<int:order_id>/update/', ajax_views.UpdateOrderAjaxView.as_view(), name='update_order'),
    path('<int:order_id>/status/', ajax_views.UpdateOrderStatusView.as_view(), name='update_status'),

    path('<int:order_id>/items/add/', ajax_views.AddOrderItemView.as_view(), name='add_item'),
    path('<int:order_id>/items/<int:item_id>/update/', ajax_views.UpdateOrderItemView.as_view(),
         name='update_item'),
    path('<int:order_id>/items/<int:item_id>/', ajax_views.DeleteOrderItemView.as_view(),
         name='delete_item'),

    path('<int:order_id>/details/', ajax_views.OrderDetailView.as_view(), name='order_details'),
]
