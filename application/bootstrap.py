from __future__ import annotations
from domain.pricing import PricingStrategy, NoDiscount, PercentageDiscount, BulkItemDiscount, CompositeStrategy


def choose_strategy(kind: str, **kwargs) -> PricingStrategy:
    # TODO: Implement strategy selection logic based on the 'kind' parameter
    # Should support: "none", "percent", "bulk", "composite"
    # Each strategy type needs different parameters from **kwargs
    # Return the appropriate strategy instance or raise an error for unknown types
    pass
