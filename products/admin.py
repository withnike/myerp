from django.contrib import admin
from .models import Product, Inventory, InventoryTx


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "spec", "unit", "maker", "location", "sale_price", "cost_price", "is_active")
    search_fields = ("sku", "name", "barcode", "maker")
    list_filter = ("is_active", "vat_type", "maker")
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


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity", "updated_at")
    search_fields = ("product__sku", "product__name")
    list_per_page = 50

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)
    
@admin.register(InventoryTx)
class InventoryTxAdmin(admin.ModelAdmin):
    list_display = ("product", "tx_type", "source_id", "qty_change", "created_at")
    search_fields = ("product__sku", "product__name")
    list_filter = ("tx_type",)    