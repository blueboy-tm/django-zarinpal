from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

from django_zarinpal.config import ZARINPAL_START_GATEWAY


class Transaction(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name='کاربر', null=True, blank=True)
    amount = models.DecimalField(max_digits=64, decimal_places=2, verbose_name='مقدار')
    authority = models.CharField(max_length=100, blank=True, null=True, verbose_name='شناسه مرجع')
    ref_id = models.IntegerField(null=True, blank=True, verbose_name='کد پیگیری')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    verified_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تایید')

    TRANSACTION_STATUS_CHOICES = (
        ("PENDING", "تراکنش شروع شده است"),
        ("FAILED", "تراکنش با خطا مواجه شد"),
        ("SUCCESS", "نراکنش با موفقیت انجام شد"),
    )
    status = models.CharField(
        max_length=100,
        choices=TRANSACTION_STATUS_CHOICES,
        default="PENDING",
        verbose_name='وضعیت'
    )
    failure_reason = models.CharField(max_length=100, blank=True, null=True, verbose_name='دلیل خطا')
    is_test = models.BooleanField(default=False, verbose_name='آیا تراکنش آزمایشی است؟')

    def success(self, ref_id):
        self.ref_id = ref_id
        self.status = "SUCCESS"
        self.verified_at = timezone.now()
        self.save(
            update_fields=["status", "verified_at", "ref_id"]
        )

    def fail(self, failure_reason=""):
        self.status = "FAILED"
        if failure_reason:
            self.failure_reason = failure_reason
            self.save(update_fields=["status", "failure_reason"])
        else:
            self.save(update_fields=["status"])

    def is_successful(self):
        return self.status == "SUCCESS"

    def get_transaction_start_url(self, request=None):
        if self.is_test is False:
            return ZARINPAL_START_GATEWAY + self.authority
        else:
            relative_start_url = reverse(
                "django_zarinpal:sandbox-payment",
                kwargs={"authority_start": self.authority}
            )
            if request:
                return request.build_absolute_uri(relative_start_url)
            else:
                return relative_start_url
    class Meta:
        verbose_name = 'تراکنش زرین‌پال'
        verbose_name_plural = 'تراکنش های زرین‌پال'
        ordering = ('created_at',)

    def __str__(self) -> str:
        return self.id

