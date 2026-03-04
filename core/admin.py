from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from .models import Company, User


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "business_number", "ceo_name", "phone", "created_at")
    search_fields = ("name", "business_number")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("회사 정보", {"fields": ("company", "is_company_admin")}),
    )
    list_display = ("username", "email", "company", "is_company_admin", "is_staff", "is_superuser")
    list_filter = ("company", "is_company_admin", "is_staff", "is_superuser")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(company=request.user.company)

    def save_model(self, request, obj, form, change):
        # 슈퍼유저가 아니면 회사 자동 지정
        if not request.user.is_superuser and not obj.company_id:
            obj.company = request.user.company
        super().save_model(request, obj, form, change)