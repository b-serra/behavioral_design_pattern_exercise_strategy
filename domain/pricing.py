
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


class CompositeStrategy(PricingStrategy):
    """Compose multiple strategies; apply in order."""
    def __init__(self, strategies: list[PricingStrategy]) -> None:
        self.strategies = strategies

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        total = subtotal
        for strat in self.strategies:
            total = strat.apply(total, items)
        return round(total, 2)


class TieredDiscount(PricingStrategy):
    """Applies different discount percentages based on spending tiers."""
    def __init__(self, tiers: list[tuple[float, float]]) -> None:
        """
        Args:
            tiers: List of (threshold, discount_percent) tuples, sorted by threshold.
                   Example: [(100, 5), (200, 10), (500, 20)] means:
                   - Spend $100+: 5% off
                   - Spend $200+: 10% off  
                   - Spend $500+: 20% off
        """
        self.tiers = sorted(tiers, key=lambda x: x[0])

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        discount_percent = 0
        for threshold, percent in self.tiers:
            if subtotal >= threshold:
                discount_percent = percent
            else:
                break
        
        discount = subtotal * (discount_percent / 100.0)
        return round(subtotal - discount, 2)


class BuyXGetYFree(PricingStrategy):
    """Buy X quantity of an item, get Y quantity free."""
    def __init__(self, sku: str, buy_qty: int, free_qty: int) -> None:
        self.sku = sku
        self.buy_qty = buy_qty
        self.free_qty = free_qty

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        total = subtotal
        for item in items:
            if item.sku == self.sku and item.qty >= self.buy_qty:
                # Calculate how many free items customer gets
                promotion_sets = item.qty // (self.buy_qty + self.free_qty)
                additional_free = min(
                    (item.qty % (self.buy_qty + self.free_qty)) // self.buy_qty * self.free_qty,
                    item.qty - (promotion_sets * (self.buy_qty + self.free_qty))
                )
                total_free = promotion_sets * self.free_qty + additional_free
                discount = total_free * item.unit_price
                total -= discount
        return round(max(total, 0.0), 2)


class CategoryDiscount(PricingStrategy):
    """Apply discount to items based on SKU pattern/category."""
    def __init__(self, category_prefix: str, discount_percent: float) -> None:
        self.category_prefix = category_prefix.upper()
        assert 0 <= discount_percent <= 100, "percent must be between 0 and 100"
        self.discount_percent = discount_percent

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        total = subtotal
        for item in items:
            if item.sku.upper().startswith(self.category_prefix):
                item_total = item.unit_price * item.qty
                discount = item_total * (self.discount_percent / 100.0)
                total -= discount
        return round(max(total, 0.0), 2)


class LoyaltyPointsDiscount(PricingStrategy):
    """Convert loyalty points to discount at a specified rate."""
    def __init__(self, points_available: int, points_per_dollar: int = 100) -> None:
        self.points_available = points_available
        self.points_per_dollar = points_per_dollar

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        max_discount = self.points_available / self.points_per_dollar
        # Can't discount more than the subtotal
        actual_discount = min(max_discount, subtotal)
        return round(subtotal - actual_discount, 2)


class QuantityBasedDiscount(PricingStrategy):
    """Apply progressive discount based on total quantity of items in cart."""
    def __init__(self, quantity_tiers: list[tuple[int, float]]) -> None:
        """
        Args:
            quantity_tiers: List of (min_quantity, discount_percent) tuples.
                           Example: [(5, 5), (10, 10), (20, 15)] means:
                           - 5+ items: 5% off
                           - 10+ items: 10% off
                           - 20+ items: 15% off
        """
        self.quantity_tiers = sorted(quantity_tiers, key=lambda x: x[0])

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        total_qty = sum(item.qty for item in items)
        discount_percent = 0
        
        for min_qty, percent in self.quantity_tiers:
            if total_qty >= min_qty:
                discount_percent = percent
            else:
                break
        
        discount = subtotal * (discount_percent / 100.0)
        return round(subtotal - discount, 2)


class HappyHourDiscount(PricingStrategy):
    """Time-based discount that applies only during specified hours."""
    def __init__(self, discount_percent: float, start_hour: int = 14, end_hour: int = 16) -> None:
        """
        Args:
            discount_percent: Percentage discount to apply
            start_hour: Starting hour in 24-hour format (default: 2 PM)
            end_hour: Ending hour in 24-hour format (default: 4 PM)
        """
        from datetime import datetime
        assert 0 <= discount_percent <= 100, "percent must be between 0 and 100"
        self.discount_percent = discount_percent
        self.start_hour = start_hour
        self.end_hour = end_hour
        self._current_hour = datetime.now().hour  # For testing, this could be injected

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        if self.start_hour <= self._current_hour < self.end_hour:
            discount = subtotal * (self.discount_percent / 100.0)
            return round(subtotal - discount, 2)
        return round(subtotal, 2)


def compute_subtotal(items: list[LineItem]) -> float:
    return round(sum(it.unit_price * it.qty for it in items), 2)