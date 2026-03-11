from django.db.models.signals import post_save
from django.dispatch import receiver

from products.models import InventoryTx
from .models import PurchaseItem


@receiver(post_save, sender=PurchaseItem)
def purchase_item_inventory(sender, instance, created, **kwargs):

    if created:

        InventoryTx.objects.create(
            company=instance.company,
            product=instance.product,
            tx_type="PURCHASE_ITEM",
            source_id=instance.id,
            qty_change=instance.quantity,
        )