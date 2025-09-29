import pytest
from domain.pricing import LineItem, compute_subtotal, NoDiscount, PercentageDiscount, BulkItemDiscount, CompositeStrategy, BuyXGetYFreeDiscount


def sample_items():
    return [
        LineItem("A", qty=2, unit_price=10.0),  # 20
        LineItem("B", qty=5, unit_price=3.0),   # 15
    ]  # subtotal = 35


def test_no_discount():
    items = sample_items()
    subtotal = compute_subtotal(items)
    total = NoDiscount().apply(subtotal, items)
    assert total == 35.00


@pytest.mark.parametrize("percent, expected", [(10, 31.5), (0, 35.0), (100, 0.0)])
def test_percentage_discount(percent, expected):
    items = sample_items()
    subtotal = compute_subtotal(items)
    total = PercentageDiscount(percent).apply(subtotal, items)
    assert total == expected


def test_bulk_item_discount_applies_per_item_when_threshold_met():
    items = sample_items()  # B has qty 5
    subtotal = compute_subtotal(items)  # 35
    total = BulkItemDiscount(sku="B", threshold=5, per_item_off=0.5).apply(subtotal, items)
    # 5 items of B get 0.5 off each => 2.5 off
    assert total == 32.5


def test_composite_applies_in_order():
    items = sample_items()  # subtotal 35
    subtotal = compute_subtotal(items)
    # First 10% off => 31.5, then bulk: - (5 * 0.5) = -2.5 => 29.0
    comp = CompositeStrategy([PercentageDiscount(10), BulkItemDiscount("B", 5, 0.5)])
    assert comp.apply(subtotal, items) == 29.0


def test_buyxgetyfree_discount():
    items = [LineItem("C", qty=7, unit_price=4.0)]  # 7 items, $4 each, subtotal = 28
    subtotal = compute_subtotal(items)
    # Buy 2 get 1 free: for every 3 items, 1 is free (so 2 paid, 1 free)
    # 7 items: 2 groups of 3 (2*1 free = 2 free), 1 leftover (not enough for another free)
    # So 2 free items, discount = 2*4 = 8, total = 28-8 = 20
    total = BuyXGetYFreeDiscount("C", buy_x=2, get_y=1).apply(subtotal, items)
    assert total == 20.0
