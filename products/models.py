from django.db import models
from core.models import Company

class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="products")

    # 유통/철물 필수
    sku = models.CharField(max_length=50, verbose_name="품목코드")  # 내부코드
    name = models.CharField(max_length=255, verbose_name="품목명")
    maker = models.CharField(max_length=100, blank=True, verbose_name="메이커")
    category_l = models.CharField(max_length=100, blank=True, verbose_name="대분류")
    category_m = models.CharField(max_length=100, blank=True, verbose_name="중분류")
    category_s = models.CharField(max_length=100, blank=True, verbose_name="소분류")

    barcode = models.CharField(max_length=50, blank=True, verbose_name="바코드")
    unit = models.CharField(max_length=20, blank=True, verbose_name="단위")  # EA, BOX 등

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
        unique_together = (("company", "sku"),)  # 회사별 품목코드 중복 방지
        indexes = [
            models.Index(fields=["company", "name"]),
            models.Index(fields=["company", "barcode"]),
        ]

    def __str__(self):
        return f"{self.sku} {self.name}"