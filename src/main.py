import asyncio
import ccxt.async_support as ccxt
import logging
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style
from typing import Dict, List, Optional


load_dotenv()

init(autoreset=True)


log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def fetch_price(exchange_id: str, symbol: str) -> Optional[float]:
    exchange = None
    try:
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class({'enableRateLimit': True})
        ticker = await exchange.fetch_ticker(symbol)
        price = ticker['last']
        if price is None:
            logger.warning(f"Price for {symbol} on {exchange_id} not found")
            return None
        return float(price)
    except Exception as e:
        logger.error(f"Error on {exchange_id} for {symbol}: {e}")
        return None
    finally:
        if exchange:
            await exchange.close()


async def fetch_prices_for_exchange(exchange_id: str, symbols: List[str]) -> Dict[str, Optional[float]]:
    results = {}
    for symbol in symbols:
        price = await fetch_price(exchange_id, symbol)
        results[symbol] = price
    return results


async def main_async():
    logger.info("CryptoSpreadTracker started")

    exchanges_str = os.getenv("EXCHANGES", "binance,bybit,kraken")
    exchanges = [ex.strip() for ex in exchanges_str.split(",") if ex.strip()]
    symbols_str = os.getenv("SYMBOLS", "BTC/USDT,ETH/USDT")
    symbols = [sym.strip() for sym in symbols_str.split(",") if sym.strip()]

    if not exchanges or not symbols:
        logger.error("No exchanges or symbols configured. Check your .env file.")
        return

    tasks = [fetch_prices_for_exchange(ex, symbols) for ex in exchanges]
    results_list = await asyncio.gather(*tasks)

    all_prices: Dict[str, Dict[str, float]] = {}
    for exchange, result in zip(exchanges, results_list):
        for symbol, price in result.items():
            if price is not None:
                all_prices.setdefault(symbol, {})[exchange] = price

    if not all_prices:
        print("\n❌ No prices fetched from any exchange.\n")
        return

    for symbol, prices in all_prices.items():
        if not prices:
            print(f"\n❌ No prices for {symbol}\n")
            continue

        sorted_exchanges = sorted(prices.items(), key=lambda x: x[1], reverse=True)
        best_exchange, best_price = sorted_exchanges[0]

        print(f"\n📊 Spread Analysis for {symbol}:\n")
        print(f"{'Exchange':<12} {'Price (USDT)':<15} {'Spread (%)':<10}")
        print("-" * 40)

        for exchange, price in sorted_exchanges:
            spread = ((price - best_price) / best_price) * 100
            color = Fore.GREEN if spread >= 0 else Fore.RED
            print(f"{exchange:<12} {price:<15.2f} {color}{spread:>+8.2f}%{Style.RESET_ALL}")

        print("-" * 40)
        print(f"Best price: {best_exchange} at {best_price:.2f} USDT\n")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
