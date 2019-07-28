from pytest import fixture, mark
from unittest.mock import patch

from coppermint.coinbase_pro.models import SimplePriceOscillationStrategy
from coppermint.coinbase_pro.factories import OrderChainFactory, LinkedOrderFactory, OrderFactory
from coppermint.coinbase_pro.constants import OrderStatus
from coppermint.coinbase_pro.constants import OrderSide, StopOrderType


@fixture()
def order_response():
    return {
        "created_at": "2019-07-18T00:27:42.920136Z",
        "executed_value": "0.0000000000000000",
        "fill_fees": "0.0000000000000000",
        "filled_size": "0.00000000",
        "id": "9456f388-67a9-4316-bad1-330c5353804f",
        "post_only": False,
        "price": "10000.0",
        "product_id": "BTC-EUR",
        "settled": True,
        "side": "buy",
        "size": "0.01097257",
        "status": "open",
        "stp": "dc",
        "time_in_force": "GTC",
        "type": "limit",
        "stop": "entry",
        "stop_price": "10000.0",
    }


@mark.parametrize("order_side, expected", [(OrderSide.BUY, OrderSide.SELL), (OrderSide.SELL, OrderSide.BUY)])
def test_order_reverse_side(order_side, expected):
    assert OrderFactory(side=order_side.value).reverse_side == expected.value


def test_simple_price_oscillation_strategy_get_active_linked_orders():
    strategy = SimplePriceOscillationStrategy.objects.create()
    order_chain = OrderChainFactory(strategy=strategy)
    active_linked_orders = LinkedOrderFactory.create_batch(15, status=OrderStatus.OPEN.value, order_chain=order_chain)
    filled_linked_orders = LinkedOrderFactory.create_batch(14, status=OrderStatus.DONE.value, order_chain=order_chain)
    # create some other unlinked orders
    unlinked_orders = LinkedOrderFactory.create_batch(5)

    for order in active_linked_orders:
        assert strategy.active_orders.filter(order_id=order.order_id).exists()

    for order in filled_linked_orders:
        assert not strategy.active_orders.filter(order_id=order.order_id).exists()

    for order in unlinked_orders:
        assert not strategy.active_orders.filter(order_id=order.order_id).exists()


def test_simple_price_oscillation_strategy_get_filled_linked_orders():
    strategy = SimplePriceOscillationStrategy.objects.create()
    order_chain = OrderChainFactory(strategy=strategy)
    active_linked_orders = LinkedOrderFactory.create_batch(15, status=OrderStatus.OPEN.value, order_chain=order_chain)
    filled_linked_orders = LinkedOrderFactory.create_batch(14, status=OrderStatus.DONE.value, order_chain=order_chain)
    # create some other unlinked orders
    unlinked_orders = LinkedOrderFactory.create_batch(5)

    for order in filled_linked_orders:
        assert strategy.filled_orders.filter(order_id=order.order_id).exists()

    for order in active_linked_orders:
        assert not strategy.filled_orders.filter(order_id=order.order_id).exists()

    for order in unlinked_orders:
        assert not strategy.filled_orders.filter(order_id=order.order_id).exists()


def test_update_active_orders(coinbase_client_mock, order_response):
    strategy = SimplePriceOscillationStrategy.objects.create()
    order_chain = OrderChainFactory(strategy=strategy)
    active_linked_order = LinkedOrderFactory(
        status=OrderStatus.OPEN.value, order_chain=order_chain, order_id="9456f388-67a9-4316-bad1-330c5353804f"
    )
    coinbase_client_mock.get_order.return_value = order_response
    strategy.update_active_orders(client=coinbase_client_mock)
    active_linked_order.refresh_from_db()
    assert active_linked_order.status == order_response["status"]
    assert active_linked_order.settled == order_response["settled"]


def test_update_accrued_fees():
    strategy = SimplePriceOscillationStrategy.objects.create()
    assert strategy.accrued_fees == 0.0
    strategy.update_accrued_fees(fees=[0.5, 0.25, 0.25])
    assert strategy.accrued_fees == 1.0
    strategy.update_accrued_fees(fees=[2.1])
    assert strategy.accrued_fees == 3.1


@mark.parametrize(
    "previous_price, order_side, expected",
    [(10000.0, OrderSide.BUY.value, 9900.0), (10000.0, OrderSide.SELL.value, 10100.0)],
)
def test_calculate_order_price(previous_price, order_side, expected):
    strategy = SimplePriceOscillationStrategy(buy_percentage_difference=1.0, sell_percentage_difference=1.0)
    assert strategy.calculate_order_price(previous_price, order_side) == expected


@mark.parametrize(
    "previous_order_side, new_order_side, new_order_stop_type, new_order_price, new_order_size",
    [
        (OrderSide.SELL.value, OrderSide.BUY.value, StopOrderType.ENTRY.value, 9900.0, 0.01003562),
        (OrderSide.BUY.value, OrderSide.SELL.value, StopOrderType.LOSS.value, 10100.00, 0.00997506),
    ],
)
def test_create_new_api_order(
    coinbase_client_mock, previous_order_side, new_order_side, new_order_stop_type, new_order_price, new_order_size
):
    strategy = SimplePriceOscillationStrategy.objects.create(
        buy_percentage_difference=1.0, sell_percentage_difference=1.0
    )
    order_chain = OrderChainFactory(strategy=strategy)
    linked_order = LinkedOrderFactory(
        status=OrderStatus.SETTLED.value,
        order_chain=order_chain,
        order_id="9456f388-67a9-4316-bad1-330c5353804f",
        side=previous_order_side,
        price=10000.0,
        size=0.00997506,
        filled_size=0.00997506,
        executed_value=99.7506,
        fill_fees=0.1496259,
    )
    strategy.create_new_api_order(client=coinbase_client_mock, previous_order=linked_order)
    coinbase_client_mock.place_stop_order.assert_called_with(
        product_id=linked_order.product_id,
        side=new_order_side,
        stop_type=new_order_stop_type,
        price=new_order_price,
        size=new_order_size,
        overdraft_enabled=False,
    )


def test_create_new_api_order_no_previous_order(coinbase_client_mock):
    strategy = SimplePriceOscillationStrategy.objects.create(
        buy_percentage_difference=1.0, sell_percentage_difference=1.0, starting_funds=110.0, starting_price=10000.0
    )
    strategy.create_new_api_order(client=coinbase_client_mock)
    coinbase_client_mock.place_stop_order.assert_called_with(
        product_id=strategy.product_id,
        side=OrderSide.BUY.value,
        stop_type=StopOrderType.ENTRY.value,
        price=strategy.starting_price,
        size=0.01097257,
        overdraft_enabled=False,
    )


def test_create_new_order_no_previous_order(coinbase_client_mock, order_response):
    with patch(
        "coppermint.coinbase_pro.models.SimplePriceOscillationStrategy.create_new_api_order",
        return_value=order_response,
    ):
        strategy = SimplePriceOscillationStrategy.objects.create(
            buy_percentage_difference=1.0, sell_percentage_difference=1.0, starting_funds=110.0, starting_price=10000.0
        )
        strategy.create_new_order(coinbase_client_mock)
        assert strategy.active_orders[0].order_id == order_response["id"]
        assert strategy.active_orders[0].price == float(order_response["price"])
        assert strategy.active_orders[0].size == float(order_response["size"])
        assert strategy.active_orders[0].order_type == order_response["type"]
        assert strategy.active_orders[0].side == order_response["side"]
        assert strategy.active_orders[0].stop_type == order_response["stop"]
        assert strategy.active_orders[0].index == 1


def test_evaluate_orders(coinbase_client_mock):
    strategy = SimplePriceOscillationStrategy.objects.create()
    order_chain = OrderChainFactory(strategy=strategy)
    updated_filled_order = LinkedOrderFactory(status=OrderStatus.DONE.value, order_chain=order_chain)
    updated_open_order = LinkedOrderFactory(status=OrderStatus.OPEN.value, order_chain=order_chain)
    with patch("coppermint.coinbase_pro.models.SimplePriceOscillationStrategy.create_new_order") as create_order_mock:
        strategy.evaluate_orders(client=coinbase_client_mock, orders=[updated_filled_order, updated_open_order])
        create_order_mock.assert_called_once_with(client=coinbase_client_mock, previous_order=updated_filled_order)
