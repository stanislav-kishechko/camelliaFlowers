"""Тести для класичних Views додатку orders."""
import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from apps.orders.enums import OrderStatusEnum


@pytest.mark.django_db
class TestOrderViews:
    def test_orders_list_requires_login(self, client):
        url = reverse("orders:orders")
        resp = client.get(url)
        assert resp.status_code == 302
        assert "/accounts/login" in resp.url

    def test_orders_list_authenticated_ok_and_context(self, client, user, order):
        client.login(email=user.email, password="pass1234")
        url = reverse("orders:orders")
        resp = client.get(url)
        assert resp.status_code == 200

        ctx = resp.context
        for key in [
            "new_orders",
            "processing_orders",
            "delivery_orders",
            "completed_orders",
            "cancelled_orders",
            "statistics",
            "delivery_today",
            "delivery_tomorrow",
            "overdue_orders",
        ]:
            assert key in ctx

    def test_order_detail_context_available_statuses(self, client, user, order):
        client.login(email=user.email, password="pass1234")
        url = reverse("orders:order_detail", args=[order.pk])
        resp = client.get(url)
        assert resp.status_code == 200
        available_statuses = resp.context["available_statuses"]
        target_values = {s for s, _ in available_statuses}
        assert OrderStatusEnum.PROCESSING in target_values
        assert OrderStatusEnum.CANCELLED in target_values

    def test_order_delete_view_removes_and_sets_message(self, client, user, order):
        client.login(email=user.email, password="pass1234")
        url = reverse("orders:order_delete", args=[order.pk])
        resp = client.post(url, follow=True)
        assert resp.status_code == 200

        from apps.orders.models import Order

        assert not Order.objects.filter(pk=order.pk).exists()

        messages = list(get_messages(resp.wsgi_request))
        assert any("успішно видалено" in m.message for m in messages)
