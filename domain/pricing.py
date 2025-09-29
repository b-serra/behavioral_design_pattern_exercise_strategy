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


# New creative pricing strategy: Buy X Get Y Free
class BuyXGetYFreeDiscount(PricingStrategy):
    """
    For a given SKU, for every X items bought, Y items are free (the cheapest ones).
    Example: Buy 2 get 1 free (X=2, Y=1)
    """
    def __init__(self, sku: str, buy_x: int, get_y: int):
        self.sku = sku
        self.buy_x = buy_x
        self.get_y = get_y

    def apply(self, amount: float, items: list[LineItem]) -> float:
        for item in items:
            if item.sku == self.sku and item.qty >= self.buy_x:
                # Calculate how many free items
                group_size = self.buy_x + self.get_y
                num_groups = item.qty // group_size
                free_items = num_groups * self.get_y
                # If there are leftover items that could form another partial group
                leftover = item.qty % group_size
                # If leftover is enough to get more free items
                if leftover > self.buy_x:
                    free_items += leftover - self.buy_x
                discount = free_items * item.unit_price
                return amount - discount
        return amount


def compute_subtotal(items: list[LineItem]) -> float:
    return round(sum(it.unit_price * it.qty for it in items), 2)
