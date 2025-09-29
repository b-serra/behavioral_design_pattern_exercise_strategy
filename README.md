# Pricing Example (Strategy Pattern in Python)

This project demonstrates the **Strategy** behavioral pattern via a small pricing engine.
You can switch pricing algorithms (strategies) at runtime without changing the client code.

## Structure

```
strategy_app/
├─ domain/               # Core domain (LineItem, PricingStrategy + implementations)
├─ application/          # Wiring / strategy selection
├─ presentation/         # CLI entry point
└─ tests/                # Unit + integration tests (pytest)
```

## Strategies

- **NoDiscount** – leaves subtotal unchanged.
- **PercentageDiscount** – applies a percentage discount to the subtotal.
- **BulkItemDiscount** – if a particular SKU quantity reaches a threshold, subtract a per-item amount.
- **CompositeStrategy** – combine multiple strategies and apply them in order.

## Run CLI

From the project root:

```bash
python -m presentation.cli --items '[{"sku":"A","qty":2,"unit_price":10.0},{"sku":"B","qty":5,"unit_price":3.0}]' --strategy percent --percent 10
# Subtotal: 35.00
# Strategy: percent
# Total: 31.50
```

Bulk strategy:

```bash
python -m presentation.cli --items '[{"sku":"A","qty":2,"unit_price":10.0},{"sku":"B","qty":5,"unit_price":3.0}]' --strategy bulk --sku B --threshold 5 --per-item-off 0.5
# Subtotal: 35.00
# Strategy: bulk
# Total: 32.50
```

Composite strategy (percent then bulk):

```bash
python -m presentation.cli --items '[{"sku":"A","qty":2,"unit_price":10.0},{"sku":"B","qty":5,"unit_price":3.0}]' --strategy composite --percent 10 --sku B --threshold 5 --per-item-off 0.5
# Subtotal: 35.00
# Strategy: composite
# Total: 29.00
```

## Tests

Install pytest and run:

```bash
pip install pytest
pytest -q strategy_app/tests
```
