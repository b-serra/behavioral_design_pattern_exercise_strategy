import sys
from importlib import reload
import presentation.cli as cli


def run_cli(args_list, capsys):
    backup = sys.argv
    try:
        sys.argv = ["prog"] + args_list
        reload(cli)
        cli.main()
        return capsys.readouterr().out
    finally:
        sys.argv = backup


def test_cli_none_strategy(capsys):
    items = '[{"sku":"A","qty":2,"unit_price":10.0},{"sku":"B","qty":5,"unit_price":3.0}]'
    out = run_cli(["--items", items, "--strategy", "none"], capsys)
    assert "Subtotal: 35.00" in out
    assert "Strategy: none" in out
    assert "Total: 35.00" in out


def test_cli_percent_strategy(capsys):
    items = '[{"sku":"A","qty":2,"unit_price":10.0},{"sku":"B","qty":5,"unit_price":3.0}]'
    out = run_cli(["--items", items, "--strategy", "percent", "--percent", "10"], capsys)
    assert "Subtotal: 35.00" in out
    assert "Strategy: percent" in out
    assert "Total: 31.50" in out


def test_cli_bulk_strategy(capsys):
    items = '[{"sku":"A","qty":2,"unit_price":10.0},{"sku":"B","qty":5,"unit_price":3.0}]'
    out = run_cli([
        "--items", items,
        "--strategy", "bulk",
        "--sku", "B",
        "--threshold", "5",
        "--per-item-off", "0.5",
    ], capsys)
    assert "Total: 32.50" in out


def test_cli_composite_strategy(capsys):
    items = '[{"sku":"A","qty":2,"unit_price":10.0},{"sku":"B","qty":5,"unit_price":3.0}]'
    out = run_cli([
        "--items", items,
        "--strategy", "composite",
        "--percent", "10",
        "--sku", "B",
        "--threshold", "5",
        "--per-item-off", "0.5",
    ], capsys)
    assert "Total: 29.00" in out
