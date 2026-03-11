from django.db import models
from core.models import Company, User
from companies.models import Customer
from products.models import Product


class PurchaseSlip(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="purchase_slips")
    supplier = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="purchase_slips")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_purchase_slips")

    slip_date = models.DateField(auto_now_add=True)

    supply_amount = models.IntegerField(default=0, verbose_name="공급가액")
    vat_amount = models.IntegerField(default=0, verbose_name="부가세")
    total_amount = models.IntegerField(default=0, verbose_name="합계")

    memo = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slip_no = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"매입전표 #{self.id}"

    def recompute_totals(self):
        agg = self.items.aggregate(
            supply=models.Sum("supply_amount"),
            vat=models.Sum("vat_amount"),
            total=models.Sum("total_amount"),
        )
        self.supply_amount = int(agg["supply"] or 0)
        self.vat_amount = int(agg["vat"] or 0)
        self.total_amount = int(agg["total"] or 0)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            date_str = self.slip_date.strftime("%Y%m%d")
            self.slip_no = f"P-{date_str}-{self.id:04d}"
            super().save(update_fields=["slip_no"])


class PurchaseItem(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="purchase_items")
    slip = models.ForeignKey(PurchaseSlip, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    quantity = models.IntegerField(default=1)
    unit_price = models.IntegerField(default=0)

    supply_amount = models.IntegerField(default=0)
    vat_amount = models.IntegerField(default=0)
    total_amount = models.IntegerField(default=0)
   

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.company_id and self.slip_id:
            self.company_id = self.slip.company_id

        if (self.unit_price or 0) == 0 and self.product_id:
            self.unit_price = self.product.cost_price or 0

        qty = int(self.quantity or 0)
        unit = int(self.unit_price or 0)
        supply = qty * unit

        vat = 0
        if self.product_id and getattr(self.product, "vat_type", "TAX") == "TAX":
            vat = supply // 10

        self.supply_amount = supply
        self.vat_amount = vat
        self.total_amount = supply + vat

        super().save(*args, **kwargs)