from typing import Dict, List, Optional

from django.db import models
from django.db.models import QuerySet
from django.conf import settings

from coppermint.coinbase_pro.client import CoinbaseClient
from coppermint.coinbase_pro.constants import (
    CoinbaseProduct,
    OrderCancelAfter,
    OrderLifeTime,
    OrderSide,
    OrderType,
    StopOrderType,
    SelfTradePreventionFlag,
    ACTIVE_ORDER_STATUSES,
    FILLED_ORDER_STATUSES,
)
from coppermint.order_helpers import calculate_buy_order_size


class Order(models.Model):

    order_id = models.CharField(max_length=191, primary_key=True)
    client_order_id = models.UUIDField()
    # price must be specified in quote_increment product units
    # for USD and EUR this is 0.01
    price = models.FloatField(blank=True, null=True)
    # Desired amount in crypto
    # must be bigger than the base_min_size and smaller than the base_max_size for the product
    # eg for BTC-EUR the min is 0.001 and max is 10000.0
    # Post-only limit orders have no enforced base_max_size
    size = models.FloatField(blank=True, null=True)
    # Desired amount of quote currency to use (only used for market orders)
    funds = models.FloatField(blank=True, null=True)
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
    stop_type = models.CharField(max_length=191, blank=True, null=True)
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

    @property
    def reverse_side(self):
        return OrderSide.SELL.value if self.side != OrderSide.SELL.value else OrderSide.BUY.value


class SimplePriceOscillationStrategy(models.Model):

    product_id = models.CharField(max_length=191, default=CoinbaseProduct.BTC_EUR.value)
    # Crypto price for initial order
    starting_price = models.FloatField(null=True)
    buy_percentage_difference = models.FloatField(default=0.0)
    sell_percentage_difference = models.FloatField(default=0.0)
    starting_funds = models.FloatField(default=0.0)
    current_funds = models.FloatField(default=0.0)
    max_order_funds = models.FloatField(default=0.0)
    max_total_funds = models.FloatField(default=0.0)
    accrued_fees = models.FloatField(default=0.0)

    @property
    def active_orders(self) -> QuerySet:
        return LinkedOrder.objects.filter(order_chain__in=self.orderchain_set.all(), status__in=ACTIVE_ORDER_STATUSES)

    @property
    def filled_orders(self) -> QuerySet:
        return LinkedOrder.objects.filter(order_chain__in=self.orderchain_set.all(), status__in=FILLED_ORDER_STATUSES)

    def calculate_order_price(self, previous_price: float, side: OrderSide):
        """"
        Calculates crypto price on which order should execute, rounded to 2 decimal places
        """
        if side == OrderSide.BUY.value:
            return round(previous_price - (previous_price / 100 * self.buy_percentage_difference), 2)
        return round(previous_price + (previous_price / 100 * self.buy_percentage_difference), 2)

    def create_new_api_order(
        self, client: CoinbaseClient, previous_order: Optional["LinkedOrder"] = None
    ) -> Dict[str, str]:
        if previous_order:
            order_side = previous_order.reverse_side
            order_price = self.calculate_order_price(previous_order.price, order_side)
            order_to_create = {
                "product_id": self.product_id,
                "side": order_side,
                "stop_type": (
                    StopOrderType.LOSS.value if order_side == OrderSide.SELL.value else StopOrderType.ENTRY.value
                ),
                "price": order_price,
                "size": (
                    previous_order.filled_size
                    if order_side == OrderSide.SELL.value
                    else calculate_buy_order_size(
                        funds_to_use=previous_order.executed_value - previous_order.fill_fees,
                        order_price=order_price,
                        fee_percentage=settings.COINBASE_PRO_TAKER_FEE,
                    )
                ),
                "overdraft_enabled": False,
            }
        else:
            # Create initial buy order if no previous order exists
            order_to_create = {
                "product_id": self.product_id,
                "side": OrderSide.BUY.value,
                "stop_type": StopOrderType.ENTRY.value,
                "price": self.starting_price,
                "size": calculate_buy_order_size(
                    funds_to_use=self.starting_funds,
                    order_price=self.starting_price,
                    fee_percentage=settings.COINBASE_PRO_TAKER_FEE,
                ),
                "overdraft_enabled": False,
            }

        return client.place_stop_order(**order_to_create)

    def create_new_order(self, client: CoinbaseClient, previous_order: Optional["LinkedOrder"] = None) -> None:
        new_order = self.create_new_api_order(client=client, previous_order=previous_order)
        order_chain = previous_order.order_chain if previous_order else OrderChain.objects.create(strategy=self)
        index = previous_order.index + 1 if previous_order else 1
        LinkedOrder.objects.create(
            order_chain=order_chain,
            index=index,
            order_id=new_order["id"],
            client_order_id=new_order["id"],
            price=new_order["price"],
            size=new_order["size"],
            funds=new_order.get("funds"),
            product_id=new_order["product_id"],
            side=new_order["side"],
            order_type=new_order["type"],
            stop=True if new_order.get("stop") else False,
            stop_type=new_order["stop"],
            stop_price=new_order["stop_price"],
            created_at=new_order["created_at"],
            fill_fees=new_order["fill_fees"],
            filled_size=new_order["filled_size"],
            executed_value=new_order["executed_value"],
            status=new_order["status"],
            settled=new_order["settled"],
        )

    def evaluate_orders(self, client: CoinbaseClient, orders: List["LinkedOrder"]) -> None:
        for order in orders:
            if order.status in FILLED_ORDER_STATUSES:
                self.create_new_order(client=client, previous_order=order)

    def update_active_orders(self, client: CoinbaseClient) -> None:
        updated_orders = []
        for order in self.active_orders:
            updated_order_info = client.get_order(order_id=order.order_id)
            order.filled_size = updated_order_info["filled_size"]
            order.executed_value = updated_order_info.get("executed_value", order.executed_value)
            order.status = updated_order_info["status"]
            order.settled = updated_order_info["settled"]
            updated_orders.append(order)
        LinkedOrder.objects.bulk_update(
            updated_orders, fields=["filled_size", "executed_value", "status", "settled", "updated_at"]
        )
        self.update_accrued_fees(fees=[order.fill_fees for order in updated_orders])
        self.evaluate_orders(client, orders=updated_orders)

    def update_accrued_fees(self, fees: List[float]) -> None:
        self.accrued_fees += sum(fees)
        self.save()

    def _set_percentages(self):
        raise NotImplementedError

    def evaluate(self):
        raise NotImplementedError


class OrderChain(models.Model):
    strategy = models.ForeignKey(SimplePriceOscillationStrategy, on_delete=models.SET_NULL, null=True, blank=True)


class LinkedOrder(Order):
    order_chain = models.ForeignKey(OrderChain, on_delete=models.SET_NULL, null=True, blank=True)
    index = models.BigIntegerField()

    class Meta:
        unique_together = ["order_chain", "index"]
