from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class LineItem:
    sku: str
    qty: int
    unit_price: float


class PricingStrategy(ABC):
    # TODO: Define the common interface for all pricing strategies.
    # This should include a method that takes pricing parameters and returns a calculated value.
    @abstractmethod
    def apply(self, amount: float, items: list[LineItem]) -> float:
        pass



class NoDiscount(PricingStrategy):
    # TODO: Implement a strategy that returns the original value without changes
    def apply(self, amount: float, items: list[LineItem]) -> float:
        return amount


class PercentageDiscount(PricingStrategy):
    def __init__(self, percent: float) -> None:
        # TODO: Store the percentage value and validate it's in the correct range
        self.percent = percent

    def apply(self, amount: float, items: list[LineItem]) -> float:
        return amount * (1 - self.percent / 100)


class BulkItemDiscount(PricingStrategy):
    """If any single item's quantity >= threshold, apply a per-item discount for that SKU."""
    def __init__(self, sku: str, threshold: int, per_item_off: float) -> None:
        # TODO: Store the parameters needed to identify items and calculate reductions
        self.sku = sku
        self.threshold = threshold
        self.per_item_off = per_item_off

    def apply(self, amount: float, items: list[LineItem]) -> float:
        # Find the item with matching SKU and check if it meets threshold
        discount = 0.0
        for item in items:
            if item.sku == self.sku and item.qty >= self.threshold:
                discount = item.qty * self.per_item_off
                break
        return amount - discount


class CompositeStrategy(PricingStrategy):
    """Compose multiple strategies; apply in order."""
    def __init__(self, strategies: list[PricingStrategy]) -> None:
        # TODO: Store the collection of strategies to be applied sequentially
        self.strategies = strategies

    def apply(self, amount: float, items: list[LineItem]) -> float:
        # TODO: Implement method that applies each strategy in sequence, using the output of one as input to the next
        for strategy in self.strategies:
            amount = strategy.apply(amount, items)
        return amount


def compute_subtotal(items: list[LineItem]) -> float:
    return round(sum(it.unit_price * it.qty for it in items), 2)
