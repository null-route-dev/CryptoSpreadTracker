import asyncio
import logging
from .config import get_config
from .fetcher import PriceFetcherManager
from .analyzer import analyze_spreads
from .display import print_spreads

logger = logging.getLogger(__name__)

async def run_once_with_manager(manager: PriceFetcherManager, min_spread: float, top: int):
    all_prices = manager.get_all_prices()
    prices_by_symbol = {}
    for ex_id, ex_prices in all_prices.items():
        for sym, price in ex_prices.items():
            if price is not None:
                prices_by_symbol.setdefault(sym, {})[ex_id] = price
    analysis = analyze_spreads(prices_by_symbol)
    print_spreads(analysis, min_spread, top)

async def run(args):
    config = get_config(args)

    logging.basicConfig(
        level=getattr(logging, config["log_level"], logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    manager = PriceFetcherManager(config["exchanges"], config["symbols"])
    await manager.start()

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
