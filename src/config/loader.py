import os
import yaml
from typing import Dict, Any

def load_yaml_config(path: str = "config.yaml") -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}

def merge_config(cli_args: Any) -> Dict[str, Any]:
    yaml_config = load_yaml_config()
    config = {
        "exchanges": [],
        "symbols": [],
        "interval": 0.0,
        "min_spread": 0.0,
        "top": None,
        "log_level": "INFO",
        "log_file": None,
        "mode": "ticker",
        "orderbook_depth": 10,
        "orderbook_amount": 1000.0,
        "stats_window": 0,
        "discover": False,
        "interactive": False,
        "triangular": False,
        "triangular_min_profit": 0.0,
        "futures": False,
        "fees": {},
        "chart": False,
        "chart_symbol": None,
        "aggregate": False,
        "aggregate_depth": 10,
    }
    if yaml_config:
        for key in config:
            if key in yaml_config:
                if key == "fees" and isinstance(yaml_config[key], dict):
                    config[key] = yaml_config[key]
                else:
                    config[key] = yaml_config[key]
    if cli_args.exchanges:
        config["exchanges"] = [ex.strip() for ex in cli_args.exchanges.split(",") if ex.strip()]
    elif os.getenv("EXCHANGES"):
        config["exchanges"] = [ex.strip() for ex in os.getenv("EXCHANGES").split(",") if ex.strip()]
    else:
        config["exchanges"] = ["binance", "bybit", "kraken"]
    if cli_args.symbols:
        config["symbols"] = [sym.strip() for sym in cli_args.symbols.split(",") if sym.strip()]
    elif os.getenv("SYMBOLS"):
        config["symbols"] = [sym.strip() for sym in os.getenv("SYMBOLS").split(",") if sym.strip()]
    else:
        config["symbols"] = ["BTC/USDT", "ETH/USDT"]
    if cli_args.interval is not None:
        config["interval"] = float(cli_args.interval)
    elif os.getenv("INTERVAL"):
        config["interval"] = float(os.getenv("INTERVAL"))
    if cli_args.min_spread is not None:
        config["min_spread"] = float(cli_args.min_spread)
    elif os.getenv("MIN_SPREAD"):
        config["min_spread"] = float(os.getenv("MIN_SPREAD"))
    if cli_args.top is not None:
        config["top"] = cli_args.top
    elif os.getenv("TOP"):
        config["top"] = int(os.getenv("TOP"))
    if cli_args.log_level:
        config["log_level"] = cli_args.log_level.upper()
    elif os.getenv("LOG_LEVEL"):
        config["log_level"] = os.getenv("LOG_LEVEL").upper()
    if os.getenv("LOG_FILE"):
        config["log_file"] = os.getenv("LOG_FILE")
    if cli_args.mode:
        config["mode"] = cli_args.mode
    elif os.getenv("MODE"):
        config["mode"] = os.getenv("MODE").lower()
    elif "mode" in yaml_config:
        config["mode"] = yaml_config["mode"]
    if cli_args.orderbook_depth is not None:
        config["orderbook_depth"] = cli_args.orderbook_depth
    elif os.getenv("ORDERBOOK_DEPTH"):
        config["orderbook_depth"] = int(os.getenv("ORDERBOOK_DEPTH"))
    elif "orderbook_depth" in yaml_config:
        config["orderbook_depth"] = yaml_config["orderbook_depth"]
    if cli_args.orderbook_amount is not None:
        config["orderbook_amount"] = cli_args.orderbook_amount
    elif os.getenv("ORDERBOOK_AMOUNT"):
        config["orderbook_amount"] = float(os.getenv("ORDERBOOK_AMOUNT"))
    elif "orderbook_amount" in yaml_config:
        config["orderbook_amount"] = yaml_config["orderbook_amount"]
    if cli_args.stats_window is not None:
        config["stats_window"] = cli_args.stats_window
    elif os.getenv("STATS_WINDOW"):
        config["stats_window"] = int(os.getenv("STATS_WINDOW"))
    elif "stats_window" in yaml_config:
        config["stats_window"] = yaml_config["stats_window"]
    if cli_args.discover:
        config["discover"] = True
    elif os.getenv("DISCOVER", "").lower() == "true":
        config["discover"] = True
    elif "discover" in yaml_config:
        config["discover"] = yaml_config["discover"]
    if cli_args.interactive:
        config["interactive"] = True
    elif os.getenv("INTERACTIVE", "").lower() == "true":
        config["interactive"] = True
    elif "interactive" in yaml_config:
        config["interactive"] = yaml_config["interactive"]
    if cli_args.triangular:
        config["triangular"] = True
    elif os.getenv("TRIANGULAR", "").lower() == "true":
        config["triangular"] = True
    elif "triangular" in yaml_config:
        config["triangular"] = yaml_config["triangular"]
    if cli_args.triangular_min_profit is not None:
        config["triangular_min_profit"] = float(cli_args.triangular_min_profit)
    elif os.getenv("TRIANGULAR_MIN_PROFIT"):
        config["triangular_min_profit"] = float(os.getenv("TRIANGULAR_MIN_PROFIT"))
    elif "triangular_min_profit" in yaml_config:
        config["triangular_min_profit"] = yaml_config["triangular_min_profit"]
    if cli_args.futures:
        config["futures"] = True
    elif os.getenv("FUTURES", "").lower() == "true":
        config["futures"] = True
    elif "futures" in yaml_config:
        config["futures"] = yaml_config["futures"]
    if cli_args.chart:
        config["chart"] = True
    elif os.getenv("CHART", "").lower() == "true":
        config["chart"] = True
    elif "chart" in yaml_config:
        config["chart"] = yaml_config["chart"]
    if cli_args.chart_symbol:
        config["chart_symbol"] = cli_args.chart_symbol
    elif os.getenv("CHART_SYMBOL"):
        config["chart_symbol"] = os.getenv("CHART_SYMBOL")
    elif "chart_symbol" in yaml_config:
        config["chart_symbol"] = yaml_config["chart_symbol"]
    if cli_args.aggregate:
        config["aggregate"] = True
    elif os.getenv("AGGREGATE", "").lower() == "true":
        config["aggregate"] = True
    elif "aggregate" in yaml_config:
        config["aggregate"] = yaml_config["aggregate"]
    if cli_args.aggregate_depth is not None:
        config["aggregate_depth"] = cli_args.aggregate_depth
    elif os.getenv("AGGREGATE_DEPTH"):
        config["aggregate_depth"] = int(os.getenv("AGGREGATE_DEPTH"))
    elif "aggregate_depth" in yaml_config:
        config["aggregate_depth"] = yaml_config["aggregate_depth"]
    fees_str = ""
    if cli_args.fees:
        fees_str = cli_args.fees
    elif os.getenv("FEES"):
        fees_str = os.getenv("FEES")
    elif "fees" in yaml_config and isinstance(yaml_config["fees"], str):
        fees_str = yaml_config["fees"]
    if fees_str:
        config["fees"] = {}
        for part in fees_str.split(","):
            if ":" in part:
                ex, fee = part.split(":", 1)
                config["fees"][ex.strip()] = float(fee.strip())
    return config
