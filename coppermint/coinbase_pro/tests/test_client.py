from unittest.mock import patch

from django.conf import settings

from coppermint.coinbase_pro.client import CoinbaseClient


def test_client():
    with patch("coppermint.coinbase_pro.client.AuthenticatedClient.__init__", return_value=None) as mock_client:
        CoinbaseClient()
        assert mock_client.called_with(
            settings.COINBASE_PRO_API_KEY,
            settings.COINBASE_PRO_API_SECRET,
            settings.COINBASE_PRO_API_PASSPHRASE,
            settings.COINBASE_PRO_API_URL,
        )
