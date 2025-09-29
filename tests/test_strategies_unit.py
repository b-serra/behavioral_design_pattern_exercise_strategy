import pytest
from domain.pricing import LineItem, compute_subtotal, NoDiscount, PercentageDiscount, BulkItemDiscount, CompositeStrategy, TieredDiscount


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


def test_tiered_discount_single_tier():
    items = sample_items()  # subtotal 35
    subtotal = compute_subtotal(items)
    # Single tier: 5% off for >= $30
    tiered = TieredDiscount([(30.0, 5.0)])
    total = tiered.apply(subtotal, items)
    assert total == 33.25  # 35 - (35 * 0.05) = 35 - 1.75 = 33.25


def test_tiered_discount_no_tier_matched():
    items = sample_items()  # subtotal 35
    subtotal = compute_subtotal(items)
    # No tier matched (threshold higher than subtotal)
    tiered = TieredDiscount([(50.0, 10.0)])
    total = tiered.apply(subtotal, items)
    assert total == 35.00  # No discount applied


def test_tiered_discount_multiple_tiers():
    items = [
        LineItem("A", qty=10, unit_price=15.0),  # 150
        LineItem("B", qty=5, unit_price=10.0),   # 50
    ]  # subtotal = 200
    
    subtotal = compute_subtotal(items)
    # Multiple tiers: 5% for >=50, 10% for >=100, 15% for >=200
    tiered = TieredDiscount([(50.0, 5.0), (100.0, 10.0), (200.0, 15.0)])
    total = tiered.apply(subtotal, items)
    assert total == 170.00  # 200 - (200 * 0.15) = 200 - 30 = 170


def test_tiered_discount_uses_highest_applicable_tier():
    items = [
        LineItem("A", qty=8, unit_price=10.0),  # 80
    ]  # subtotal = 80
    
    subtotal = compute_subtotal(items)
    # Should use 10% tier (not 5%) since 80 >= 50 and 80 >= 100
    tiered = TieredDiscount([(50.0, 5.0), (100.0, 10.0)])
    total = tiered.apply(subtotal, items)
    assert total == 76.00  # 80 - (80 * 0.05) = 80 - 4 = 76


def test_tiered_discount_unordered_tiers():
    items = sample_items()  # subtotal 35
    subtotal = compute_subtotal(items)
    # Tiers provided out of order - should be sorted internally
    tiered = TieredDiscount([(100.0, 15.0), (50.0, 10.0), (0.0, 5.0)])
    total = tiered.apply(subtotal, items)
    assert total == 33.25  # 35 - (35 * 0.05) = 35 - 1.75 = 33.25
