"""
URL patterns для AJAX API замовлень
Оновлена версія з додатковим маршрутом для update
"""

from django.urls import path

from apps.orders.views import ajax_views

app_name = 'orders_ajax'

urlpatterns = [
    path('clients/search/', ajax_views.search_clients, name='search_clients'),
    path('products/search/', ajax_views.search_products, name='search_products'),
    path('create/', ajax_views.create_order_ajax, name='create_order'),
    path('calculate-price/', ajax_views.calculate_order_price, name='calculate_price'),

    path('<int:order_id>/update/', ajax_views.update_order_ajax, name='update_order'),
    path('<int:order_id>/status/', ajax_views.update_order_status, name='update_status'),

    path('<int:order_id>/items/add/', ajax_views.add_order_item, name='add_item'),
    path('<int:order_id>/items/<int:item_id>/update/', ajax_views.update_order_item,
         name='update_item'),
    path('<int:order_id>/details/', ajax_views.get_order_details, name='order_details'),
    path(
        '<int:order_id>/items/<int:item_id>/',
         ajax_views.delete_order_item,
         name='delete_item'
    ),
]
