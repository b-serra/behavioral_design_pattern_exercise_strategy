from __future__ import annotations
from domain.pricing import PricingStrategy, NoDiscount, PercentageDiscount, BulkItemDiscount, CompositeStrategy, SubtotalThresholdPercentDiscount


def choose_strategy(kind: str, **kwargs) -> PricingStrategy:
    kind = (kind or "").lower()
    if kind == "none":
        return NoDiscount()
    if kind == "percent":
        percent = float(kwargs.get("percent", 0.0))
        return PercentageDiscount(percent)
    if kind == "bulk":
        sku = kwargs.get("sku", "")
        threshold = int(kwargs.get("threshold", 0))
        per_item_off = float(kwargs.get("per_item_off", 0.0))
        return BulkItemDiscount(sku=sku, threshold=threshold, per_item_off=per_item_off)
    if kind == "composite":
        # Compose a percent then bulk using the provided args
        percent = float(kwargs.get("percent", 0.0))
        sku = kwargs.get("sku", "")
        threshold = int(kwargs.get("threshold", 0))
        per_item_off = float(kwargs.get("per_item_off", 0.0))
        return CompositeStrategy([
            PercentageDiscount(percent),
            BulkItemDiscount(sku=sku, threshold=threshold, per_item_off=per_item_off),
        ])
    if kind == "subtotal-threshold-percent":
        threshold_amount = float(kwargs.get("threshold_amount", 0.0))
        percent = float(kwargs.get("percent", 0.0))
        return SubtotalThresholdPercentDiscount(threshold=threshold_amount, percent=percent)
    raise ValueError(f"Unknown strategy kind: {kind}")
