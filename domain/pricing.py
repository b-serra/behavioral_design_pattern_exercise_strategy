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
        """Return the total after applying this pricing strategy."""
        raise NotImplementedError


class NoDiscount(PricingStrategy):
    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        return round(subtotal, 2)


class PercentageDiscount(PricingStrategy):
    def __init__(self, percent: float) -> None:
        if percent < 0 or percent > 100:
            raise ValueError("percent must be between 0 and 100")
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
        total_off = 0.0
        for it in items:
            if it.sku == self.sku and it.qty >= self.threshold:
                total_off += it.qty * self.per_item_off
        return round(subtotal - total_off, 2)


class CompositeStrategy(PricingStrategy):
    """Compose multiple strategies; apply in order."""
    def __init__(self, strategies: list[PricingStrategy]) -> None:
        self.strategies = strategies

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        running = subtotal
        for s in self.strategies:
            running = s.apply(running, items)
        return round(running, 2)


class ThresholdSubtotalDiscount(PricingStrategy):
    """If subtotal >= threshold, subtract a fixed amount."""
    def __init__(self, threshold_total: float, off_amount: float) -> None:
        if threshold_total < 0 or off_amount < 0:
            raise ValueError("threshold_total and off_amount must be non-negative")
        self.threshold_total = threshold_total
        self.off_amount = off_amount

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        if subtotal >= self.threshold_total:
            return round(subtotal - self.off_amount, 2)
        return round(subtotal, 2)


def compute_subtotal(items: list[LineItem]) -> float:
    return round(sum(it.unit_price * it.qty for it in items), 2)
