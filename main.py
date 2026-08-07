import argparse
import asyncio
from src.cli import run

def parse_args():
    parser = argparse.ArgumentParser(
        description="Real-time cryptocurrency arbitrage monitor (CLI)"
    )
    parser.add_argument(
        "-e", "--exchanges",
        help="Comma-separated list of exchange IDs (e.g. binance,bybit,kraken)"
    )
    parser.add_argument(
        "-s", "--symbols",
        help="Comma-separated trading pairs (e.g. BTC/USDT,ETH/USDT)"
    )
    parser.add_argument(
        "-i", "--interval",
        type=float,
        help="Update interval in seconds (omit or 0 for single run)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    asyncio.run(run(args))

if __name__ == "__main__":
    main()
