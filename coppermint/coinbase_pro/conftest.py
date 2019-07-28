from unittest.mock import MagicMock
from pytest import fixture

from coppermint.coinbase_pro.client import CoinbaseClient


@fixture
def coinbase_client_mock():
    return MagicMock(spec=CoinbaseClient)
