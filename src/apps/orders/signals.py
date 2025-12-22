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
    if created:
        Client.objects.filter(pk=instance.client_id).update(
            orders_count=F("orders_count") + 1,
            total_spent=F("total_spent") + instance.total_price
        )
    else:
        client = instance.client
        total = client.orders.filter(
            status__in=[OrderStatusEnum.COMPLETED]
        ).aggregate(
            total=Sum("total_price")
        )["total"] or Decimal("0.00")

        Client.objects.filter(pk=client.pk).update(
            total_spent=total
        )


@receiver(post_delete, sender=Order)
def update_client_on_order_delete(sender, instance, **kwargs):
    client = instance.client

    orders_count = client.orders.count()

    total_spent = client.orders.filter(
        status__in=[OrderStatusEnum.COMPLETED]
    ).aggregate(
        total=Sum("total_price")
    )["total"] or Decimal("0.00")

    Client.objects.filter(pk=client.pk).update(
        orders_count=orders_count,
        total_spent=total_spent
    )


@receiver(pre_save, sender=OrderItem)
def track_order_item_quantity_change(sender, instance, **kwargs):
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
def update_product_on_order_item_save(sender, instance, created, **kwargs):
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

    new_total = instance.order.calculate_total()

    Order.objects.filter(pk=instance.order.pk).update(
        total_price=new_total
    )

    instance.order.total_price = new_total


@receiver(post_delete, sender=OrderItem)
def update_product_on_order_item_delete(sender, instance, **kwargs):
    Product.objects.filter(pk=instance.product_id).update(
        stock=F("stock") + instance.quantity,
        sold=F("sold") - instance.quantity
    )

    new_total = instance.order.calculate_total()

    Order.objects.filter(pk=instance.order.pk).update(
        total_price=new_total
    )