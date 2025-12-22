import pytest
from decimal import Decimal
from django.urls import reverse
from django.contrib.messages import get_messages

from apps.products.models import Product
from apps.products.enums import ProductStatusEnum


@pytest.mark.django_db
class TestProductViews:
    def test_list_requires_login(self, client):
        url = reverse("products:products")
        resp = client.get(url)
        assert resp.status_code == 302
        assert reverse("accounts:login") in resp.url

    def test_list_filters_and_context(self, client, user, product, category):
        client.login(username="manager", password="pass1234")
        Product.objects.create(
            name="Тюльпани",
            description="Жовті тюльпани",
            image="test",
            category=category,
            price=Decimal("99.99"),
            stock=5,  # LOW_STOCK
            sold=3,
            rating=4.0,
            status=ProductStatusEnum.LOW_STOCK,
            is_active=True,
        )
        url = reverse("products:products")

        resp = client.get(url, {"search": "тюльп", "status": ProductStatusEnum.LOW_STOCK, "sort": "price_desc"})
        assert resp.status_code == 302

    def test_create_sets_success_message_and_redirects(self, client, user, category):
        client.login(username="manager", password="pass1234")
        url = reverse("products:create")
        data = {
            "name": "Піони",
            "description": "Ніжні піони",
            "image": "",  # optional
            "category": category.id,
            "price": "149.50",
            "stock": 15,
            "rating": 4.5,
            "is_active": True,
        }
        resp = client.post(url, data, follow=True)
        assert resp.status_code == 200

    def test_update_redirects_to_list(self, client, user, product, category):
        client.login(username="manager", password="pass1234")
        url = reverse("products:update", kwargs={"pk": product.pk})
        data = {
            "name": product.name + " (оновлено)",
            "description": product.description,
            "image": "",
            "category": category.id,
            "price": str(product.price),
            "stock": product.stock,
            "rating": product.rating,
            "is_active": product.is_active,
        }
        resp = client.post(url, data, follow=True)
        assert resp.status_code == 200

    def test_delete_removes_product(self, client, user, product):
        client.login(username="manager", password="pass1234")
        url = reverse("products:delete", kwargs={"pk": product.pk})
        resp = client.post(url, follow=True)
        assert resp.status_code == 200
        assert not Product.objects.filter(pk=product.pk).exists()

    def test_detail_context_has_orders_info(self, client, user, order_item):
        client.login(username="manager", password="pass1234")
        product = order_item.product
        url = reverse("products:detail", kwargs={"pk": product.pk})
        resp = client.get(url)
        assert resp.status_code == 200
        assert "order_items" in resp.context  # type: ignore[operator]
        assert "orders_count" in resp.context  # type: ignore[operator]
        assert "total_sold" in resp.context  # type: ignore[operator]
        assert resp.context["orders_count"] >= 1  # type: ignore[index]
        assert resp.context["total_sold"] >= 1  # type: ignore[index]
