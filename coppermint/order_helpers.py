from typing import Optional


def calculate_fee(amount: float, fee_percentage: float):
    return (amount / 100) * fee_percentage


def neutralize_fee(gross_amount: float, fee_percentage: float, decimal_places: Optional[int] = None) -> float:
    """
    Calculates the maximum for a given gross amount that can be used for an order considering given fee percentage
    eg:
    If an order for EUR 100 would require a fee of 0.25 % to be paid the actual order cost would be 100.25
    In case we only want to spent max EUR 100 we would need to know the Net amount for an order.

    gross = net + (net/100 * fee_percentage)
    net + (net * fee_percentage)/100 = gross
    net * (fee_percentage)/100 + 1) = gross
    net * (fee_percentage/100 + 1) / (fee_percentage/100 + 1) = gross / (fee_percentage/100 + 1)
    net = gross / (fee_percentage/100 + 1)
    net = (gross * 100) / (fee_percentage + 100)

    """
    result = (100 * gross_amount) / (fee_percentage + 100)
    if decimal_places:
        return round(result, decimal_places)
    return result


def calculate_buy_order_size(funds_to_use: float, order_price: float, fee_percentage: float):
    """
    Calculates amount of crypto to buy for given max founds taking fees into account
    """
    net_funds_to_use = neutralize_fee(gross_amount=funds_to_use, fee_percentage=fee_percentage)
    return round(net_funds_to_use / order_price, 8)
