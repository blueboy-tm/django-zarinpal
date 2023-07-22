from django.conf import settings

from django_zarinpal.exceptions import MerchantIdNotSet

ZARINPAL_WEBSERVICE = "https://www.zarinpal.com/pg/services/WebGate/wsdl"
ZARINPAL_START_GATEWAY = "https://www.zarinpal.com/pg/StartPay/"

ZARINPAL_SANDBOX = getattr(settings, "ZARINPAL_SIMULATION", False)

ZARINPAL_MERCHANT_ID = getattr(settings, "ZARINPAL_MERCHANT_ID", None)
if not ZARINPAL_SANDBOX and not ZARINPAL_MERCHANT_ID:
    raise MerchantIdNotSet("Specify ZARINPAL_MERCHANT_ID in settings")

if ZARINPAL_SANDBOX:
    ZARINPAL_WEBSERVICE = "https://sandbox.zarinpal.com/pg/services/WebGate/wsdl"
    ZARINPAL_START_GATEWAY = "https://sandbox.zarinpal.com/pg/StartPay/"
    ZARINPAL_MERCHANT_ID = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
