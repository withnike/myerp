from django import forms
from products.models import Product
from .models import SalesItem


class SalesItemForm(forms.ModelForm):
    product_code = forms.CharField(
        required=False,
        label="상품코드/바코드",
        help_text="품목코드(sku) 또는 바코드 입력",
    )

    class Meta:
        model = SalesItem
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # 기존 product 선택은 유지하되, 사용자는 product_code를 주로 쓰게 할 것
        # (원하면 product 필드를 숨길 수도 있음)

    def clean(self):
        cleaned = super().clean()
        code = (cleaned.get("product_code") or "").strip()

        # 이미 product가 선택되어 있으면 OK
        if cleaned.get("product"):
            return cleaned

        if not code:
            raise forms.ValidationError("상품을 선택하거나 상품코드/바코드를 입력하세요.")

        # 회사 기준으로 상품 찾기
        qs = Product.objects.all()
        if self.request and (not self.request.user.is_superuser):
            qs = qs.filter(company=self.request.user.company)

        product = qs.filter(sku=code).first()
        if not product:
            product = qs.filter(barcode=code).first()

        if not product:
            raise forms.ValidationError(f"상품을 찾을 수 없습니다: {code}")

        cleaned["product"] = product
        return cleaned