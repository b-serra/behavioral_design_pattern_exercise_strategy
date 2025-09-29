from __future__ import annotations
from domain.pricing import PricingStrategy, NoDiscount, PercentageDiscount, BulkItemDiscount, CompositeStrategy, ThresholdSubtotalDiscount


def choose_strategy(kind: str, **kwargs) -> PricingStrategy:
    kind = kind.lower()
    if kind == "none":
        return NoDiscount()
    if kind == "percent":
        percent = float(kwargs.get("percent", 0.0))
        return PercentageDiscount(percent)
    if kind == "bulk":
        sku = kwargs.get("sku")
        threshold = int(kwargs.get("threshold", 0))
        per_item_off = float(kwargs.get("per_item_off", 0.0))
        if not sku:
            raise ValueError("sku is required for bulk strategy")
        return BulkItemDiscount(sku, threshold, per_item_off)
    if kind == "composite":
        percent = float(kwargs.get("percent", 0.0))
        sku = kwargs.get("sku")
        threshold = int(kwargs.get("threshold", 0))
        per_item_off = float(kwargs.get("per_item_off", 0.0))
        strategies: list[PricingStrategy] = []
        strategies.append(PercentageDiscount(percent))
        if not sku:
            raise ValueError("sku is required for composite bulk component")
        strategies.append(BulkItemDiscount(sku, threshold, per_item_off))
        return CompositeStrategy(strategies)
    if kind == "threshold_subtotal":
        threshold_total = float(kwargs.get("threshold_total", 0.0))
        off_amount = float(kwargs.get("off_amount", 0.0))
        return ThresholdSubtotalDiscount(threshold_total, off_amount)
    raise ValueError(f"Unknown strategy kind: {kind}")
