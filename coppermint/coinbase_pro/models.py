from django.db import models

from coppermint.coinbase_pro.constants import (
    CoinbaseProduct,
    OrderCancelAfter,
    OrderLifeTime,
    OrderSide,
    OrderType,
    SelfTradePreventionFlag,
)


class Order(models.Model):

    order_id = models.CharField(max_length=191, primary_key=True)
    client_order_id = models.UUIDField()
    price = models.FloatField(blank=True, null=True)
    # Desired amount in crypto
    size = models.FloatField(blank=True, null=True)
    # Desired amount of quote currency to use
    funds = models.FloatField()
    product_id = models.CharField(max_length=191, default=CoinbaseProduct.BTC_EUR.value)
    side = models.CharField(
        max_length=191, choices=((OrderSide.BUY.value, "Buy order"), (OrderSide.SELL.value, "Sell order"))
    )
    # Self trade prevention
    stp = models.CharField(
        max_length=191, default=SelfTradePreventionFlag.DECREASE_AND_CANCEL.value, blank=True, null=True
    )
    order_type = models.CharField(max_length=191, default=OrderType.LIMIT.value)
    # only needed if order_type is 'stop'
    stop = models.CharField(max_length=191, blank=True, null=True)
    stop_price = models.FloatField(blank=True, null=True)
    # Order lifetime
    time_in_force = models.CharField(max_length=191, default=OrderLifeTime.GOOD_TIL_CANCELED, blank=True, null=True)
    cancel_after = models.CharField(
        max_length=191,
        blank=True,
        null=True,
        choices=(
            (OrderCancelAfter.MINUTE.value, "Cancel after 1 minute"),
            (OrderCancelAfter.HOUR.value, "Cancel after 1 hour"),
            (OrderCancelAfter.DAY.value, "Cancel after 24 hours"),
        ),
    )
    # Post-only: order can only be placed as a Maker Order.
    # An Order which would be posted as a Taker Order will be rejected.
    post_only = models.NullBooleanField(default=False, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    fill_fees = models.FloatField()
    filled_size = models.FloatField()
    executed_value = models.FloatField()
    status = models.CharField(max_length=191)
    settled = models.BooleanField(default=False)
