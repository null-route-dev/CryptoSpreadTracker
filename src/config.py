import os
from dotenv import load_dotenv

load_dotenv()

def get_config(args):
    exchanges = args.exchanges or os.getenv("EXCHANGES", "binance,bybit,kraken")
    symbols = args.symbols or os.getenv("SYMBOLS", "BTC/USDT,ETH/USDT")
    interval = args.interval if args.interval is not None else 0.0
    log_level = args.log_level or os.getenv("LOG_LEVEL", "INFO")

    return {
        "exchanges": [ex.strip() for ex in exchanges.split(",") if ex.strip()],
        "symbols": [sym.strip() for sym in symbols.split(",") if sym.strip()],
        "interval": float(interval),
        "log_level": log_level.upper(),
    }
