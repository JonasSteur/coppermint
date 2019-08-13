from typing import List

from cbpro import AuthenticatedClient
from cbpro.websocket_client import WebsocketClient

from django.conf import settings

from coppermint.coinbase_pro.constants import CoinbaseFeedChannel, CoinbaseProduct


class CoinbaseClient(AuthenticatedClient):
    def __init__(self):
        super().__init__(
            key=settings.COINBASE_PRO_API_KEY,
            b64secret=settings.COINBASE_PRO_API_SECRET,
            passphrase=settings.COINBASE_PRO_API_PASSPHRASE,
            api_url=settings.COINBASE_PRO_API_URL,
        )


class CoinbaseFeedClient(WebsocketClient):
    def __init__(self, products: List[CoinbaseProduct], channels=List[CoinbaseFeedChannel]):
        super().__init__(
            url=settings.COINBASE_PRO_API_FEED_URL,
            products=products,
            channels=channels,
            auth=True,
            api_key=settings.COINBASE_PRO_API_KEY,
            api_secret=settings.COINBASE_PRO_API_SECRET,
            api_passphrase=settings.COINBASE_PRO_API_PASSPHRASE,
        )
