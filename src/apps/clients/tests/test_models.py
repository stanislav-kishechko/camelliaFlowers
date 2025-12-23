from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.urls import reverse

from apps.clients.models import Client


@pytest.mark.django_db
class TestClientModel:
    """Test suite for the Client model."""

    def test_create_client_with_required_fields(self):
        """Test creating a client with only required fields."""
        client = Client.objects.create(
            first_name="Іван",
            last_name="Петренко",
            phone="+380501234567"
        )

        assert client.first_name == "Іван"
        assert client.last_name == "Петренко"
        assert client.phone == "+380501234567"
        assert client.is_active is True
        assert client.is_vip is False
        assert client.orders_count == 0
        assert client.total_spent == Decimal("0")

    def test_create_client_with_all_fields(self):
        """Test creating a client with all fields populated."""
        client = Client.objects.create(
            first_name="Марія",
            last_name="Коваленко",
            phone="+380671234567",
            email="maria@example.com",
            address="вул. Хрещатик, 1",
            city="Київ",
            notes="Постійний клієнт",
            is_vip=True,
            orders_count=5,
            total_spent=Decimal("1500.00")
        )

        assert client.email == "maria@example.com"
        assert client.address == "вул. Хрещатик, 1"
        assert client.city == "Київ"
        assert client.notes == "Постійний клієнт"
        assert client.is_vip is True
        assert client.orders_count == 5
        assert client.total_spent == Decimal("1500.00")

    def test_phone_uniqueness(self):
        """Test that phone number must be unique."""
        Client.objects.create(
            first_name="Олександр",
            last_name="Іванов",
            phone="+380931234567"
        )

        with pytest.raises(IntegrityError):
            Client.objects.create(
                first_name="Петро",
                last_name="Сидоренко",
                phone="+380931234567"
            )

    def test_full_name_property(self):
        """Test the full_name property returns correct format."""
        client = Client.objects.create(
            first_name="Наталія",
            last_name="Шевченко",
            phone="+380951234567"
        )

        assert client.full_name == "Наталія Шевченко"

    def test_initials_property(self):
        """Test the initials property returns first letters."""
        client = Client.objects.create(
            first_name="Андрій",
            last_name="Бондаренко",
            phone="+380961234567"
        )

        assert client.initials == "АБ"

    def test_str_method(self):
        """Test string representation of the client."""
        client = Client.objects.create(
            first_name="Олена",
            last_name="Ткаченко",
            phone="+380971234567"
        )

        assert str(client) == "Олена Ткаченко"

    def test_get_absolute_url(self):
        """Test get_absolute_url returns correct URL."""
        client = Client.objects.create(
            first_name="Дмитро",
            last_name="Мельник",
            phone="+380981234567"
        )

        expected_url = reverse("clients:client_detail", args=[str(client.id)])
        assert client.get_absolute_url() == expected_url

    def test_make_vip(self):
        """Test make_vip method sets is_vip to True."""
        client = Client.objects.create(
            first_name="Юлія",
            last_name="Коваль",
            phone="+380991234567",
            is_vip=False
        )

        assert client.is_vip is False
        client.make_vip()
        client.refresh_from_db()
        assert client.is_vip is True

    def test_remove_vip(self):
        """Test remove_vip method sets is_vip to False."""
        client = Client.objects.create(
            first_name="Сергій",
            last_name="Бойко",
            phone="+380631234567",
            is_vip=True
        )

        assert client.is_vip is True
        client.remove_vip()
        client.refresh_from_db()
        assert client.is_vip is False

    def test_deactivate(self):
        """Test deactivate method sets is_active to False."""
        client = Client.objects.create(
            first_name="Вікторія",
            last_name="Павленко",
            phone="+380641234567",
            is_active=True
        )

        assert client.is_active is True
        client.deactivate()
        client.refresh_from_db()
        assert client.is_active is False

    def test_activate(self):
        """Test activate method sets is_active to True."""
        client = Client.objects.create(
            first_name="Максим",
            last_name="Савченко",
            phone="+380651234567",
            is_active=False
        )

        assert client.is_active is False
        client.activate()
        client.refresh_from_db()
        assert client.is_active is True

    def test_client_ordering(self):
        """Test that clients are ordered by created_at descending."""
        client1 = Client.objects.create(
            first_name="First",
            last_name="Client",
            phone="+380501111111"
        )
        client2 = Client.objects.create(
            first_name="Second",
            last_name="Client",
            phone="+380502222222"
        )

        clients = list(Client.objects.all())
        assert clients[0] == client2
        assert clients[1] == client1

    def test_email_can_be_null(self):
        """Test that email field can be null."""
        client = Client.objects.create(
            first_name="Тест",
            last_name="Клієнт",
            phone="+380503333333",
            email=None
        )

        assert client.email is None

    def test_optional_fields_can_be_blank(self):
        """Test that optional fields can be blank."""
        client = Client.objects.create(
            first_name="Тест",
            last_name="Клієнт",
            phone="+380504444444",
            address="",
            city="",
            notes=""
        )

        assert client.address == ""
        assert client.city == ""
        assert client.notes == ""

    def test_meta_verbose_names(self):
        """Test model meta verbose names."""
        assert Client._meta.verbose_name == "Клієнт"
        assert Client._meta.verbose_name_plural == "Клієнти"
