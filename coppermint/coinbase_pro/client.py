from cbpro import AuthenticatedClient
from django.conf import settings


class CoinbaseClient(AuthenticatedClient):
    def __init__(self):
        super().__init__(key=settings.COINBASE_PRO_API_KEY, b64secret=settings.COINBASE_PRO_API_SECRET,
                         passphrase=settings.COINBASE_PRO_API_PASSPHRASE, api_url=settings.COINBASE_PRO_API_URL)
