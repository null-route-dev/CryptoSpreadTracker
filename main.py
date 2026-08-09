import argparse
import asyncio
import signal
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
        "--min-spread",
        type=float,
        default=0.0,
        help="Minimum absolute spread percentage to display (default: 0.0)"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="Show only the top N opportunities by absolute spread (default: all)"
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
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def shutdown():
        print("\nShutdown requested. Exiting gracefully.")
        loop.stop()

    try:
        loop.add_signal_handler(signal.SIGINT, shutdown)
        loop.add_signal_handler(signal.SIGTERM, shutdown)
    except NotImplementedError:
        pass

    try:
        loop.run_until_complete(run(args))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    main()
