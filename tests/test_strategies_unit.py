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


def test_buy_x_get_y_free_discount():
    # Test "Buy 2, Get 1 Free" on product A
    items = [
        LineItem("A", qty=6, unit_price=10.0),  # 6 items at $10 each = $60
        LineItem("B", qty=2, unit_price=5.0),   # 2 items at $5 each = $10
    ]  # subtotal = 70
    
    subtotal = compute_subtotal(items)
    
    # Buy 2 Get 1 Free on product A
    # 6 items = 2 complete sets of (2 buy + 1 free)
    # So we get 2 free items worth $20 off
    strategy = BuyXGetYFreeDiscount(sku="A", buy_quantity=2, free_quantity=1)
    total = strategy.apply(subtotal, items)
    
    assert total == 50.0  # 70 - 20 = 50


def test_buy_x_get_y_free_no_complete_sets():
    # Test when we don't have enough items for a complete set
    items = [LineItem("A", qty=2, unit_price=10.0)]  # Only 2 items
    subtotal = compute_subtotal(items)  # 20
    
    # Buy 3 Get 1 Free - we only have 2 items, so no discount applies
    strategy = BuyXGetYFreeDiscount(sku="A", buy_quantity=3, free_quantity=1)
    total = strategy.apply(subtotal, items)
    
    assert total == 20.0  # No discount applied
