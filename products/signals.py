from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import Sum
from django.db import transaction

from products.models import Inventory, InventoryTx


@receiver(pre_save, sender="sales.SalesItem")
def cache_old_salesitem(sender, instance, **kwargs):
    """
    수정 시 이전 상태(상품/수량)를 알아야 재고를 정확히 조정할 수 있음.
    """
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_product_id = old.product_id
            instance._old_qty = old.quantity
        except sender.DoesNotExist:
            instance._old_product_id = None
            instance._old_qty = None
    else:
        instance._old_product_id = None
        instance._old_qty = None


def recalc_inventory(company_id: int, product_id: int):
    """
    해당 회사/상품의 재고를 InventoryTx 합계로 재계산.
    (초기엔 단순하게, 나중에 최적화 가능)
    """
    total = (
        InventoryTx.objects
        .filter(company_id=company_id, product_id=product_id)
        .aggregate(s=Sum("qty_change"))
        .get("s") or 0
    )
    inv, _ = Inventory.objects.get_or_create(company_id=company_id, product_id=product_id)
    inv.quantity = int(total)
    inv.save(update_fields=["quantity"])


@receiver(post_save, sender="sales.SalesItem")
def upsert_salesitem_tx(sender, instance, created, **kwargs):
    """
    SalesItem 1줄당 InventoryTx 1개를 유지(Upsert).
    qty_change는 매출이므로 -quantity
    """
    company_id = instance.company_id
    product_id = instance.product_id

    def _apply():
        InventoryTx.objects.update_or_create(
            tx_type="SALE_ITEM",
            source_id=instance.id,
            defaults={
                "company_id": company_id,
                "product_id": product_id,
                "qty_change": -int(instance.quantity),
            },
        )

        # 상품이 바뀐 수정이면 이전 상품 재고도 다시 계산
        old_pid = getattr(instance, "_old_product_id", None)
        if old_pid and old_pid != product_id:
            recalc_inventory(company_id, old_pid)

        recalc_inventory(company_id, product_id)

    transaction.on_commit(_apply)


@receiver(post_delete, sender="sales.SalesItem")
def delete_salesitem_tx(sender, instance, **kwargs):
    company_id = instance.company_id
    product_id = instance.product_id

    def _apply():
        InventoryTx.objects.filter(tx_type="SALE_ITEM", source_id=instance.id).delete()
        recalc_inventory(company_id, product_id)

    transaction.on_commit(_apply)