from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Sum
from django.urls import reverse

from apps.abstract_models import AbstractDatetimeModel
from apps.clients.models import Client
from apps.orders.enums import OrderStatusEnum
from apps.orders.managers import OrderManager
from apps.products.models import Product


class Order(AbstractDatetimeModel):
    """
    Represents an order made by a client, tracking details necessary for processing, delivery, and status
    management.

    This class models an order with attributes such as client information, total price, delivery requirements,
    status, and notes. It provides methods for calculating the total price, transitioning between statuses,
    updating order information, and more. It ensures validation related to delivery requirements and supports
    tracking status history over time.

    :ivar client: The client who placed the order.
    :type client: Client
    :ivar total_price: The total price of the order calculated from its items.
    :type total_price: Decimal
    :ivar needs_delivery: Indicates whether delivery is required for this order.
    :type needs_delivery: bool
    :ivar delivery_address: The delivery address if delivery is required.
    :type delivery_address: str or None
    :ivar delivery_date: The date on which the delivery is scheduled.
    :type delivery_date: datetime.date or None
    :ivar delivery_time: The time during which the delivery is scheduled.
    :type delivery_time: datetime.time or None
    :ivar status: The current status of the order from predefined choices.
    :type status: str
    :ivar notes: Additional notes or comments related to the order.
    :type notes: str or None
    """
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Клієнт"
    )
    total_price = models.DecimalField(
        verbose_name="Загальна сума",
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    needs_delivery = models.BooleanField(
        verbose_name="Потребує доставки",
        default=False,
        help_text="Чи потрібна доставка для цього замовлення"
    )
    delivery_address = models.CharField(
        verbose_name="Адреса доставки",
        max_length=255,
        blank=True,
        null=True
    )
    delivery_date = models.DateField(
        verbose_name="Дата доставки",
        blank=True,
        null=True
    )
    delivery_time = models.TimeField(
        verbose_name="Час доставки",
        null=True,
        blank=True
    )
    status = models.CharField(
        verbose_name="Статус",
        max_length=20,
        choices=OrderStatusEnum.choices,
        default=OrderStatusEnum.NEW
    )
    notes = models.TextField(
        verbose_name="Примітки",
        blank=True,
        null=True
    )

    objects = OrderManager()

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["client"]),
            models.Index(fields=["delivery_date"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["needs_delivery"]),
        ]

    def __str__(self):
        return f"Замовлення #{self.id} - {self.client.full_name}"

    def get_absolute_url(self):
        return reverse("orders:order_detail", args=[str(self.id)])

    def clean(self):
        super().clean()
        if self.needs_delivery:
            if not self.delivery_address:
                raise ValidationError({
                    "delivery_address": "Адреса доставки обов'язкова, якщо потрібна доставка"
                })
            if not self.delivery_date:
                raise ValidationError({
                    "delivery_date": "Дата доставки обов'язкова, якщо потрібна доставка"
                })

    def calculate_total(self):
        total = self.items.aggregate(
            total=Sum(F("unit_price") * F("quantity"))
        )["total"] or Decimal("0.00")
        return total

    def update_total(self):
        self.total_price = self.calculate_total()
        self.save(update_fields=["total_price", "updated_at"])

    def can_transition_to(self, new_status):
        allowed_transitions = {
            OrderStatusEnum.NEW: [OrderStatusEnum.PROCESSING, OrderStatusEnum.CANCELLED],
            OrderStatusEnum.PROCESSING: [OrderStatusEnum.DELIVERY, OrderStatusEnum.COMPLETED,
                                         OrderStatusEnum.CANCELLED],
            OrderStatusEnum.DELIVERY: [OrderStatusEnum.COMPLETED, OrderStatusEnum.CANCELLED],
            OrderStatusEnum.COMPLETED: [],
            OrderStatusEnum.CANCELLED: [],
        }
        return new_status in allowed_transitions.get(self.status, [])

    def transition_to(self, new_status, user=None, notes=None):
        if not self.can_transition_to(new_status):
            raise ValidationError(
                f"Неможливо перейти зі статусу \"{self.get_status_display()}\" "
                f"до \"{OrderStatusEnum(new_status).label}\""
            )

        old_status = self.status
        self.status = new_status
        self.save(update_fields=["status", "updated_at"])

        OrderStatusHistory.objects.create(
            order=self,
            from_status=old_status,
            to_status=new_status,
            changed_by=user,
            notes=notes
        )

        return True

    def get_status_timeline(self):
        """Отримання хронології змін статусів"""
        return self.status_history.select_related("changed_by").order_by("created_at")


class OrderItem(AbstractDatetimeModel):
    """
    Represents an item in a customer's order.

    The OrderItem class defines the relationship between a specific product and an order,
    along with the quantity, unit price, and subtotal for the product within the order. It
    also validates stock availability before saving and ensures the subtotal is calculated
    based on quantity and unit price.

    :ivar order: The order that this item is associated with.
    :type order: Order
    :ivar product: The product being ordered.
    :type product: Product
    :ivar quantity: The quantity of the product in the order.
    :type quantity: int
    :ivar unit_price: The price per unit of the product.
    :type unit_price: Decimal
    :ivar subtotal: The computed total price for the quantity of the product in the order.
    :type subtotal: Decimal
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Замовлення"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
        verbose_name="Продукт"
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Кількість",
        default=1
    )
    unit_price = models.DecimalField(
        verbose_name="Ціна за одиницю",
        max_digits=10,
        decimal_places=2
    )
    subtotal = models.DecimalField(
        verbose_name="Сума",
        max_digits=10,
        decimal_places=2,
        editable=False
    )

    class Meta:
        verbose_name = "Товар в замовленні"
        verbose_name_plural = "Товари в замовленні"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def clean(self):
        super().clean()
        if self.product and self.quantity:
            if not self.pk:
                if self.product.stock < self.quantity:
                    raise ValidationError({
                        "quantity": f"Недостатньо товару на складі. "
                                    f"Доступно: {self.product.stock} шт."
                    })

    def save(self, *args, **kwargs):
        if self.unit_price is None:
            self.unit_price = self.product.price

        self.subtotal = self.unit_price * self.quantity

        super().save(*args, **kwargs)


class OrderStatusHistory(AbstractDatetimeModel):
    """
    Represents the history of status changes for an order.

    This class tracks changes in the status of an order, providing details
    about the previous status, new status, who made the change, and any
    optional notes. It is tied to a specific order and maintains a record
    of the chronological history of status changes for that order.

    :ivar order: The order associated with the status change history.
    :type order: Order
    :ivar from_status: The previous status of the order.
    :type from_status: str
    :ivar to_status: The new status of the order.
    :type to_status: str
    :ivar changed_by: The user who made the status change.
    :type changed_by: User
    :ivar notes: Optional notes regarding the status change.
    :type notes: str
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="Замовлення"
    )
    from_status = models.CharField(
        verbose_name="Попередній статус",
        max_length=20,
        choices=OrderStatusEnum.choices
    )
    to_status = models.CharField(
        verbose_name="Новий статус",
        max_length=20,
        choices=OrderStatusEnum.choices
    )
    changed_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_status_changes",
        verbose_name="Змінив"
    )
    notes = models.TextField(
        verbose_name="Примітки",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Історія статусу"
        verbose_name_plural = "Історія статусів"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.order}: {self.from_status} → {self.to_status}"

    @property
    def duration_in_previous_status(self):
        previous = OrderStatusHistory.objects.filter(
            order=self.order,
            created_at__lt=self.created_at
        ).order_by("-created_at").first()

        if previous:
            return self.created_at - previous.created_at
        else:
            return self.created_at - self.order.created_at
