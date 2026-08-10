import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os
from .config import get_config
from .fetcher import PriceFetcherManager
from .analyzer import analyze_spreads
from .display import print_spreads

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

async def run_once_with_manager(manager: PriceFetcherManager, min_spread: float, top: int):
    all_prices = manager.get_all_prices()
    prices_by_symbol = {}
    for ex_id, ex_prices in all_prices.items():
        for sym, price in ex_prices.items():
            if price is not None:
                prices_by_symbol.setdefault(sym, {})[ex_id] = price
    analysis = analyze_spreads(prices_by_symbol)
    print_spreads(analysis, min_spread, top)

async def run_monitor(config: dict):
    manager = PriceFetcherManager(config["exchanges"], config["symbols"])
    await manager.start()
    return manager

async def run_cli_loop(manager: PriceFetcherManager, config: dict):
    try:
        if config["interval"] > 0:
            while True:
                await run_once_with_manager(manager, config["min_spread"], config["top"])
                await asyncio.sleep(config["interval"])
        else:
            await asyncio.sleep(1.5)
            await run_once_with_manager(manager, config["min_spread"], config["top"])
    finally:
        await manager.stop()

async def run(args):
    config = get_config(args)
    setup_logging(config)
    manager = await run_monitor(config)
    await run_cli_loop(manager, config)
