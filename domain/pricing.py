from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
import random


@dataclass(frozen=True)
class LineItem:
    sku: str
    qty: int
    unit_price: float


class PricingStrategy(ABC):
    @abstractmethod
    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        """Return the final total given a subtotal and cart items."""
        raise NotImplementedError


class NoDiscount(PricingStrategy):
    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        return round(subtotal, 2)


class PercentageDiscount(PricingStrategy):
    def __init__(self, percent: float) -> None:
        assert 0 <= percent <= 100, "percent must be between 0 and 100"
        self.percent = percent

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        discount = subtotal * (self.percent / 100.0)
        return round(subtotal - discount, 2)


class BulkItemDiscount(PricingStrategy):
    """If any single item's quantity >= threshold, apply a per-item discount for that SKU."""
    def __init__(self, sku: str, threshold: int, per_item_off: float) -> None:
        self.sku = sku
        self.threshold = threshold
        self.per_item_off = per_item_off

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        total = subtotal
        for it in items:
            if it.sku == self.sku and it.qty >= self.threshold:
                total -= self.per_item_off * it.qty
        return round(max(total, 0.0), 2)


class CompositeStrategy(PricingStrategy):
    """Compose multiple strategies; apply in order."""
    def __init__(self, strategies: list[PricingStrategy]) -> None:
        self.strategies = strategies

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        total = subtotal
        for strat in self.strategies:
            total = strat.apply(total, items)
        return round(total, 2)


class LuckyItemDiscount(PricingStrategy):
    """Randomly selects one item in the cart and makes it free."""
    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        if not items:
            return round(subtotal, 2)
        lucky_index = random.randint(0, len(items) - 1)
        lucky_item = items[lucky_index]
        lucky_item_total = lucky_item.unit_price * lucky_item.qty
        total = subtotal - lucky_item_total
        return round(max(total, 0.0), 2)

def compute_subtotal(items: list[LineItem]) -> float:
    return round(sum(it.unit_price * it.qty for it in items), 2)
