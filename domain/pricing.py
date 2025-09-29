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
    pass


class NoDiscount(PricingStrategy):
    # TODO: Implement a strategy that returns the original value without changes
    pass


class PercentageDiscount(PricingStrategy):
    def __init__(self, percent: float) -> None:
        # TODO: Store the percentage value and validate it's in the correct range
        pass

    # TODO: Implement the main calculation method that reduces the input by a percentage


class BulkItemDiscount(PricingStrategy):
    """If any single item's quantity >= threshold, apply a per-item discount for that SKU."""
    def __init__(self, sku: str, threshold: int, per_item_off: float) -> None:
        # TODO: Store the parameters needed to identify items and calculate reductions
        pass

    # TODO: Implement logic to iterate through items and apply reductions based on quantity thresholds


class BulkDiscount(PricingStrategy):
    def __init__(self, sku: str, min_qty: int, discount: float):
        """
        Initialize the BulkDiscount strategy.

        :param sku: The SKU of the item eligible for the discount.
        :param min_qty: The minimum quantity required to apply the discount.
        :param discount: The discount amount per unit (in the same currency as unit_price).
        """
        self.sku = sku
        self.min_qty = min_qty
        self.discount = discount

    def apply(self, subtotal: float, items: list[LineItem]) -> float:
        """
        Apply the bulk discount to the subtotal if the conditions are met.

        :param subtotal: The current subtotal of the cart.
        :param items: The list of LineItem objects in the cart.
        :return: The final total after applying the bulk discount.
        """
        discount_total = 0
        for item in items:
            if item.sku == self.sku and item.qty >= self.min_qty:
                discount_total += item.qty * self.discount
        return round(subtotal - discount_total, 2)


class CompositeStrategy(PricingStrategy):
    """Compose multiple strategies; apply in order."""
    def __init__(self, strategies: list[PricingStrategy]) -> None:
        # TODO: Store the collection of strategies to be applied sequentially
        pass

    # TODO: Implement method that applies each strategy in sequence, using the output of one as input to the next


def compute_subtotal(items: list[LineItem]) -> float:
    return round(sum(it.unit_price * it.qty for it in items), 2)
