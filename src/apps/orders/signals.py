from decimal import Decimal

from django.db.models import F, Sum
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from apps.clients.models import Client
from apps.orders.enums import OrderStatusEnum
from apps.orders.models import Order, OrderItem
from apps.products.models import Product


@receiver(post_save, sender=Order)
def update_client_on_order_save(sender, instance, created, **kwargs):
    """
    Signal receiver function to handle the `post_save` signal for the `Order` model.

    This function updates the client's statistics, including the total number of
    orders (excluding canceled ones) and the total amount spent (for completed orders only),
    whenever an `Order` instance is saved. The updates are applied directly to the `Client`
    model without triggering signals.

    :param sender: The model class that sent the signal.
    :type sender: Type[Model]
    :param instance: The instance of the `Order` model that was saved.
    :type instance: Order
    :param created: A boolean indicating whether a new instance was created.
    :type created: bool
    :param kwargs: Additional keyword arguments provided by the signal.
    :type kwargs: dict
    :return: None
    """
    client = instance.client

    orders_count = client.orders.exclude(
        status=OrderStatusEnum.CANCELLED
    ).count()

    total_spent = client.orders.filter(
        status=OrderStatusEnum.COMPLETED
    ).aggregate(
        total=Sum("total_price")
    )["total"] or Decimal("0.00")

    Client.objects.filter(pk=client.pk).update(
        orders_count=orders_count,
        total_spent=total_spent
    )


@receiver(post_delete, sender=Order)
def update_client_on_order_delete(sender, instance, **kwargs):
    """
    Signal receiver to update the client's information when an associated order is deleted.

    This function listens for the ``post_delete`` signal sent by the ``Order`` model.
    After an order is removed, it recalculates and updates the client's total number of
    orders (excluding canceled orders) and total spending (based on completed orders).

    :param sender: Model class that sent the signal. Should always be ``Order`` in this context.
    :type sender: Type[Model]
    :param instance: Instance of the model sent by the signal. Represents the deleted order.
    :type instance: Order
    :param kwargs: Additional arguments passed to the signal function.
    :type kwargs: dict
    :return: None
    """
    client = instance.client

    orders_count = client.orders.exclude(
        status=OrderStatusEnum.CANCELLED
    ).count()

    total_spent = client.orders.filter(
        status=OrderStatusEnum.COMPLETED
    ).aggregate(
        total=Sum("total_price")
    )["total"] or Decimal("0.00")

    Client.objects.filter(pk=client.pk).update(
        orders_count=orders_count,
        total_spent=total_spent
    )


@receiver(pre_save, sender=Order)
def track_order_status_change(sender, instance, **kwargs):
    """
    Tracks changes in the order status before saving an Order instance. This function identifies
    if the status of an order is being updated by comparing the current status of the instance
    with the stored status in the database. It also sets an attribute on the instance to keep
    track of the old status for further processing.

    :param sender: The model class that sends the signal. In this case, it is the Order model.
    :type sender: Any
    :param instance: The Order instance that is being saved.
    :type instance: Order
    :param kwargs: Additional arguments passed to the signal.
    :type kwargs: dict
    :return: None
    """
    if instance.pk:
        try:
            old_order = Order.objects.get(pk=instance.pk)
            instance._old_status = old_order.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def update_product_stock_on_status_change(sender, instance, created, **kwargs):
    """
    Handles the stock and sold quantities of products in response to changes
    in the status of an order. This function is triggered when an `Order`
    object is saved, and it adjusts the product stock based on the following
    conditions:

    - When a new order is created: Items in the order are deducted from the stock
      and added to the sold count.
    - When an order is cancelled: Items in the order are returned to stock and
      removed from the sold count.
    - When an order is reinstated from the cancelled state: Items in the order
      are deducted from the stock and added back to the sold count.

    The function ensures the consistency of product inventory in response to
    these status changes.

    :param sender: The model class that triggered the signal (expected to be `Order`).
    :type sender: Type[Model]
    :param instance: The instance of the `Order` model being saved.
    :type instance: Order
    :param created: A boolean indicating if the instance is being created (True)
        or updated (False).
    :type created: bool
    :param kwargs: Additional keyword arguments passed by the signal.
    :type kwargs: dict
    :return: None
    """
    old_status = getattr(instance, '_old_status', None)

    if created:
        for item in instance.items.all():
            Product.objects.filter(pk=item.product_id).update(
                stock=F("stock") - item.quantity,
                sold=F("sold") + item.quantity
            )

    elif old_status and old_status != instance.status:
        if instance.status == OrderStatusEnum.CANCELLED and old_status != OrderStatusEnum.CANCELLED:
            for item in instance.items.all():
                Product.objects.filter(pk=item.product_id).update(
                    stock=F("stock") + item.quantity,
                    sold=F("sold") - item.quantity
                )

        elif (
            old_status == OrderStatusEnum.CANCELLED and instance.status != OrderStatusEnum.CANCELLED
        ):
            for item in instance.items.all():
                Product.objects.filter(pk=item.product_id).update(
                    stock=F("stock") - item.quantity,
                    sold=F("sold") + item.quantity
                )


@receiver(pre_save, sender=OrderItem)
def track_order_item_quantity_change(sender, instance, **kwargs):
    """
    Відстеження змін кількості товару перед збереженням
    """
    if instance.pk:
        try:
            old_item = OrderItem.objects.get(pk=instance.pk)
            instance._old_quantity = old_item.quantity
            instance._old_product_id = old_item.product_id
        except OrderItem.DoesNotExist:
            instance._old_quantity = 0
            instance._old_product_id = None
    else:
        instance._old_quantity = 0
        instance._old_product_id = None


@receiver(post_save, sender=OrderItem)
def update_order_and_product_on_item_save(sender, instance, created, **kwargs):
    """
    Signal handler for `post_save` of `OrderItem` model. This function updates the stock
    and sold quantities of the associated `Product` based on the changes in the
    `OrderItem` instance. Additionally, it recalculates and updates the total price
    of the related `Order` instance.

    :param sender: The model class that triggered the signal.
    :type sender: type
    :param instance: The instance of `OrderItem` that triggered the signal.
    :type instance: OrderItem
    :param created: A boolean indicating whether a new instance was created.
    :type created: bool
    :param kwargs: Additional arguments passed by the signal.
    :type kwargs: dict
    :return: None
    """
    order = instance.order

    if order.status != OrderStatusEnum.CANCELLED:
        if created:
            Product.objects.filter(pk=instance.product_id).update(
                stock=F("stock") - instance.quantity,
                sold=F("sold") + instance.quantity
            )
        else:
            old_quantity = getattr(instance, "_old_quantity", 0)
            old_product_id = getattr(instance, "_old_product_id", None)
            quantity_diff = instance.quantity - old_quantity

            if old_product_id and old_product_id != instance.product_id:
                Product.objects.filter(pk=old_product_id).update(
                    stock=F("stock") + old_quantity,
                    sold=F("sold") - old_quantity
                )
                Product.objects.filter(pk=instance.product_id).update(
                    stock=F("stock") - instance.quantity,
                    sold=F("sold") + instance.quantity
                )
            elif quantity_diff != 0:
                Product.objects.filter(pk=instance.product_id).update(
                    stock=F("stock") - quantity_diff,
                    sold=F("sold") + quantity_diff
                )

    new_total = order.calculate_total()
    Order.objects.filter(pk=order.pk).update(
        total_price=new_total
    )
    order.total_price = new_total


@receiver(post_delete, sender=OrderItem)
def update_order_and_product_on_item_delete(sender, instance, **kwargs):
    """
    Signal handler to update the order and product details when an order item is deleted.

    This function ensures that when an order item is deleted, the related product's stock
    and sold quantities are adjusted accordingly. Additionally, if the parent order is not
    cancelled, the order's total price is recalculated and updated.

    :param sender: The model class that sent the signal.
    :param instance: The instance of the model being deleted.
    :type instance: OrderItem
    :param kwargs: Additional keyword arguments passed by the signal.
    :return: None
    """
    order = instance.order

    if order.status != OrderStatusEnum.CANCELLED:
        Product.objects.filter(pk=instance.product_id).update(
            stock=F("stock") + instance.quantity,
            sold=F("sold") - instance.quantity
        )

    new_total = order.calculate_total()
    Order.objects.filter(pk=order.pk).update(
        total_price=new_total
    )
