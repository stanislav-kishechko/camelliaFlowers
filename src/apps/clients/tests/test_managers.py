from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.clients.models import Client


@pytest.mark.django_db
class TestClientManager:
    """Test suite for the ClientManager."""

    @pytest.fixture
    def sample_clients(self):
        """Create a set of sample clients for testing."""
        clients = []

        clients.append(Client.objects.create(
            first_name="Іван",
            last_name="Петренко",
            phone="+380501234567",
            email="ivan@example.com",
            city="Київ",
            is_active=True,
            is_vip=False,
            orders_count=5,
            total_spent=Decimal("1000.00")
        ))

        clients.append(Client.objects.create(
            first_name="Марія",
            last_name="Коваленко",
            phone="+380671234567",
            email="maria@example.com",
            city="Львів",
            is_active=True,
            is_vip=True,
            orders_count=10,
            total_spent=Decimal("5000.00")
        ))

        clients.append(Client.objects.create(
            first_name="Петро",
            last_name="Сидоренко",
            phone="+380931234567",
            email="petro@example.com",
            city="Київ",
            is_active=False,
            is_vip=False,
            orders_count=2,
            total_spent=Decimal("300.00")
        ))

        clients.append(Client.objects.create(
            first_name="Олена",
            last_name="Ткаченко",
            phone="+380971234567",
            city="Одеса",
            is_active=True,
            is_vip=False,
            orders_count=0,
            total_spent=Decimal("0.00")
        ))

        clients.append(Client.objects.create(
            first_name="Андрій",
            last_name="Бондаренко",
            phone="+380961234567",
            city="Харків",
            is_active=True,
            is_vip=False,
            orders_count=3,
            total_spent=Decimal("750.00")
        ))

        return clients

    def test_search_by_first_name(self, sample_clients):
        """Test searching clients by first name."""
        results = Client.objects.search("Іван")
        assert results.count() == 1
        assert results.first().first_name == "Іван"

    def test_search_by_last_name(self, sample_clients):
        """Test searching clients by last name."""
        results = Client.objects.search("Коваленко")
        assert results.count() == 1
        assert results.first().last_name == "Коваленко"

    def test_search_by_phone(self, sample_clients):
        """Test searching clients by phone number."""
        results = Client.objects.search("380501234567")
        assert results.count() == 1
        assert "+380501234567" in results.first().phone

    def test_search_by_email(self, sample_clients):
        """Test searching clients by email."""
        results = Client.objects.search("maria@example.com")
        assert results.count() == 1
        assert results.first().email == "maria@example.com"

    def test_search_empty_query(self, sample_clients):
        """Test that empty search returns all clients."""
        results = Client.objects.search("")
        assert results.count() == 5

    def test_search_no_results(self, sample_clients):
        """Test search with no matching results."""
        results = Client.objects.search("NonExistent")
        assert results.count() == 0

    def test_by_type_active(self, sample_clients):
        """Test filtering by active client type."""
        results = Client.objects.by_type("active")
        assert results.count() == 4
        assert all(client.is_active for client in results)

    def test_by_type_vip(self, sample_clients):
        """Test filtering by VIP client type."""
        results = Client.objects.by_type("vip")
        assert results.count() == 1
        assert results.first().is_vip is True

    def test_by_type_inactive(self, sample_clients):
        """Test filtering by inactive client type."""
        results = Client.objects.by_type("inactive")
        assert results.count() == 1
        assert results.first().is_active is False

    def test_by_type_new(self, sample_clients):
        """Test filtering by new client type (created in last 30 days)."""
        results = Client.objects.by_type("new")
        # All sample clients are just created, so all should be "new"
        assert results.count() == 5

    def test_by_type_invalid(self, sample_clients):
        """Test that invalid type returns all clients."""
        results = Client.objects.by_type("invalid_type")
        assert results.count() == 5

    def test_sort_by_name(self, sample_clients):
        """Test sorting clients by name."""
        results = list(Client.objects.sort_by("name"))
        assert results[0].first_name == "Іван"
        assert results[-1].first_name == "Петро"

    def test_sort_by_orders(self, sample_clients):
        """Test sorting clients by orders count."""
        results = list(Client.objects.sort_by("orders"))
        assert results[0].orders_count == 10  # VIP with most orders
        assert results[-1].orders_count == 0  # Client without orders

    def test_sort_by_spent(self, sample_clients):
        """Test sorting clients by total spent."""
        results = list(Client.objects.sort_by("spent"))
        assert results[0].total_spent == Decimal("5000.00")
        assert results[-1].total_spent == Decimal("0.00")

    def test_sort_by_date(self, sample_clients):
        """Test sorting clients by creation date."""
        results = list(Client.objects.sort_by("date"))
        # Should be ordered by most recent first
        assert results[0].created_at >= results[-1].created_at

    def test_sort_by_invalid(self, sample_clients):
        """Test that invalid sort option defaults to date."""
        results = list(Client.objects.sort_by("invalid"))
        # Should default to date ordering
        assert results[0].created_at >= results[-1].created_at

    def test_active_filter(self, sample_clients):
        """Test active() method returns only active clients."""
        results = Client.objects.active()
        assert results.count() == 4
        assert all(client.is_active for client in results)

    def test_vip_filter(self, sample_clients):
        """Test vip() method returns only VIP clients."""
        results = Client.objects.vip()
        assert results.count() == 1
        assert all(client.is_vip for client in results)

    def test_regular_filter(self, sample_clients):
        """Test regular() method returns non-VIP clients."""
        results = Client.objects.regular()
        assert results.count() == 4
        assert all(not client.is_vip for client in results)

    def test_with_orders(self, sample_clients):
        """Test with_orders() returns clients with at least one order."""
        results = Client.objects.with_orders()
        assert results.count() == 4
        assert all(client.orders_count > 0 for client in results)

    def test_without_orders(self, sample_clients):
        """Test without_orders() returns clients with zero orders."""
        results = Client.objects.without_orders()
        assert results.count() == 1
        assert results.first().orders_count == 0

    def test_top_buyers_default_limit(self, sample_clients):
        """Test top_buyers() with default limit."""
        results = list(Client.objects.top_buyers())
        # Should return clients ordered by total_spent descending
        assert len(results) <= 10
        assert results[0].total_spent >= results[-1].total_spent

    def test_top_buyers_custom_limit(self, sample_clients):
        """Test top_buyers() with custom limit."""
        results = list(Client.objects.top_buyers(limit=2))
        assert len(results) == 2
        assert results[0].total_spent == Decimal("5000.00")
        assert results[1].total_spent == Decimal("1000.00")

    def test_top_buyers_excludes_zero_spent(self, sample_clients):
        """Test that top_buyers excludes clients with zero spending."""
        results = Client.objects.top_buyers()
        assert all(client.total_spent > 0 for client in results)

    def test_recent_default_days(self, sample_clients):
        """Test recent() with default 30 days."""
        results = Client.objects.recent()
        # All sample clients are just created
        assert results.count() == 5

    def test_recent_custom_days(self, sample_clients):
        """Test recent() with custom number of days."""
        results = Client.objects.recent(days=7)
        assert results.count() == 5

    def test_recent_old_clients(self):
        """Test that old clients are not included in recent()."""
        # Create a client with old creation date
        old_date = timezone.now() - timedelta(days=60)
        old_client = Client.objects.create(
            first_name="Старий",
            last_name="Клієнт",
            phone="+380991111111"
        )
        old_client.created_at = old_date
        old_client.save()

        results = Client.objects.recent(days=30)
        assert old_client not in results

    def test_by_spending_range_min_only(self, sample_clients):
        """Test filtering by minimum spending amount only."""
        results = Client.objects.by_spending_range(min_amount=1000)
        assert results.count() == 2
        assert all(client.total_spent >= Decimal("1000.00") for client in results)

    def test_by_spending_range_max_only(self, sample_clients):
        """Test filtering by maximum spending amount only."""
        results = Client.objects.by_spending_range(max_amount=500)
        assert results.count() == 2
        assert all(client.total_spent <= Decimal("500.00") for client in results)

    def test_by_spending_range_both(self, sample_clients):
        """Test filtering by both min and max spending amounts."""
        results = Client.objects.by_spending_range(min_amount=300, max_amount=1000)
        assert results.count() == 3
        assert all(
            Decimal("300.00") <= client.total_spent <= Decimal("1000.00")
            for client in results
        )

    def test_by_spending_range_no_limits(self, sample_clients):
        """Test that no limits returns all clients."""
        results = Client.objects.by_spending_range()
        assert results.count() == 5

    def test_with_email(self, sample_clients):
        """Test with_email() returns only clients with email."""
        results = Client.objects.with_email()
        assert results.count() == 3
        assert all(client.email for client in results)

    def test_get_statistics(self, sample_clients):
        """Test get_statistics() returns correct metrics."""
        stats = Client.objects.get_statistics()

        assert stats["total_clients"] == 5
        assert stats["active_clients"] == 4
        assert stats["vip_clients"] == 1
        assert stats["new_clients_month"] == 5
        assert stats["total_revenue"] == Decimal("7050.00")
        assert stats["average_order"] == Decimal("1410.00")

    def test_get_statistics_empty_database(self):
        """Test get_statistics() with no clients."""
        stats = Client.objects.get_statistics()

        assert stats["total_clients"] == 0
        assert stats["active_clients"] == 0
        assert stats["vip_clients"] == 0
        assert stats["new_clients_month"] == 0
        assert stats["average_order"] == 0
        assert stats["total_revenue"] == 0

    def test_chaining_methods(self, sample_clients):
        """Test chaining multiple manager methods."""
        results = Client.objects.active().vip().with_orders()
        assert results.count() == 1
        assert results.first().is_active is True
        assert results.first().is_vip is True
        assert results.first().orders_count > 0
