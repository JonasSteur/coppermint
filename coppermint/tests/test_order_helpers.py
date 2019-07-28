from pytest import mark

from coppermint.order_helpers import neutralize_fee, calculate_fee, calculate_buy_order_size


@mark.parametrize(
    "gross_amount, fee_percentage, decimal_places, expected",
    [
        (100.0, 0.25, None, 99.75062344139651),
        (100.0, 1.0, None, 99.00990099009901),
        (100.0, 0.25, 8, 99.75062344),
        (100.0, 1.0, 2, 99.01),
    ],
)
def test_neutralize_fee(gross_amount, fee_percentage, decimal_places, expected):
    assert neutralize_fee(gross_amount, fee_percentage, decimal_places) == expected


@mark.parametrize("amount, fee_percentage, expected", [(100.0, 0.25, 0.25), (999.0, 0.12, 1.1988), (100.0, 75.0, 75.0)])
def test_calculate_fee(amount, fee_percentage, expected):
    assert calculate_fee(amount, fee_percentage) == expected


@mark.parametrize("funds_to_use, order_price, expected", [(100.0, 10000.0, 0.00997506), (999.0, 10000.0, 0.09965087)])
def test_calculate_buy_order_size(funds_to_use, order_price, expected):
    assert calculate_buy_order_size(funds_to_use=funds_to_use, order_price=order_price, fee_percentage=0.25) == expected
