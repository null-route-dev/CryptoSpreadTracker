import logging
from typing import Dict, List, Optional

from .websocket_fetcher import (
    BinanceWebSocketFetcher,
    BybitWebSocketFetcher,
    KrakenWebSocketFetcher,
    WebSocketPriceFetcher,
)

logger = logging.getLogger(__name__)

EXCHANGE_FETCHER_MAP = {
    "binance": BinanceWebSocketFetcher,
    "bybit": BybitWebSocketFetcher,
    "kraken": KrakenWebSocketFetcher,
}

async def fetch_prices_for_exchange(exchange_id: str, symbols: List[str]) -> Dict[str, Optional[float]]:
    fetcher_class = EXCHANGE_FETCHER_MAP.get(exchange_id.lower())
    if not fetcher_class:
        raise ValueError(f"Unsupported exchange: {exchange_id}")

    fetcher: WebSocketPriceFetcher = fetcher_class(symbols)
    try:
        await fetcher.connect()
        await fetcher.subscribe()
        prices = await fetcher.get_prices()
        return prices
    except Exception as e:
        logger.error("Error fetching from %s via WebSocket: %s", exchange_id, e)
        return {sym: None for sym in symbols}
    finally:
        await fetcher.close()
