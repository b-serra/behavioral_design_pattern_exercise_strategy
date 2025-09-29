
from __future__ import annotations
from domain.pricing import (
    PricingStrategy, NoDiscount, PercentageDiscount, BulkItemDiscount, CompositeStrategy,
    TieredDiscount, BuyXGetYFree, CategoryDiscount, LoyaltyPointsDiscount, 
    QuantityBasedDiscount, HappyHourDiscount
)


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
        # Example: tiered=[(100,5),(200,10),(500,20)]
        tiers = kwargs.get("tiers", [(100, 5), (200, 10), (500, 20)])
        return TieredDiscount(tiers)
    if kind == "buyxgety":
        return BuyXGetYFree(
            sku=kwargs.get("sku", ""),
            buy_qty=int(kwargs.get("buy_qty", 2)),
            free_qty=int(kwargs.get("free_qty", 1))
        )
    if kind == "category":
        return CategoryDiscount(
            category_prefix=kwargs.get("category_prefix", ""),
            discount_percent=float(kwargs.get("discount_percent", 10.0))
        )
    if kind == "loyalty":
        return LoyaltyPointsDiscount(
            points_available=int(kwargs.get("points_available", 0)),
            points_per_dollar=int(kwargs.get("points_per_dollar", 100))
        )
    if kind == "quantity":
        # Example: quantity_tiers=[(5,5),(10,10),(20,15)]
        tiers = kwargs.get("quantity_tiers", [(5, 5), (10, 10), (20, 15)])
        return QuantityBasedDiscount(tiers)
    if kind == "happyhour":
        return HappyHourDiscount(
            discount_percent=float(kwargs.get("discount_percent", 20.0)),
            start_hour=int(kwargs.get("start_hour", 14)),
            end_hour=int(kwargs.get("end_hour", 16))
        )
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
