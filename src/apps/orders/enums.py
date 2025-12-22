from django.db import models


class OrderStatusEnum(models.TextChoices):
    """
    Represents an enumeration of order statuses for a system.

    The enumeration provides a list of possible statuses an order can take
    within the workflow of the system. Each status is paired with a display
    name in a specific language for user representation.

    :ivar NEW: Represents a newly created order.
    :type NEW: str
    :ivar PROCESSING: Represents an order that is currently being processed.
    :type PROCESSING: str
    :ivar DELIVERY: Represents an order that is in delivery.
    :type DELIVERY: str
    :ivar COMPLETED: Represents an order that has been successfully completed.
    :type COMPLETED: str
    :ivar CANCELLED: Represents an order that has been cancelled.
    :type CANCELLED: str
    """
    NEW = 'new', 'Нове'
    PROCESSING = 'processing', 'В обробці'
    DELIVERY = 'delivery', 'Доставка'
    COMPLETED = 'completed', 'Завершено'
    CANCELLED = 'cancelled', 'Скасовано'
