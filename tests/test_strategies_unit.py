import pytest
from domain.pricing import LineItem, compute_subtotal, NoDiscount, PercentageDiscount, BulkItemDiscount, BuyOneGetOne, CompositeStrategy


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


def test_buy_one_get_one_discount():
    items = [
        LineItem("A", qty=3, unit_price=10.0),  # 3 items, should get 1 free
        LineItem("B", qty=1, unit_price=5.0),   # 1 item, no BOGO
    ]  # subtotal = 35
    subtotal = compute_subtotal(items)
    total = BuyOneGetOne(sku="A").apply(subtotal, items)
    # 3 items of A: 1 free (10.0 off) => 35 - 10 = 25
    assert total == 25.0


def test_buy_one_get_one_even_quantities():
    items = [
        LineItem("A", qty=4, unit_price=10.0),  # 4 items, should get 2 free
        LineItem("B", qty=2, unit_price=5.0),   # 2 items, should get 1 free
    ]  # subtotal = 50
    subtotal = compute_subtotal(items)
    total = BuyOneGetOne(sku="A").apply(subtotal, items)
    # 4 items of A: 2 free (20.0 off) => 50 - 20 = 30
    assert total == 30.0


def test_buy_one_get_one_odd_quantities():
    items = [
        LineItem("A", qty=5, unit_price=10.0),  # 5 items, should get 2 free
    ]  # subtotal = 50
    subtotal = compute_subtotal(items)
    total = BuyOneGetOne(sku="A").apply(subtotal, items)
    # 5 items of A: 2 free (20.0 off) => 50 - 20 = 30
    assert total == 30.0


def test_buy_one_get_one_no_match():
    items = [
        LineItem("A", qty=3, unit_price=10.0),  # 3 items
    ]  # subtotal = 30
    subtotal = compute_subtotal(items)
    total = BuyOneGetOne(sku="B").apply(subtotal, items)  # Different SKU
    # No discount applied
    assert total == 30.0


def test_composite_applies_in_order():
    items = sample_items()  # subtotal 35
    subtotal = compute_subtotal(items)
    # First 10% off => 31.5, then bulk: - (5 * 0.5) = -2.5 => 29.0
    comp = CompositeStrategy([PercentageDiscount(10), BulkItemDiscount("B", 5, 0.5)])
    assert comp.apply(subtotal, items) == 29.0
