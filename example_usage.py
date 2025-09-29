#!/usr/bin/env python3
"""
Example showing how to use the new BuyXGetYFreeDiscount strategy
"""

from domain.pricing import (
    LineItem, 
    compute_subtotal, 
    BuyXGetYFreeDiscount, 
    PercentageDiscount,
    CompositeStrategy
)

def main():
    # Create some sample items
    items = [
        LineItem("SHIRT", qty=6, unit_price=25.0),  # 6 shirts at $25 each
        LineItem("JEANS", qty=4, unit_price=50.0),  # 4 jeans at $50 each
        LineItem("SHOES", qty=2, unit_price=80.0),  # 2 shoes at $80 each
    ]
    
    # Calculate subtotal
    subtotal = compute_subtotal(items)
    print(f"Original subtotal: ${subtotal}")
    print(f"Items: {items}")
    print()
    
    # Example 1: Buy 2 Get 1 Free on SHIRT
    print("=== Example 1: Buy 2 Get 1 Free on SHIRT ===")
    buy2get1_strategy = BuyXGetYFreeDiscount(sku="SHIRT", buy_quantity=2, free_quantity=1)
    new_total = buy2get1_strategy.apply(subtotal, items)
    print(f"Strategy: Buy 2 SHIRT, Get 1 Free")
    print(f"6 shirts = 2 complete sets of (buy 2 + get 1 free)")
    print(f"Discount: 2 free shirts × $25 = $50")
    print(f"New total: ${new_total} (saved ${subtotal - new_total})")
    print()
    
    # Example 2: Buy 3 Get 1 Free on JEANS
    print("=== Example 2: Buy 3 Get 1 Free on JEANS ===")
    buy3get1_strategy = BuyXGetYFreeDiscount(sku="JEANS", buy_quantity=3, free_quantity=1)
    new_total = buy3get1_strategy.apply(subtotal, items)
    print(f"Strategy: Buy 3 JEANS, Get 1 Free")
    print(f"4 jeans = 1 complete set of (buy 3 + get 1 free)")
    print(f"Discount: 1 free jean × $50 = $50")
    print(f"New total: ${new_total} (saved ${subtotal - new_total})")
    print()
    
    # Example 3: Combining strategies
    print("=== Example 3: Combining Strategies ===")
    combined_strategy = CompositeStrategy([
        BuyXGetYFreeDiscount(sku="SHIRT", buy_quantity=2, free_quantity=1),  # Buy 2 Get 1 Free on shirts
        PercentageDiscount(10)  # Then apply 10% off everything
    ])
    new_total = combined_strategy.apply(subtotal, items)
    print(f"Strategy: Buy 2 Get 1 Free on SHIRT + 10% off total")
    print(f"Step 1: Buy 2 Get 1 Free saves $50 → ${subtotal - 50}")
    print(f"Step 2: 10% off ${subtotal - 50} = ${(subtotal - 50) * 0.9}")
    print(f"Final total: ${new_total} (saved ${subtotal - new_total})")

if __name__ == "__main__":
    main()