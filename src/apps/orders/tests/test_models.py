import pytest
from django.core.exceptions import ValidationError

from apps.orders.enums import OrderStatusEnum
from apps.orders.models import OrderStatusHistory


@pytest.mark.django_db
class TestOrderModel:
    def test_calculate_and_update_total(self, order, order_item):
        assert order.calculate_total() == order_item.subtotal
        order.update_total()
        order.refresh_from_db()
        assert order.total_price == order_item.subtotal

    def test_order_item_uses_product_price_and_sets_subtotal(self, product, order):
        from apps.orders.models import OrderItem

        item = OrderItem.objects.create(order=order, product=product, quantity=3)
        assert item.unit_price == product.price
        assert item.subtotal == product.price * 3

    def test_order_item_clean_prevents_oversell(self, product, order):
        from apps.orders.models import OrderItem

        product.stock = 1
        product.save(update_fields=["stock"])

        with pytest.raises(ValidationError) as exc:
            OrderItem(order=order, product=product, quantity=2).clean()
        assert "Недостатньо товару" in str(exc.value)

    def test_status_transition_success_and_history_created(self, user, order):
        assert order.status == OrderStatusEnum.NEW
        order.transition_to(OrderStatusEnum.PROCESSING, user=user, notes="start")
        order.refresh_from_db()
        assert order.status == OrderStatusEnum.PROCESSING

        hist = OrderStatusHistory.objects.filter(order=order).latest("created_at")
        assert hist.from_status == OrderStatusEnum.NEW
        assert hist.to_status == OrderStatusEnum.PROCESSING
        assert hist.changed_by == user
        assert hist.notes == "start"

    def test_status_transition_invalid_raises(self, order):
        order.status = OrderStatusEnum.COMPLETED
        order.save(update_fields=["status"])
        with pytest.raises(ValidationError):
            order.transition_to(OrderStatusEnum.PROCESSING)

    def test_get_status_timeline_ordering(self, user, order):
        order.transition_to(OrderStatusEnum.PROCESSING, user=user)
        order.transition_to(OrderStatusEnum.DELIVERY, user=user)
        timeline = list(order.get_status_timeline())
        assert timeline[0].from_status == OrderStatusEnum.NEW
        assert timeline[-1].to_status == OrderStatusEnum.DELIVERY
