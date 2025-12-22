from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.products.models import Product
from apps.products.state_mashine.state_factory import get_product_state


@receiver(pre_save, sender=Product)
def product_status_signal(sender, instance: Product, **kwargs):
    state = get_product_state(instance)
    resolved_status = state.next_state()

    if resolved_status != instance.status:
        instance.status = resolved_status
