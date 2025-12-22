import pytest
from django.contrib.auth import get_user_model
from decimal import Decimal

from apps.clients.models import Client
from apps.products.models import Product, ProductCategory
from apps.products.enums import ProductStatusEnum
from apps.orders.models import Order, OrderItem


@pytest.fixture
def user(db):
    User = get_user_model()
    user = User.objects.create_user(
        username="manager",
        email="manager@example.com",
        password="pass1234",
        first_name="Test",
        last_name="User",
    )
    return user


@pytest.fixture
def client_obj(db):
    return Client.objects.create(
        first_name="Іван",
        last_name="Іванов",
        phone="+380671112233",
        email="ivan@example.com",
        address="Київ, Хрещатик 1",
        city="Київ",
    )


@pytest.fixture
def category(db):
    return ProductCategory.objects.create(name="Квіти")


@pytest.fixture
def product(db, category):
    return Product.objects.create(
        name="Троянди",
        description="Букет червоних троянд",
        image="test",
        category=category,
        price=Decimal("199.99"),
        stock=10,
        sold=0,
        rating=0.0,
        status=ProductStatusEnum.AVAILABLE,
        is_active=True,
    )


@pytest.fixture
def order(db, client_obj):
    return Order.objects.create(client=client_obj, needs_delivery=False)


@pytest.fixture
def order_item(db, order, product):
    return OrderItem.objects.create(
        order=order,
        product=product,
        quantity=2,
        unit_price=product.price,
    )
