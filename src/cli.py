import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os
from .config import get_config
from .fetcher import PriceFetcherManager, discover_common_symbols
from .analyzer import analyze_spreads
from .display import print_spreads, print_arbitrage_summary
from .stats import SpreadStats

logger = logging.getLogger(__name__)

def setup_logging(config):
    log_level = getattr(logging, config["log_level"], logging.INFO)
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers = [logging.StreamHandler()]

    if config.get("log_file"):
        log_dir = os.path.dirname(config["log_file"])
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            config["log_file"],
            maxBytes=10*1024*1024,
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )

async def run_once_with_manager(manager: PriceFetcherManager, min_spread: float, top: int, stats: SpreadStats = None, discover: bool = False):
    all_prices = manager.get_all_prices()
    prices_by_symbol = {}
    for ex_id, ex_prices in all_prices.items():
        for sym, data in ex_prices.items():
            if data is not None:
                prices_by_symbol.setdefault(sym, {})[ex_id] = data
    analysis = analyze_spreads(prices_by_symbol)
    if stats:
        for symbol, entries in analysis.items():
            for entry in entries:
                exchange, mid, bid, ask, spread = entry
                stats.update(symbol, exchange, spread)
    if discover:
        print_arbitrage_summary(analysis)
    else:
        print_spreads(analysis, min_spread, top, stats)

async def run_monitor(config: dict):
    exchange_ids = config["exchanges"]
    symbols = config["symbols"]

    if config.get("discover", False):
        logger.info("Discovering common symbols...")
        symbols = await discover_common_symbols(exchange_ids, min_exchanges=2)
        if not symbols:
            logger.error("No common symbols found. Exiting.")
            return None
        logger.info("Using %d common symbols: %s", len(symbols), symbols[:10])
        if len(symbols) > 50:
            symbols = symbols[:50]
            logger.info("Limited to 50 symbols for performance.")

    manager = PriceFetcherManager(
        exchange_ids,
        symbols,
        mode=config.get("mode", "ticker"),
        depth=config.get("orderbook_depth", 10),
        amount=config.get("orderbook_amount", 1000.0)
    )
    await manager.start()
    return manager

async def run_cli_loop(manager: PriceFetcherManager, config: dict):
    stats = SpreadStats(config.get("stats_window", 0))
    try:
        if config["interval"] > 0:
            while True:
                await run_once_with_manager(manager, config["min_spread"], config["top"], stats, config.get("discover", False))
                await asyncio.sleep(config["interval"])
        else:
            await asyncio.sleep(1.5)
            await run_once_with_manager(manager, config["min_spread"], config["top"], stats, config.get("discover", False))
    finally:
        await manager.stop()

async def run(args):
    config = get_config(args)
    setup_logging(config)
    manager = await run_monitor(config)
    if manager is None:
        return
    await run_cli_loop(manager, config)
