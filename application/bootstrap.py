from __future__ import annotations
from domain.pricing import PricingStrategy, NoDiscount, PercentageDiscount, BulkItemDiscount, TieredPricingStrategy, CompositeStrategy


def choose_strategy(kind: str, **kwargs) -> PricingStrategy:
    kind = kind.lower()
    if kind == "none":
        return NoDiscount()
    if kind == "percent":
        return PercentageDiscount(kwargs.get("percent", 0.0))
    if kind == "bulk":
        return BulkItemDiscount(
            sku=kwargs.get("sku", ""),
            threshold=int(kwargs.get("threshold", 0)),
            per_item_off=float(kwargs.get("per_item_off", 0.0)),
        )
    if kind == "tiered":
        # Parse tier configuration from kwargs
        # Format: tiers=[(100,5),(200,10),(500,15)] as string representation
        tiers_str = kwargs.get("tiers", "[(100.0,5.0),(200.0,10.0),(500.0,15.0)]")
        try:
            tiers = eval(tiers_str)
            if not isinstance(tiers, list):
                tiers = [(100.0, 5.0), (200.0, 10.0), (500.0, 15.0)]  # default tiers
            # Convert to list of tuples with float values
            tiers = [(float(threshold), float(percent)) for threshold, percent in tiers]
        except:
            tiers = [(100.0, 5.0), (200.0, 10.0), (500.0, 15.0)]  # default tiers
        return TieredPricingStrategy(tiers)
    if kind == "composite":
        # Example: combine percent then bulk
        percent = PercentageDiscount(kwargs.get("percent", 0.0))
        bulk = BulkItemDiscount(
            sku=kwargs.get("sku", ""),
            threshold=int(kwargs.get("threshold", 0)),
            per_item_off=float(kwargs.get("per_item_off", 0.0)),
        )
        return CompositeStrategy([percent, bulk])
    raise ValueError(f"Unknown strategy kind: {kind}")
