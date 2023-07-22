from typing import Dict

from django.urls import reverse
from zeep import Client

from django_zarinpal.config import (
    ZARINPAL_START_GATEWAY,
    ZARINPAL_SANDBOX
)
from django_zarinpal.config import (
    ZARINPAL_WEBSERVICE,
    ZARINPAL_MERCHANT_ID
)
from django_zarinpal.exceptions import (
    CouldNotStartTransaction,
    AmountIsLessThanMinimum
)
from django_zarinpal.exceptions import TransactionDoesNotExist
from django_zarinpal.models import Transaction


def start_transaction(amount, callback_url,  user=None, mobile=None, email=None, description='null') -> str:
    transaction = Transaction(
        user=user,
        amount=amount,
        description=description,
        is_test=ZARINPAL_SANDBOX
    )

    client = Client(ZARINPAL_WEBSERVICE)
    result = client.service.PaymentRequest(
        ZARINPAL_MERCHANT_ID,
        amount,
        description,
        email,
        mobile,
        callback_url,
    )

    if result.Status == 100:
        transaction.authority = result.Authority
        transaction.save()
        return ZARINPAL_START_GATEWAY + result.Authority
    elif result.Status == -3:
        raise AmountIsLessThanMinimum(f"response:{result}")
    else:
        raise CouldNotStartTransaction(f"response:{result}")


def verify_transaction(status: str, authority: int) -> Transaction:
    client = Client(ZARINPAL_WEBSERVICE)

    try:
        transaction = Transaction.objects.get(status="PENDING",
                                              authority=authority)
    except Transaction.DoesNotExist:
        raise TransactionDoesNotExist()

    if status == "OK":
        result = client.service.PaymentVerification(
            ZARINPAL_MERCHANT_ID, authority, transaction.amount
        )
        if result.Status == 100:
            transaction.success(result.RefID)
        else:
            transaction.fail(result.Status)
    else:
        transaction.fail("انصراف توسط کاربر")

    return transaction
