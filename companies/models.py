from django.db import models

# Create your models here.

from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=100, verbose_name="거래처명")
    business_number = models.CharField(max_length=20, blank=True, verbose_name="사업자번호")
    phone = models.CharField(max_length=20, blank=True, verbose_name="전화번호")
    address = models.CharField(max_length=200, blank=True, verbose_name="주소")
    credit_limit = models.IntegerField(default=0, verbose_name="여신한도")
    current_balance = models.IntegerField(default=0, verbose_name="현재잔액")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    