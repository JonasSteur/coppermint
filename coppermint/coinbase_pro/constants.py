from enum import Enum


class CoinbaseProduct(Enum):
    ZRX_EUR = "ZRX-EUR"
    BAT_USDC = "BAT-USDC"
    GNT_USDC = "GNT-USDC"
    XRP_USD = "XRP-USD"
    REP_BTC = "REP-BTC"
    BTC_USDC = "BTC-USDC"
    ZRX_USD = "ZRX-USD"
    ETC_USD = "ETC-USD"
    XRP_EUR = "XRP-EUR"
    LTC_EUR = "LTC-EUR"
    LTC_USD = "LTC-USD"
    ETC_GBP = "ETC-GBP"
    ETH_EUR = "ETH-EUR"
    ETH_BTC = "ETH-BTC"
    LINK_USD = "LINK-USD"
    EOS_USD = "EOS-USD"
    LTC_BTC = "LTC-BTC"
    DAI_USDC = "DAI-USDC"
    CVC_USDC = "CVC-USDC"
    LINK_ETH = "LINK-ETH"
    MANA_USDC = "MANA-USDC"
    DNT_USDC = "DNT-USDC"
    BCH_EUR = "BCH-EUR"
    ZRX_BTC = "ZRX-BTC"
    BTC_USD = "BTC-USD"
    BCH_GBP = "BCH-GBP"
    BTC_GBP = "BTC-GBP"
    ETH_USD = "ETH-USD"
    ETC_EUR = "ETC-EUR"
    BTC_EUR = "BTC-EUR"
    ZEC_USDC = "ZEC-USDC"
    ETH_GBP = "ETH-GBP"
    ETH_USDC = "ETH-USDC"
    LOOM_USDC = "LOOM-USDC"
    LTC_GBP = "LTC-GBP"
    ZEC_BTC = "ZEC-BTC"
    BAT_ETH = "BAT-ETH"
    BCH_BTC = "BCH-BTC"
    EOS_EUR = "EOS-EUR"
    REP_USD = "REP-USD"
    EOS_BTC = "EOS-BTC"
    XLM_USD = "XLM-USD"
    ETC_BTC = "ETC-BTC"
    XRP_BTC = "XRP-BTC"
    ETH_DAI = "ETH-DAI"
    XLM_BTC = "XLM-BTC"
    BCH_USD = "BCH-USD"
    XLM_EUR = "XLM-EUR"


class SelfTradePreventionFlag(Enum):
    DECREASE_AND_CANCEL = "dc"
    CANCEL_OLDERS = "cd"
    CANCEL_NEWEST = "cn"
    CANCEL_BOTH = "cb"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    LIMIT = "limit"
    MARKET = "market"
    STOP = "stop"


class OrderLifeTime(Enum):
    GOOD_TIL_CANCELED = "GTC"
    GOOD_TIL_TIME = "GTT"
    IMMEDIATE_OR_CANCEL = "IOC"
    FILL_OR_KILL = "FOK"


class OrderCancelAfter(Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "DAY"


class OrderStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    ACTIVE = "active"
    DONE = "done"
    SETTLED = "settled"


class StopOrderType(Enum):
    # Loss: Triggers when the last trade price changes to a value at or below the stop_price.
    LOSS = "loss"
    # Entry: Triggers when the last trade price changes to a value at or above the stop_price
    ENTRY = "entry"
