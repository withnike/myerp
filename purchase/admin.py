from django.contrib import admin
from .models import PurchaseSlip, PurchaseItem
from companies.models import Customer
from products.models import Product


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    exclude = ("company",)
    autocomplete_fields = ("product",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == "product":
            kwargs["queryset"] = Product.objects.filter(company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(PurchaseSlip)
class PurchaseSlipAdmin(admin.ModelAdmin):
    inlines = [PurchaseItemInline]
    list_display = ("slip_no", "supplier", "slip_date", "total_amount", "created_by")
    autocomplete_fields = ("supplier",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)

    def get_exclude(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        return ("company", "created_by")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == "supplier":
            kwargs["queryset"] = Customer.objects.filter(company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            if not obj.created_by_id:
                obj.created_by = request.user
        else:
            obj.company = request.user.company
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        obj.recompute_totals()
        obj.save(update_fields=["supply_amount", "vat_amount", "total_amount"])