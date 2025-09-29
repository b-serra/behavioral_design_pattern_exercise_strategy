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



class BuyOneGetTwoFree(PricingStrategy):
    """Buy 1 item, get 2 free. Applied per SKU."""
    def __init__(self, sku: str) -> None:
        self.sku = sku

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        total = subtotal
        for item in items:
            if item.sku == self.sku and item.qty >= 3:
                every_three_items = item.qty // 3
                free_items = every_three_items * 2  
                discount = free_items * item.unit_price
                total -= discount
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


def compute_subtotal(items: list[LineItem]) -> float:
    return round(sum(it.unit_price * it.qty for it in items), 2)
