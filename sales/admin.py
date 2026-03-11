from django.contrib import admin
from .models import SalesSlip, SalesItem
from companies.models import Customer
from products.models import Product
from sales.forms import SalesItemForm

class SalesItemInline(admin.TabularInline):
    model = SalesItem
    extra = 1

    exclude = ("company",)  # (이미 적용했다면 유지)

    autocomplete_fields = ("product",)  # ✅ 이 줄 추가!

    form = SalesItemForm
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        # form에 request를 주입하기 위해 formset.form을 감싸기
        base_form = formset.form

        class RequestInjectedForm(base_form):
            def __init__(self, *args, **kws):
                kws["request"] = request
                super().__init__(*args, **kws)

        formset.form = RequestInjectedForm
        return formset


@admin.register(SalesSlip)
class SalesSlipAdmin(admin.ModelAdmin):
    inlines = [SalesItemInline]

    autocomplete_fields = ("customer",)  # ✅ 추천
    list_display = ("slip_no", "customer", "slip_date", "total_amount", "created_by")
    exclude = ("company", "created_by")  # (이미 적용했다면 유지)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == "customer":
            kwargs["queryset"] = Customer.objects.filter(company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # ✅ 거래처도 내 회사 것만
        if not request.user.is_superuser and db_field.name == "customer":
            kwargs["queryset"] = Customer.objects.filter(company=request.user.company)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
        # 슈퍼유저는 화면에서 company를 선택하는 방식
            if not obj.company_id:
                raise ValueError("Company를 선택하세요.")
            if not obj.created_by_id:
                obj.created_by = request.user
        else:
        # 일반유저는 자동 세팅
            if not request.user.company_id:
                raise ValueError("이 사용자에 회사(company)가 지정되어 있지 않습니다.")
            obj.company = request.user.company
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        obj.recompute_totals()
        obj.save(update_fields=["supply_amount", "vat_amount", "total_amount"])   

    def get_exclude(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        return ("company", "created_by")     
    



@admin.register(SalesItem)
class SalesItemAdmin(admin.ModelAdmin):
    list_display = ("slip", "product", "quantity", "unit_price", "total_amount")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser and not obj.company_id:
            obj.company = request.user.company
        super().save_model(request, obj, form, change)

