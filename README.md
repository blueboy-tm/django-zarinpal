# django-zarinpal

Forked from [Glyphack/django-zarinpal](https://github.com/Glyphack/django-zarinpal)

Integrate django payments with [zarinpal](https://www.zarinpal.com)


Quickstart
----------

Install django-zarinpal::

    pip install git+https://github.com/blueboy-tm/django-zarinpal.git@master

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_zarinpal',
        ...
    )





### How to Use

set these variables in your settings file:

```python

ZARINPAL_SIMULATION: bool # is transactions for test?

ZARINPAL_MERCHANT_ID: str # merchant id from zarinpal (you may leave it blank if you set the simulation to True)
```

you can use function `start_transaction` with a dictionary containing your transaction data like this:

```python
from django.shortcuts import redirect
from django_zarinpal.services import start_transaction


def start_payment(request):
    result = start_transaction(
        amount=10000, callback_url='/',  user=request.user, mobile=None, email=None,
        description='transaction description'
    )
    return redirect(result) # result is the url for starting transaction
```


You can use verify_transaction to verify the transaction
```python
from django_zarinpal.services import verify_transaction
from django_zarinpal.exceptions import TransactionDoesNotExist
from django.http import HttpResponse, Http404

def payment_callback(request):
    authority = request.GET.get("Authority")
    status = request.GET.get("Status")
    try:
        transaction = verify_transaction(status, authority)
        if transaction.is_successful():
            return HttpResponse('Thanks for payment.')
        return HttpResponse(transaction.failure_reason)
    except TransactionDoesNotExist:
        raise Http404
```
