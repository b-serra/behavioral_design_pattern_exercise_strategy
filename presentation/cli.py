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
                        choices=["none", "percent", "bulk", "composite", "tiered", 
                                "buyxgety", "category", "loyalty", "quantity", "happyhour"],
                        help="Strategy kind")
    parser.add_argument("--percent", type=float, default=0.0, help="Percent discount for 'percent' or 'composite'")
    parser.add_argument("--sku", type=str, default="", help="SKU for bulk/composite")
    parser.add_argument("--threshold", type=int, default=0, help="Qty threshold for bulk/composite")
    parser.add_argument("--per-item-off", type=float, default=0.0, dest="per_item_off",
                        help="Per item discount for bulk/composite")
    parser.add_argument("--buy-qty", type=int, default=2, dest="buy_qty",
                        help="Buy quantity for buyxgety strategy")
    parser.add_argument("--free-qty", type=int, default=1, dest="free_qty",
                        help="Free quantity for buyxgety strategy")
    parser.add_argument("--category-prefix", type=str, default="", dest="category_prefix",
                        help="Category prefix for category discount")
    parser.add_argument("--discount-percent", type=float, default=10.0, dest="discount_percent",
                        help="Discount percentage for category/happyhour strategies")
    parser.add_argument("--points-available", type=int, default=0, dest="points_available",
                        help="Available loyalty points")
    parser.add_argument("--points-per-dollar", type=int, default=100, dest="points_per_dollar",
                        help="Points needed per dollar discount")
    parser.add_argument("--start-hour", type=int, default=14, dest="start_hour",
                        help="Happy hour start time (24-hour format)")
    parser.add_argument("--end-hour", type=int, default=16, dest="end_hour",
                        help="Happy hour end time (24-hour format)")
    args = parser.parse_args()

    items = parse_items(args.items)
    subtotal = compute_subtotal(items)
    strat = choose_strategy(args.strategy, percent=args.percent, sku=args.sku,
                            threshold=args.threshold, per_item_off=args.per_item_off,
                            buy_qty=args.buy_qty, free_qty=args.free_qty,
                            category_prefix=args.category_prefix, discount_percent=args.discount_percent,
                            points_available=args.points_available, points_per_dollar=args.points_per_dollar,
                            start_hour=args.start_hour, end_hour=args.end_hour)
    total = strat.apply(subtotal, items)

    print(f"Subtotal: {subtotal:.2f}")
    print(f"Strategy: {args.strategy}")
    print(f"Total: {total:.2f}")


if __name__ == "__main__":
    main()