from __future__ import annotations
from domain.pricing import PricingStrategy, NoDiscount, PercentageDiscount, BulkItemDiscount, CompositeStrategy


def choose_strategy(kind: str, **kwargs) -> PricingStrategy:
    """
    Factory function to create pricing strategies based on the kind parameter.
    
    Args:
        kind: Strategy type ("none", "percent", "bulk", "composite")
        **kwargs: Strategy-specific parameters
        
    Returns:
        PricingStrategy instance
        
    Raises:
        ValueError: If unknown strategy kind or missing required parameters
    """
    if kind == "none":
        return NoDiscount()
    
    elif kind == "percent":
        percent = kwargs.get("percent", 0.0)
        return PercentageDiscount(percent)
    
    elif kind == "bulk":
        sku = kwargs.get("sku", "")
        threshold = kwargs.get("threshold", 0)
        per_item_off = kwargs.get("per_item_off", 0.0)
        
        if not sku:
            raise ValueError("SKU is required for bulk discount strategy")
        if threshold <= 0:
            raise ValueError("Threshold must be greater than 0 for bulk discount strategy")
        if per_item_off <= 0:
            raise ValueError("Per item discount must be greater than 0 for bulk discount strategy")
            
        return BulkItemDiscount(sku, threshold, per_item_off)
    
    elif kind == "composite":
        # For composite strategy, we'll combine percentage and bulk discounts
        strategies = []
        
        # Add percentage discount if specified
        percent = kwargs.get("percent", 0.0)
        if percent > 0:
            strategies.append(PercentageDiscount(percent))
        
        # Add bulk discount if parameters are provided
        sku = kwargs.get("sku", "")
        threshold = kwargs.get("threshold", 0)
        per_item_off = kwargs.get("per_item_off", 0.0)
        
        if sku and threshold > 0 and per_item_off > 0:
            strategies.append(BulkItemDiscount(sku, threshold, per_item_off))
        
        if not strategies:
            # If no strategies specified, default to no discount
            strategies.append(NoDiscount())
            
        return CompositeStrategy(strategies)
    
    else:
        raise ValueError(f"Unknown strategy kind: {kind}")
