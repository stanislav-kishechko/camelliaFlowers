import pytest
from django.contrib.auth import get_user_model

from apps.clients.models import Client
from apps.products.models import Product, ProductCategory
from apps.orders.models import Order, OrderItem


@pytest.fixture
def user(db):
    User = get_user_model()
    u = User.objects.create_user(
        username="tester",
        email="tester@example.com",
        password="pass1234",
        first_name="Test",
        last_name="User",
    )
    return u


@pytest.fixture
def client_obj(db):
    return Client.objects.create(
        first_name="Іван",
        last_name="Іванов",
        phone="+380501112233",
        email="ivan@example.com",
        address="вул. Тестова, 1",
        city="Київ",
    )


@pytest.fixture
def product_category(db):
    return ProductCategory.objects.create(name="Квіти")


@pytest.fixture
def product(db, product_category):
    return Product.objects.create(
        name="Троянда",
        description="Червона троянда",
        category=product_category,
        price=100,
        stock=10,
        rating=4.5,
        is_active=True,
    )


@pytest.fixture
def order(db, client_obj):
    return Order.objects.create(client=client_obj)


@pytest.fixture
def order_item(db, order, product):
    return OrderItem.objects.create(order=order, product=product, quantity=2, unit_price=product.price)
