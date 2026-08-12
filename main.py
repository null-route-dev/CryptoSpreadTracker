import argparse
import asyncio
import signal
import uvicorn
from src.cli import run_monitor, run_cli_loop, setup_logging
from src.config import get_config
from src.api import app, set_manager

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
    parser.add_argument(
        "--api-port",
        type=int,
        default=None,
        help="Start FastAPI server on specified port (e.g. 8000)"
    )
    parser.add_argument(
        "--stats-window",
        type=int,
        default=0,
        help="Number of recent spreads to keep for statistics (0 to disable)"
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Automatically discover common trading pairs across exchanges and show arbitrage summary"
    )
    return parser.parse_args()

async def run_api(manager, port: int):
    set_manager(manager)
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

async def main_async(args):
    config = get_config(args)
    setup_logging(config)

    manager = await run_monitor(config)
    if manager is None:
        return

    if args.api_port:
        api_task = asyncio.create_task(run_api(manager, args.api_port))
        cli_task = asyncio.create_task(run_cli_loop(manager, config))
        await asyncio.gather(api_task, cli_task)
    else:
        await run_cli_loop(manager, config)

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
        loop.run_until_complete(main_async(args))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

if __name__ == "__main__":
    main()
