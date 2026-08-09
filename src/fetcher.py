import asyncio
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


class PriceFetcherManager:
    def __init__(self, exchange_ids: List[str], symbols: List[str]):
        self.exchange_ids = exchange_ids
        self.symbols = symbols
        self.clients: Dict[str, WebSocketPriceFetcher] = {}
        self.prices: Dict[str, Dict[str, Optional[float]]] = {}
        self._update_task = None
        self._running = False

    async def start(self):
        for ex_id in self.exchange_ids:
            client_class = EXCHANGE_FETCHER_MAP.get(ex_id.lower())
            if not client_class:
                raise ValueError(f"Unsupported exchange: {ex_id}")
            client = client_class(self.symbols)
            self.clients[ex_id] = client
            await client.connect()
            self.prices[ex_id] = {sym: None for sym in self.symbols}
        self._running = True
        self._update_task = asyncio.create_task(self._update_prices_loop())

    async def _update_prices_loop(self):
        while self._running:
            for ex_id, client in self.clients.items():
                self.prices[ex_id] = client.get_current_prices()
            await asyncio.sleep(0.5)

    async def stop(self):
        self._running = False
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
        for client in self.clients.values():
            await client.close()

    def get_all_prices(self) -> Dict[str, Dict[str, Optional[float]]]:
        return self.prices
