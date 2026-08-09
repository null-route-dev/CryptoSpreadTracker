import os
import yaml
from typing import Dict, Any, Optional

def load_yaml_config(path: str = "config.yaml") -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}

def merge_config(cli_args: Any, env_prefix: str = "") -> Dict[str, Any]:
    yaml_config = load_yaml_config()
    config = {
        "exchanges": [],
        "symbols": [],
        "interval": 0.0,
        "min_spread": 0.0,
        "top": None,
        "log_level": "INFO",
        "log_file": None,
    }

    if yaml_config:
        for key in config:
            if key in yaml_config:
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

    return config
