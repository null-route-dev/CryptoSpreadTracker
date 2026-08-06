import ccxt
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fetch_price(exchange_id: str, symbol: str = "BTC/USDT") -> float | None:
    try:
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class({
            'enableRateLimit': True,
        })

        ticker = exchange.fetch_ticker(symbol)
        price = ticker['last']

        if price is None:
            logger.warning(f"Price for {symbol} on {exchange_id} not found")
            return None

        return float(price)

    except ccxt.NetworkError as e:
        logger.error(f"Network error on {exchange_id}: {e}")
        return None
    except ccxt.ExchangeError as e:
        logger.error(f"Exchange error on {exchange_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error on {exchange_id}: {e}")
        return None


def main():
    logger.info("CryptoSpreadTracker started")

    symbol = "BTC/USDT"
    exchanges = ["binance", "bybit", "kraken"]

    prices = {}

    for exchange_id in exchanges:
        price = fetch_price(exchange_id, symbol)
        if price is not None:
            prices[exchange_id] = price

    if not prices:
        print("\n❌ No prices fetched from any exchange.\n")
        return

    best_exchange = max(prices, key=prices.get)
    best_price = prices[best_exchange]

    print(f"\nSpread Analysis for {symbol}:\n")
    print(f"{'Exchange':<12} {'Price (USDT)':<15} {'Spread (%)':<10}")
    print("-" * 40)

    for exchange, price in prices.items():
        spread = ((price - best_price) / best_price) * 100
        print(f"{exchange:<12} {price:<15.2f} {spread:>+8.2f}%")

    print("\n" + "-" * 40)
    print(f"Best price: {best_exchange} at {best_price:.2f} USDT\n")


if __name__ == "__main__":
    main()
