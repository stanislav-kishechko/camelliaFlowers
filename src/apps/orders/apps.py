from django.apps import AppConfig


class OrdersConfig(AppConfig):
    name = 'apps.orders'

    def ready(self):
        from apps.orders import signals
