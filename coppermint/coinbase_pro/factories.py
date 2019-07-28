from factory import DjangoModelFactory, SubFactory, Sequence
from uuid import uuid4

from django.utils import timezone

from coppermint.coinbase_pro.constants import (
    CoinbaseProduct,
    OrderStatus,
    OrderLifeTime,
    StopOrderType,
    OrderType,
    OrderSide,
    SelfTradePreventionFlag,
)
from coppermint.coinbase_pro.models import Order, LinkedOrder, OrderChain


class OrderFactory(DjangoModelFactory):
    class Meta:
        model = Order

    order_id = Sequence(lambda _: uuid4())
    client_order_id = Sequence(lambda _: uuid4())
    price = 15000.00
    size = 0.1
    funds = None
    product_id = CoinbaseProduct.BTC_EUR.value
    side = OrderSide.SELL.value
    stp = SelfTradePreventionFlag.DECREASE_AND_CANCEL.value
    order_type = OrderType.LIMIT.value
    stop = StopOrderType.LOSS
    stop_price = 15000.00
    time_in_force = OrderLifeTime.GOOD_TIL_CANCELED
    cancel_after = None
    post_only = None
    created_at = timezone.now()
    fill_fees = 0.0
    filled_size = 0.0
    executed_value = 0.0
    status = OrderStatus.ACTIVE.value
    settled = False


class OrderChainFactory(DjangoModelFactory):
    class Meta:
        model = OrderChain


class LinkedOrderFactory(DjangoModelFactory):
    class Meta:
        model = LinkedOrder

    order_id = Sequence(lambda _: uuid4())
    client_order_id = Sequence(lambda _: uuid4())
    price = 15000.00
    size = 0.1
    funds = None
    product_id = CoinbaseProduct.BTC_EUR.value
    side = OrderSide.SELL.value
    stp = SelfTradePreventionFlag.DECREASE_AND_CANCEL.value
    order_type = OrderType.LIMIT.value
    stop = StopOrderType.LOSS
    stop_price = 15000.00
    time_in_force = OrderLifeTime.GOOD_TIL_CANCELED
    cancel_after = None
    post_only = None
    created_at = timezone.now()
    fill_fees = 0.0
    filled_size = 0.0
    executed_value = 0.0
    status = OrderStatus.ACTIVE.value
    settled = False
    order_chain = SubFactory(OrderChainFactory)
    index = Sequence(lambda n: n)
