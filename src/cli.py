import asyncio
import logging
from .config import get_config
from .fetcher import fetch_prices_for_exchange
from .analyzer import analyze_spreads
from .display import print_spreads

logger = logging.getLogger(__name__)

async def run_once(config):
    exchanges = config["exchanges"]
    symbols = config["symbols"]

    tasks = [fetch_prices_for_exchange(ex, symbols) for ex in exchanges]
    results_list = await asyncio.gather(*tasks)

    all_prices = {}
    for exchange, result in zip(exchanges, results_list):
        for symbol, price in result.items():
            if price is not None:
                all_prices.setdefault(symbol, {})[exchange] = price

    analysis = analyze_spreads(all_prices)
    print_spreads(
        analysis,
        min_spread=config["min_spread"],
        top=config["top"]
    )


async def run_loop(config):
    interval = config["interval"]
    while True:
        await run_once(config)
        if interval > 0:
            await asyncio.sleep(interval)
        else:
            break

async def run(args):
    config = get_config(args)

    logging.basicConfig(
        level=getattr(logging, config["log_level"], logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if config["interval"] > 0:
        await run_loop(config)
    else:
        await run_once(config)
