from django.db import models
from django.contrib.auth.models import AbstractUser


class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="회사명")
    business_number = models.CharField(max_length=20, unique=True, verbose_name="사업자번호")
    ceo_name = models.CharField(max_length=100, verbose_name="대표자")
    address = models.CharField(max_length=255, blank=True, verbose_name="주소")
    phone = models.CharField(max_length=20, blank=True, verbose_name="전화번호")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="users",
    )
    is_company_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username