# New Pricing Strategy: BuyXGetYFreeDiscount

## What is the Strategy Pattern?

The **Strategy Pattern** lets you define different ways to do the same task and switch between them easily. Think of it like having different discount calculators - each one knows how to calculate a specific type of discount.

## How Our Pricing Strategies Work

1. **All strategies implement the same interface**: `PricingStrategy.apply(subtotal, items)`
2. **Each strategy calculates discounts differently**
3. **You can combine strategies** using `CompositeStrategy`

## Existing Strategies

- `NoDiscount`: No discount applied
- `PercentageDiscount`: Take X% off the total 
- `BulkItemDiscount`: If you buy enough of an item, get money off per item
- `CompositeStrategy`: Apply multiple strategies in order

## New Strategy: BuyXGetYFreeDiscount

### What it does:
Implements "Buy X, Get Y Free" offers (like "Buy 2, Get 1 Free")

### How it works:
1. Looks for items with the specified SKU
2. Calculates how many complete sets of (X + Y) items you have
3. Gives you Y free items for each complete set
4. Reduces the total by (free items × unit price)

### Example:
- **Offer**: Buy 2 shirts, get 1 free
- **You have**: 6 shirts at $25 each
- **Calculation**: 6 shirts ÷ 3 (2 buy + 1 free) = 2 complete sets
- **Discount**: 2 free shirts × $25 = $50 off

### Code:
```python
# Create the strategy
strategy = BuyXGetYFreeDiscount(sku="SHIRT", buy_quantity=2, free_quantity=1)

# Apply it to your cart
discounted_total = strategy.apply(original_total, items)
```

## Why This is Good Design

1. **Easy to add new strategies** - just create a new class that implements `PricingStrategy`
2. **Easy to test** - each strategy is independent 
3. **Easy to combine** - use `CompositeStrategy` to apply multiple discounts
4. **Easy to change** - swap strategies without changing other code
5. **Follows Single Responsibility** - each class has one job

## Key Files Modified

- `domain/pricing.py` - Added the new `BuyXGetYFreeDiscount` class
- `tests/test_strategies_unit.py` - Added tests for the new strategy
- `example_usage.py` - Created examples showing how to use it

The new strategy integrates seamlessly with the existing code and follows the same pattern as other strategies!