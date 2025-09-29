import pytest
from domain.pricing import LineItem, compute_subtotal, NoDiscount, PercentageDiscount, BulkItemDiscount, CompositeStrategy
from domain.pricing import BuyXGetYFree


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


def test_buy_x_get_y_free_single_group():
    items = [
        LineItem("C", qty=3, unit_price=5.0),  # 15
    ]
    subtotal = compute_subtotal(items)
    # Buy 2 get 1 free on C => one free item => discount 5.0 => total 10.0
    strat = BuyXGetYFree(sku="C", x=2, y=1)
    assert strat.apply(subtotal, items) == 10.0


def test_buy_x_get_y_free_multiple_groups_and_remainder():
    items = [
        LineItem("C", qty=7, unit_price=2.0),  # 14
    ]
    subtotal = compute_subtotal(items)
    # Buy 2 get 1 free => group size 3, groups = 7 // 3 = 2 => free_items = 2*1 = 2
    # discount = 2 * 2.0 = 4.0 => total = 10.0
    strat = BuyXGetYFree(sku="C", x=2, y=1)
    assert strat.apply(subtotal, items) == 10.0
