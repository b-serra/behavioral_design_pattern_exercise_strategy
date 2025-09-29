from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class LineItem:
    sku: str
    qty: int
    unit_price: float


class PricingStrategy(ABC):
    # Common interface for all pricing strategies.
    @abstractmethod
    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        """Return the final total after applying this pricing strategy.

        Implementations should not mutate inputs and should round to 2 decimals.
        """
        raise NotImplementedError


class NoDiscount(PricingStrategy):
    # TODO: Implement a strategy that returns the original value without changes
    pass


class PercentageDiscount(PricingStrategy):
    def __init__(self, percent: float) -> None:
        if percent < 0 or percent > 100:
            raise ValueError("percent must be between 0 and 100")
        self._percent = float(percent)

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        discount = subtotal * (self._percent / 100.0)
        return round(subtotal - discount, 2)

class BulkItemDiscount(PricingStrategy):
    """If any single item's quantity >= threshold, apply a per-item discount for that SKU."""
    def __init__(self, sku: str, threshold: int, per_item_off: float) -> None:
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        if per_item_off < 0:
            raise ValueError("per_item_off must be non-negative")
        self._sku = sku
        self._threshold = threshold
        self._per_item_off = float(per_item_off)

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        reduction = 0.0
        for item in items:
            if item.sku == self._sku and item.qty >= self._threshold:
                reduction += self._per_item_off * item.qty
        return round(max(0.0, subtotal - reduction), 2)


class CompositeStrategy(PricingStrategy):
    """Compose multiple strategies; apply in order."""
    def __init__(self, strategies: list[PricingStrategy]) -> None:
        self._strategies = list(strategies)

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        total = subtotal
        for strategy in self._strategies:
            total = strategy.apply(total, items)
        return round(total, 2)


class SubtotalThresholdPercentDiscount(PricingStrategy):
    """Apply percent off only if subtotal >= threshold."""
    def __init__(self, threshold: float, percent: float) -> None:
        if threshold < 0:
            raise ValueError("threshold must be non-negative")
        if percent < 0 or percent > 100:
            raise ValueError("percent must be between 0 and 100")
        self._threshold = float(threshold)
        self._percent = float(percent)

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        if subtotal >= self._threshold:
            discount = subtotal * (self._percent / 100.0)
            return round(subtotal - discount, 2)
        return round(subtotal, 2)


def compute_subtotal(items: list[LineItem]) -> float:
    return round(sum(it.unit_price * it.qty for it in items), 2)
