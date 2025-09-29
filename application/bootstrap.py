from __future__ import annotations
from domain.pricing import PricingStrategy, NoDiscount, PercentageDiscount, BulkItemDiscount, CompositeStrategy, TieredDiscount


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
        # Parse tiers from comma-separated list of "threshold:percent" pairs
        tiers_str = kwargs.get("tiers", "0:0")
        tiers = []
        for tier_str in tiers_str.split(","):
            threshold_str, percent_str = tier_str.strip().split(":")
            tiers.append((float(threshold_str), float(percent_str)))
        return TieredDiscount(tiers)
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
