from __future__ import annotations
from domain.pricing import PricingStrategy, NoDiscount, PercentageDiscount, BulkItemDiscount, CompositeStrategy


def choose_strategy(kind: str, **kwargs) -> PricingStrategy:
    # TODO: Implement strategy selection logic based on the 'kind' parameter
    # Should support: "none", "percent", "bulk", "composite"
    # Each strategy type needs different parameters from **kwargs
    # Return the appropriate strategy instance or raise an error for unknown types
    kind = kind.lower()
    if kind == "none":
        return NoDiscount()
    elif kind == "percent":
        return PercentageDiscount(kwargs["percent"])
    elif kind == "bulk":
        return BulkItemDiscount(
            sku=kwargs["sku"],
            threshold=kwargs["threshold"],
            per_item_off=kwargs["per_item_off"]
        )
    elif kind == "composite":
        # For composite, create both percentage and bulk strategies
        strategies = []
        if "percent" in kwargs:
            strategies.append(PercentageDiscount(kwargs["percent"]))
        if "sku" in kwargs and "threshold" in kwargs and "per_item_off" in kwargs:
            strategies.append(BulkItemDiscount(
                sku=kwargs["sku"],
                threshold=kwargs["threshold"],
                per_item_off=kwargs["per_item_off"]
            ))
        return CompositeStrategy(strategies)
    else:
        raise ValueError(f"Unknown pricing strategy: {kind}")
