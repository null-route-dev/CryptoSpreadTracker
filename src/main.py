import ccxt
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


logger = logging.getLogger(__name__)


def fetch_price(symbol: str = "BTC/USDT") -> float | None:
    try:
        exchange = ccxt.binance({
            'enableRateLimit': True,
        })

        ticker = exchange.fetch_ticker(symbol)
        price = ticker['last']

        if price is None:
            logger.warning(f"Price for {symbol} not found")
            return None

        return float(price)

    except ccxt.NetworkError as e:
        logger.error(f"Network error: {e}")
        return None
    except ccxt.ExchangeError as e:
        logger.error(f"Exchange error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


def main():
    logger.info("CryptoSpreadTracker started")

    pair = "BTC/USDT"
    price = fetch_price(pair)

    if price is not None:
        print(f"\n{pair} current price: {price:.2f} USDT\n")
    else:
        print(f"\nFailed to fetch price for {pair}\n")


if __name__ == "__main__":
    main()
