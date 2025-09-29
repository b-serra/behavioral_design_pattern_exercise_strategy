# Pricing Engine - Strategy Design Pattern in Python

This project demonstrates the **Strategy** behavioral pattern via a small pricing engine.
You can switch pricing algorithms (strategies) at runtime without changing the client code.
This codebase contains TODO comments marking areas where students need to implement the Strategy pattern components.

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

## Assignment

Complete the TODO comments throughout the codebase to implement the Strategy pattern.

### Key Implementation Areas:

1. **Strategy Interface** (`domain/pricing.py`): Define the common interface
2. **Concrete Strategies** (`domain/pricing.py`): Implement the calculation logic for each strategy type
3. **Strategy Factory** (`application/bootstrap.py`): Implement strategy selection logic
4. **Client Integration** (`presentation/cli.py`): Connect strategy usage with the CLI

### Expected Behavior (After Implementation)

**Percentage discount:**
```bash
python -m presentation.cli --items '[{"sku":"A","qty":2,"unit_price":10.0},{"sku":"B","qty":5,"unit_price":3.0}]' --strategy percent --percent 10
# Should output: Total: 31.50
```

**Bulk discount:**
```bash
python -m presentation.cli --items '[{"sku":"A","qty":2,"unit_price":10.0},{"sku":"B","qty":5,"unit_price":3.0}]' --strategy bulk --sku B --threshold 5 --per-item-off 0.5
# Should output: Total: 32.50
```

**Composite strategy:**
```bash
python -m presentation.cli --items '[{"sku":"A","qty":2,"unit_price":10.0},{"sku":"B","qty":5,"unit_price":3.0}]' --strategy composite --percent 10 --sku B --threshold 5 --per-item-off 0.5
# Should output: Total: 29.00
```

### Testing

Uncomment the test cases in `tests/` directory once your implementation is complete:
```bash
python -m pytest tests/
```

## Tests

Install pytest and run:

```bash
pip install pytest
pytest -q strategy_app/tests
```
