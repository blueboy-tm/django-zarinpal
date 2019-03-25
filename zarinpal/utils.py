from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.urls import reverse
from zeep import Client

from zarinpal.exceptions import TransactionDoesNotExist
from .config import (
    ZARINPAL_MERCHANT_ID,
    ZARINPAL_SIMULATION,
    ZARINPAL_START_GATEWAY,
    ZARINPAL_WEBSERVICE,
    ZARINPAL_CALLBACK_URL)
from .models import Transaction


def start_transaction(transaction_data: dict) -> str:
    transaction = Transaction.objects.create_transaction(transaction_data)
    start_transaction_data = generate_start_transaction_data(transaction)
    client = Client(ZARINPAL_WEBSERVICE)
    result = client.service.PaymentRequest(
        start_transaction_data['merchant_id'],
        start_transaction_data['amount'],
        start_transaction_data['description'],
        start_transaction_data['email'],
        start_transaction_data['mobile'],
        start_transaction_data['callback_url'],
    )
    print(start_transaction_data)
    if result.Status == 100:
        return ZARINPAL_START_GATEWAY + result.Authority
    else:
        print(result)


def verify_transaction(status: str, authority: int) -> Transaction:
    client = Client(ZARINPAL_WEBSERVICE)
    try:
        transaction = Transaction.objects.get(authority=authority)
    except Transaction.DoesNotExist:
        raise TransactionDoesNotExist
    if status == "OK":
        result = client.service.PaymentVerification(
            ZARINPAL_MERCHANT_ID, authority, transaction.amount
        )
        if result.Status == 100:
            transaction.success(result.RefID)
        elif result.Status == 101:
            transaction.status = result.Status
            return HttpResponse('Transaction submitted : ' + str(result.Status))
        else:
            transaction.fail(result.Status)
    else:
        transaction.fail('Canceled')

    return transaction


def generate_start_transaction_data(transaction):
    return {
        'merchant_id': ZARINPAL_MERCHANT_ID,
        "amount": transaction.amount,
        "description": transaction.description,
        "email": transaction.email,
        "mobile": transaction.mobile,
        "callback_url": get_callback_url(),
    }


def get_callback_url():
    if ZARINPAL_CALLBACK_URL:
        return ZARINPAL_CALLBACK_URL
    else:
        return Site.objects.get_current().domain + reverse(
            'zarinpal:verify_transaction',
        )


