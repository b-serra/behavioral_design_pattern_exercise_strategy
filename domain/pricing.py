from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class LineItem:
    sku: str
    qty: int
    unit_price: float


class PricingStrategy(ABC):
    @abstractmethod
    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        pass
    # TODO: Define the common interface for all pricing strategies.
    # This should include a method that takes pricing parameters and returns a calculated value.
     


class NoDiscount(PricingStrategy):
    # TODO: Implement a strategy that returns the original value without changes
    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        return subtotal
  


class PercentageDiscount(PricingStrategy):
    def __init__(self, percent: float) -> None:
        # TODO: Store the percentage value and validate it's in the correct range
        if not (0 <= percent <= 100):
            raise ValueError("Percentage must be between 0 and 100.")
        self.percent = percent

    # TODO: Implement the main calculation method that reduces the input by a percentage
    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        return round(subtotal*((100 - self.percent)/100), 2)


class BulkItemDiscount(PricingStrategy):
    """If any single item's quantity >= threshold, apply a per-item discount for that SKU."""
    def __init__(self, sku: str, threshold: int, per_item_off: float) -> None:
        # TODO: Store the parameters needed to identify items and calculate reductions
        self.sku = sku
        self.threshold = threshold
        self.per_item_off = per_item_off

    # TODO: Implement logic to iterate through items and apply reductions based on quantity thresholds
    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        total_discount = 0.0
        for item in items:
            if item.sku == self.sku and item.qty >= self.threshold:
                total_discount += item.qty * self.per_item_off
        return round(subtotal - total_discount, 2)

class BuyXGetYFreeDiscount(PricingStrategy):
    """Buy X items of a specific SKU, get Y items free (pay for X, get X+Y total)"""
    def __init__(self, sku: str, buy_quantity: int, free_quantity: int) -> None:
        # Store the parameters for the buy X get Y free offer
        self.sku = sku
        self.buy_quantity = buy_quantity
        self.free_quantity = free_quantity
        
        if buy_quantity <= 0 or free_quantity <= 0:
            raise ValueError("Buy and free quantities must be positive")

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        total_discount = 0.0
        
        for item in items:
            if item.sku == self.sku:
                # Calculate how many complete "buy X get Y free" sets we have
                complete_sets = item.qty // (self.buy_quantity + self.free_quantity)
                
                # Calculate discount: free items * unit price * number of complete sets
                free_items_discount = complete_sets * self.free_quantity * item.unit_price
                total_discount += free_items_discount
        
        return round(subtotal - total_discount, 2)


class CompositeStrategy(PricingStrategy):
    """Compose multiple strategies; apply in order."""
    def __init__(self, strategies: list[PricingStrategy]) -> None:
        # TODO: Store the collection of strategies to be applied sequentially
        self.strategies = strategies

    # TODO: Implement method that applies each strategy in sequence, using the output of one as input to the next
    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        current_total = subtotal
        for strategy in self.strategies:
            current_total = strategy.apply(current_total, items)
        return current_total

def compute_subtotal(items: list[LineItem]) -> float:
    return round(sum(it.unit_price * it.qty for it in items), 2)
