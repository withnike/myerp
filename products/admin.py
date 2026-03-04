from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "maker", "sale_price", "cost_price", "barcode", "is_active")
    list_filter = ("is_active", "vat_type", "maker")
    search_fields = ("sku", "name", "barcode", "maker")
    list_editable = ("sale_price", "cost_price", "is_active")
    list_per_page = 50

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not obj.company_id:
            obj.company = request.user.company
        super().save_model(request, obj, form, change)