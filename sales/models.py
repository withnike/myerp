from django.db import models
from core.models import Company, User
from companies.models import Customer
from products.models import Product


class SalesSlip(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="sales_slips")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="sales_slips")
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_sales_slips")

    slip_date = models.DateField(auto_now_add=True)

    supply_amount = models.IntegerField(default=0, verbose_name="공급가액")
    vat_amount = models.IntegerField(default=0, verbose_name="부가세")
    total_amount = models.IntegerField(default=0, verbose_name="합계")

    memo = models.CharField(max_length=255, blank=True)
    slip_no = models.CharField(max_length=30, blank=True)  # 나중에 자동 생성할 예정
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"매출전표 #{self.id}"

    def recompute_totals(self):
        agg = self.items.aggregate(
            supply=models.Sum("supply_amount"),
            vat=models.Sum("vat_amount"),
            total=models.Sum("total_amount"),
        )
        self.supply_amount = int(agg["supply"] or 0)
        self.vat_amount = int(agg["vat"] or 0)
        self.total_amount = int(agg["total"] or 0)


class SalesItem(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="sales_items")
    slip = models.ForeignKey(SalesSlip, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    quantity = models.IntegerField(default=1)
    unit_price = models.IntegerField(default=0)
    supply_amount = models.IntegerField(default=0)
    vat_amount = models.IntegerField(default=0)
    total_amount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.sku} x {self.quantity}"

    def save(self, *args, **kwargs):
        # 회사 자동 세팅
        if not self.company_id and self.slip_id:
            self.company_id = self.slip.company_id

        # 단가 자동 (비어 있으면 상품 판매단가)
        if (self.unit_price or 0) == 0 and self.product_id:
            self.unit_price = self.product.sale_price or 0

        qty = int(self.quantity or 0)
        unit = int(self.unit_price or 0)
        supply = qty * unit

        vat = 0
        if self.product_id and getattr(self.product, "vat_type", "TAX") == "TAX":
            vat = supply // 10  # 10% 원단위 절삭(단순)

        self.supply_amount = supply
        self.vat_amount = vat
        self.total_amount = supply + vat

        super().save(*args, **kwargs)

