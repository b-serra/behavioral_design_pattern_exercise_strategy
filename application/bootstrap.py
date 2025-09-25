from __future__ import annotations
from domain.pricing import PricingStrategy, NoDiscount, PercentageDiscount, BulkItemDiscount, CompositeStrategy


def choose_strategy(kind: str, **kwargs) -> PricingStrategy:
    # TODO: Implement strategy selection logic based on the 'kind' parameter
    # Should support: "none", "percent", "bulk", "composite"
    # Each strategy type needs different parameters from **kwargs
    # Return the appropriate strategy instance or raise an error for unknown types
    if kind == "none":
        return NoDiscount() # no paramenter because no init in NoDiscount
    
    elif kind == "percent":
        percent = kwargs.get("percent")
        if percent is None:
            raise ValueError("PercentageDiscount requires 'percent' parameter")
        return PercentageDiscount(percent=percent)

    elif kind == "bulk":
        sku = kwargs.get("sku")
        threshold = kwargs.get("threshold")
        per_item_off = kwargs.get("per_item_off")

        if sku is None:
            raise ValueError("BulkDiscount requires 'sku' parameter")
        if threshold is None:
            raise ValueError("BulkDiscount requires 'threshold' parameter")
        if per_item_off is None:
            raise ValueError("BulkDiscount requires 'per_item_off' parameter")
        return BulkItemDiscount(sku=sku, threshold=threshold, per_item_off=per_item_off)

    elif kind == "composite":
        strategies = kwargs.get("strategies")
        if strategies is None:
            raise ValueError("CompositeStrategy requires 'strategies' parameter")
        return CompositeStrategy(strategies=strategies)
    
    else:
        raise ValueError(f"Unknown strategy kind: '{kind}'. Supported kinds: none, percent, bulk, composite")