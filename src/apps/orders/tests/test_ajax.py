import json
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestOrdersAjax:
    def _auth(self, client, user):
        client.login(email=user.email, password="pass1234")

    def test_search_clients_min_length(self, client, user):
        self._auth(client, user)
        url = reverse("orders_ajax:search_clients")
        resp = client.get(url, {"phone": "12"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["clients"] == []

    def test_search_products_min_length(self, client, user):
        self._auth(client, user)
        url = reverse("orders_ajax:search_products")
        resp = client.get(url, {"q": "a"})
        assert resp.status_code == 200
        assert resp.json()["products"] == []

    def test_create_order_ajax_success_with_existing_client(self, client, user, client_obj, product):
        self._auth(client, user)
        url = reverse("orders_ajax:create_order")
        payload = {
            "client_id": client_obj.id,
            "needs_delivery": False,
            "items": [
                {"product_id": product.id, "quantity": 2}
            ],
            "notes": "test"
        }
        resp = client.post(url, data=json.dumps(payload), content_type="application/json")
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert data["order"]["id"] > 0
        assert data["order"]["total_price"] == str(product.price * 2)

    def test_create_order_ajax_validates_delivery_fields(self, client, user, client_obj, product):
        self._auth(client, user)
        url = reverse("orders_ajax:create_order")
        payload = {
            "client_id": client_obj.id,
            "needs_delivery": True,
            "items": [
                {"product_id": product.id, "quantity": 1}
            ]
        }
        resp = client.post(url, data=json.dumps(payload), content_type="application/json")
        assert resp.status_code == 400
        data = resp.json()
        assert "delivery_address" in data["errors"] or "delivery_date" in data["errors"]
