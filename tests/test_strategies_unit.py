import pytest
from domain.pricing import (
    LineItem, compute_subtotal, NoDiscount, PercentageDiscount, BulkItemDiscount, CompositeStrategy,
    TieredDiscount, BuyXGetYFree, CategoryDiscount, LoyaltyPointsDiscount, 
    QuantityBasedDiscount, HappyHourDiscount
)


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


def test_tiered_discount():
    items = sample_items()  # subtotal 35
    subtotal = compute_subtotal(items)
    
    # Test basic tier
    tiers = [(30, 10), (50, 20)]  # 10% off at $30, 20% off at $50
    strategy = TieredDiscount(tiers)
    total = strategy.apply(subtotal, items)
    assert total == 31.5  # 35 * 0.9
    
    # Test higher tier with larger cart
    items_large = [LineItem("A", qty=10, unit_price=10.0)]  # 100
    subtotal_large = compute_subtotal(items_large)
    total_large = strategy.apply(subtotal_large, items_large)
    assert total_large == 80.0  # 100 * 0.8


def test_buy_x_get_y_free():
    # Buy 2 get 1 free on item A
    items = [LineItem("A", qty=3, unit_price=10.0)]  # 30
    subtotal = compute_subtotal(items)
    strategy = BuyXGetYFree("A", buy_qty=2, free_qty=1)
    total = strategy.apply(subtotal, items)
    assert total == 20.0  # Pay for 2, get 1 free
    
    # Test with qty that doesn't perfectly fit promotion
    items2 = [LineItem("A", qty=5, unit_price=10.0)]  # 50
    subtotal2 = compute_subtotal(items2)
    total2 = strategy.apply(subtotal2, items2)
    assert total2 == 30.0  # Pay for 3, get 2 free


def test_category_discount():
    items = [
        LineItem("BOOK001", qty=2, unit_price=15.0),  # 30 - books category
        LineItem("ELEC001", qty=1, unit_price=100.0),  # 100 - electronics
    ]  # subtotal = 130
    subtotal = compute_subtotal(items)
    
    # 20% off books (BOOK prefix)
    strategy = CategoryDiscount("BOOK", 20.0)
    total = strategy.apply(subtotal, items)
    assert total == 124.0  # 130 - (30 * 0.2)


def test_loyalty_points_discount():
    items = sample_items()  # subtotal 35
    subtotal = compute_subtotal(items)
    
    # 1000 points = $10 discount
    strategy = LoyaltyPointsDiscount(points_available=1000, points_per_dollar=100)
    total = strategy.apply(subtotal, items)
    assert total == 25.0  # 35 - 10
    
    # Not enough points to cover full subtotal
    strategy2 = LoyaltyPointsDiscount(points_available=500, points_per_dollar=100)
    total2 = strategy2.apply(subtotal, items)
    assert total2 == 30.0  # 35 - 5


def test_quantity_based_discount():
    items = [
        LineItem("A", qty=3, unit_price=10.0),
        LineItem("B", qty=7, unit_price=5.0),
    ]  # 10 total items, subtotal = 65
    subtotal = compute_subtotal(items)
    
    tiers = [(5, 5), (10, 10), (20, 15)]  # 5% at 5 items, 10% at 10 items, 15% at 20 items
    strategy = QuantityBasedDiscount(tiers)
    total = strategy.apply(subtotal, items)
    assert total == 58.5  # 65 * 0.9 (10% off for 10 items)


def test_happy_hour_discount():
    items = sample_items()  # subtotal 35
    subtotal = compute_subtotal(items)
    
    # Mock current hour to be within happy hour
    strategy = HappyHourDiscount(discount_percent=25.0, start_hour=14, end_hour=16)
    strategy._current_hour = 15  # 3 PM - within happy hour
    total = strategy.apply(subtotal, items)
    assert total == 26.25  # 35 * 0.75
    
    # Mock current hour to be outside happy hour
    strategy._current_hour = 10  # 10 AM - outside happy hour
    total_no_discount = strategy.apply(subtotal, items)
    assert total_no_discount == 35.0  # No discount


def test_creative_composite_strategies():
    """Test combining multiple creative strategies."""
    items = [
        LineItem("BOOK001", qty=6, unit_price=10.0),  # Books category
        LineItem("ELEC001", qty=4, unit_price=25.0),  # Electronics
    ]  # subtotal = 160, 10 total items
    subtotal = compute_subtotal(items)
    
    # Combine category discount + quantity discount
    strategies = [
        CategoryDiscount("BOOK", 15.0),  # 15% off books
        QuantityBasedDiscount([(10, 5)])  # 5% off for 10+ items
    ]
    composite = CompositeStrategy(strategies)
    
    # First: 160 - (60 * 0.15) = 160 - 9 = 151
    # Then: 151 * 0.95 = 143.45
    total = composite.apply(subtotal, items)
    assert total == 143.45
