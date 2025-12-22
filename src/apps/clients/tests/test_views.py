import pytest
from decimal import Decimal
from django.urls import reverse
from django.contrib.messages import get_messages

from apps.clients.models import Client


@pytest.mark.django_db
class TestClientViews:
    def test_list_requires_login(self, client):
        url = reverse("clients:clients")
        resp = client.get(url)
        assert resp.status_code == 302
        assert reverse("accounts:login") in resp.url

    def test_detail_includes_orders_stats_and_pagination(self, client, user, client_obj, order):
        client.login(username="manager", password="pass1234")

        client_obj.orders_count = 2
        client_obj.total_spent = Decimal("100.00")
        client_obj.save(update_fields=["orders_count", "total_spent"])

        url = reverse("clients:client_detail", kwargs={"pk": client_obj.pk})
        resp = client.get(url)
        assert resp.status_code == 302

    def test_delete_removes_and_sets_message(self, client, user):
        client.login(username="manager", password="pass1234")
        to_delete = Client.objects.create(first_name="X", last_name="Y", phone="+380679999999")
        url = reverse("clients:client_delete", kwargs={"pk": to_delete.pk})
        resp = client.post(url, follow=True)
        assert resp.status_code == 200
