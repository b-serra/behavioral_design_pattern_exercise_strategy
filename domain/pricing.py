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


class TieredDiscount(PricingStrategy):
    """Apply different discount percentages based on subtotal amount tiers."""
    def __init__(self, tiers: list[tuple[float, float]]) -> None:
        """Initialize with tiers list of (threshold, discount_percent).
        
        Args:
            tiers: List of (threshold, discount_percent) tuples. The first threshold
                  that the subtotal meets or exceeds determines the discount rate.
                  Tiers should be ordered from lowest to highest threshold.
        
        Example: tiers=[(50.0, 5.0), (100.0, 10.0), (200.0, 15.0)]
                means 5% off for >=$50, 10% off for >=$100, 15% off for >=$200
        """
        assert len(tiers) > 0, "At least one tier is required"
        for threshold, percent in tiers:
            assert threshold >= 0, "Threshold must be non-negative"
            assert 0 <= percent <= 100, "Discount percent must be between 0 and 100"
        
        # Sort tiers by threshold to ensure proper ordering
        self.tiers = sorted(tiers, key=lambda x: x[0])

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        # Find the highest threshold that the subtotal meets or exceeds
        discount_percent = 0.0
        for threshold, percent in self.tiers:
            if subtotal >= threshold:
                discount_percent = percent
            else:
                break
        
        discount = subtotal * (discount_percent / 100.0)
        return round(subtotal - discount, 2)


class CompositeStrategy(PricingStrategy):
    """Compose multiple strategies; apply in order."""
    def __init__(self, strategies: list[PricingStrategy]) -> None:
        self.strategies = strategies

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        total = subtotal
        for strat in self.strategies:
            total = strat.apply(total, items)
        return round(total, 2)


def compute_subtotal(items: list[LineItem]) -> float:
    return round(sum(it.unit_price * it.qty for it in items), 2)
