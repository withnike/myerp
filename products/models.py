from django.db import models
from core.models import Company


class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="products")

    sku = models.CharField(max_length=50, verbose_name="품목코드")
    name = models.CharField(max_length=255, verbose_name="품명")
    spec = models.CharField(max_length=255, blank=True, verbose_name="규격")
    unit = models.CharField(max_length=20, blank=True, verbose_name="단위")
    maker = models.CharField(max_length=100, blank=True, verbose_name="메이커명")
    location = models.CharField(max_length=100, blank=True, verbose_name="위치")

    barcode = models.CharField(max_length=50, blank=True, verbose_name="바코드")

    cost_price = models.IntegerField(default=0, verbose_name="매입단가")
    sale_price = models.IntegerField(default=0, verbose_name="판매단가")
    vat_type = models.CharField(
        max_length=10,
        choices=(("TAX", "과세"), ("ZERO", "영세"), ("EXEMPT", "면세")),
        default="TAX",
        verbose_name="부가세구분",
    )

    is_active = models.BooleanField(default=True, verbose_name="사용여부")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("company", "sku"),)
        indexes = [
            models.Index(fields=["company", "sku"]),
            models.Index(fields=["company", "name"]),
            models.Index(fields=["company", "barcode"]),
        ]

    def __str__(self):
        return f"{self.sku} {self.name}"


class Inventory(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="inventories")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventories")

    quantity = models.IntegerField(default=0, verbose_name="현재고")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["company", "product"], name="uniq_inventory_company_product"),
        ]

    def __str__(self):
        return f"{self.product.sku} 재고 {self.quantity}"
    
class InventoryTx(models.Model):
    TX_TYPE_CHOICES = (
        ("SALE_ITEM", "매출전표 품목"),
        ("PURCHASE_ITEM", "매입전표 품목"),  # 다음에 붙일 예정
        ("ADJUST", "재고조정"),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="inventory_txs")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory_txs")

    tx_type = models.CharField(max_length=30, choices=TX_TYPE_CHOICES)
    source_id = models.IntegerField()  # 예: SalesItem.id

    qty_change = models.IntegerField()  # 재고변동 (+증가, -감소)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["tx_type", "source_id"], name="uniq_tx_type_source"),
        ]
        indexes = [
            models.Index(fields=["company", "product"]),
            models.Index(fields=["tx_type", "source_id"]),
        ]

    def __str__(self):
        return f"{self.tx_type}:{self.source_id} {self.product.sku} {self.qty_change}"   