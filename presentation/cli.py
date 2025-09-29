import argparse
import json
from domain.pricing import LineItem, compute_subtotal
from application.bootstrap import choose_strategy


def parse_items(items_json: str) -> list[LineItem]:
    raw = json.loads(items_json)
    items = [LineItem(**obj) for obj in raw]
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description="Pricing CLI (Strategy Pattern)")
    parser.add_argument("--items", type=str, required=True,
                        help='JSON list of items: [{"sku":"A","qty":2,"unit_price":10.0}, ...]')
    parser.add_argument("--strategy", type=str, default="none",
                        choices=["none", "percent", "bulk", "composite", "threshold_subtotal"],
                        help="Strategy kind")
    parser.add_argument("--percent", type=float, default=0.0, help="Percent discount for 'percent' or 'composite'")
    parser.add_argument("--sku", type=str, default="", help="SKU for bulk/composite")
    parser.add_argument("--threshold", type=int, default=0, help="Qty threshold for bulk/composite")
    parser.add_argument("--per-item-off", type=float, default=0.0, dest="per_item_off",
                        help="Per item discount for bulk/composite")
    parser.add_argument("--threshold-total", type=float, default=0.0, dest="threshold_total",
                        help="Subtotal threshold for new threshold_subtotal strategy")
    parser.add_argument("--off-amount", type=float, default=0.0, dest="off_amount",
                        help="Fixed amount off when threshold is met for threshold_subtotal")
    args = parser.parse_args()

    items = parse_items(args.items)
    subtotal = compute_subtotal(items)
    
    strategy = choose_strategy(
        args.strategy,
        percent=args.percent,
        sku=args.sku,
        threshold=args.threshold,
        per_item_off=args.per_item_off,
        threshold_total=args.threshold_total,
        off_amount=args.off_amount,
    )
    total = strategy.apply(subtotal, items)
    
    print(f"Subtotal: {subtotal:.2f}")
    print(f"Strategy: {args.strategy}")
    print(f"Total: {total:.2f}")


if __name__ == "__main__":
    main()
