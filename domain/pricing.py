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
    def apply(self, total: float, items: list[LineItem]) -> float:
        pass


class NoDiscount(PricingStrategy):
    # TODO: Implement a strategy that returns the original value without changes
    def apply(self, total: float, items: list[LineItem]) -> float:
        return total


class PercentageDiscount(PricingStrategy):
    def __init__(self, percent: float) -> None:
        # TODO: Store the percentage value and validate it's in the correct range
        if percent < 0 or percent > 100:
            raise ValueError("Percentage must be between 0 and 100")
        self.percent = percent

    # TODO: Implement the main calculation method that reduces the input by a percentage
    def apply(self, total: float, items: list[LineItem]) -> float:
        return (100 - self.percent) / 100 * total


class BulkItemDiscount(PricingStrategy):
    """If any single item's quantity >= threshold, apply a per-item discount for that SKU."""
    def __init__(self, sku: str, threshold: int, per_item_off: float) -> None:
        # TODO: Store the parameters needed to identify items and calculate reductions
        self.sku = sku
        self.threshold = threshold
        self.per_item_off = per_item_off

    # TODO: Implement logic to iterate through items and apply reductions based on quantity thresholds
    def apply(self, total: float, items: list[LineItem]) -> float:
        for item in items:
            if item.sku == self.sku and item.qty >= self.threshold:
                total -= self.per_item_off * item.qty
        return total


class CompositeStrategy(PricingStrategy):
    """Compose multiple strategies; apply in order."""
    def __init__(self, strategies: list[PricingStrategy]) -> None:
        # TODO: Store the collection of strategies to be applied sequentially
        self.strategies = strategies

    # TODO: Implement method that applies each strategy in sequence, using the output of one as input to the next
    def apply(self, total: float, items: list[LineItem]) -> float:
        for strategy in self.strategies:
            total = strategy.apply(total, items)
        return total


def compute_subtotal(items: list[LineItem]) -> float:
    return round(sum(it.unit_price * it.qty for it in items), 2)
