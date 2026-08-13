import asyncio
import logging
from typing import Dict, List, Optional, Union
from .websocket_fetcher import (
    BinanceWebSocketFetcher,
    BybitWebSocketFetcher,
    KrakenWebSocketFetcher,
    OkxWebSocketFetcher,
    KuCoinWebSocketFetcher,
    GateIoWebSocketFetcher,
    HuobiWebSocketFetcher,
    BitgetWebSocketFetcher,
    MEXCWebSocketFetcher,
    BinanceOrderBookFetcher,
    BybitOrderBookFetcher,
    KrakenOrderBookFetcher,
    OkxOrderBookFetcher,
    KuCoinOrderBookFetcher,
    GateIoOrderBookFetcher,
    WebSocketPriceFetcher,
    OrderBookFetcher,
)
from .symbol_fetcher import SYMBOL_FETCHERS

logger = logging.getLogger(__name__)

TICKER_MAP = {
    "binance": BinanceWebSocketFetcher,
    "bybit": BybitWebSocketFetcher,
    "kraken": KrakenWebSocketFetcher,
    "okx": OkxWebSocketFetcher,
    "kucoin": KuCoinWebSocketFetcher,
    "gateio": GateIoWebSocketFetcher,
    "huobi": HuobiWebSocketFetcher,
    "bitget": BitgetWebSocketFetcher,
    "mexc": MEXCWebSocketFetcher,
}

ORDERBOOK_MAP = {
    "binance": BinanceOrderBookFetcher,
    "bybit": BybitOrderBookFetcher,
    "kraken": KrakenOrderBookFetcher,
    "okx": OkxOrderBookFetcher,
    "kucoin": KuCoinOrderBookFetcher,
    "gateio": GateIoOrderBookFetcher,
}

class PriceFetcherManager:
    def __init__(self, exchange_ids: List[str], symbols: List[str], mode: str = "ticker", depth: int = 10, amount: float = 1000.0):
        self.exchange_ids = set(exchange_ids)
        self.symbols = set(symbols)
        self.mode = mode
        self.depth = depth
        self.amount = amount
        self.clients: Dict[str, Union[WebSocketPriceFetcher, OrderBookFetcher]] = {}
        self.prices: Dict[str, Dict[str, Optional[Union[float, Dict]]]] = {}
        self._update_task = None
        self._running = False
        self.update_queue: asyncio.Queue = asyncio.Queue()
        self._lock = asyncio.Lock()

    async def start(self):
        async with self._lock:
            if self._running:
                return
            for ex_id in self.exchange_ids:
                await self._add_exchange_client(ex_id)
            self._running = True
            self._update_task = asyncio.create_task(self._update_prices_loop())

    async def _add_exchange_client(self, ex_id: str):
        if ex_id in self.clients:
            return
        if self.mode == "ticker":
            client_class = TICKER_MAP.get(ex_id.lower())
            if not client_class:
                raise ValueError(f"Unsupported exchange for ticker: {ex_id}")
            client = client_class(list(self.symbols))
            await client.connect()
            self.clients[ex_id] = client
            self.prices[ex_id] = {sym: None for sym in self.symbols}
        elif self.mode == "orderbook":
            client_class = ORDERBOOK_MAP.get(ex_id.lower())
            if not client_class:
                raise ValueError(f"Unsupported exchange for orderbook: {ex_id}")
            client = client_class(list(self.symbols), depth=self.depth, amount=self.amount)
            await client.connect()
            self.clients[ex_id] = client
            self.prices[ex_id] = {sym: {"bid": None, "ask": None, "mid": None, "bids": [], "asks": []} for sym in self.symbols}
        else:
            raise ValueError(f"Invalid mode: {self.mode}")

    async def _remove_exchange_client(self, ex_id: str):
        if ex_id not in self.clients:
            return
        await self.clients[ex_id].close()
        del self.clients[ex_id]
        del self.prices[ex_id]

    async def add_exchange(self, ex_id: str):
        async with self._lock:
            if ex_id in self.exchange_ids:
                logger.info("Exchange %s already active", ex_id)
                return
            self.exchange_ids.add(ex_id)
            await self._add_exchange_client(ex_id)

    async def remove_exchange(self, ex_id: str):
        async with self._lock:
            if ex_id not in self.exchange_ids:
                logger.info("Exchange %s not active", ex_id)
                return
            self.exchange_ids.remove(ex_id)
            await self._remove_exchange_client(ex_id)

    async def add_symbol(self, symbol: str):
        async with self._lock:
            if symbol in self.symbols:
                logger.info("Symbol %s already tracked", symbol)
                return
            self.symbols.add(symbol)
            for ex_id in list(self.clients.keys()):
                await self._remove_exchange_client(ex_id)
                await self._add_exchange_client(ex_id)

    async def remove_symbol(self, symbol: str):
        async with self._lock:
            if symbol not in self.symbols:
                logger.info("Symbol %s not tracked", symbol)
                return
            self.symbols.remove(symbol)
            for ex_id in list(self.clients.keys()):
                await self._remove_exchange_client(ex_id)
                await self._add_exchange_client(ex_id)

    async def switch_mode(self, mode: str, depth: int = 10, amount: float = 1000.0):
        async with self._lock:
            if mode == self.mode and depth == self.depth and amount == self.amount:
                logger.info("Mode already %s", mode)
                return
            self.mode = mode
            self.depth = depth
            self.amount = amount
            for ex_id in list(self.clients.keys()):
                await self._remove_exchange_client(ex_id)
                await self._add_exchange_client(ex_id)

    async def _update_prices_loop(self):
        while self._running:
            changed = False
            for ex_id, client in self.clients.items():
                if self.mode == "ticker":
                    new_prices = client.get_current_prices()
                    if new_prices != self.prices[ex_id]:
                        self.prices[ex_id] = new_prices
                        changed = True
                else:
                    books = client.get_current_orderbooks()
                    for sym, book in books.items():
                        bids = book.get("bids", [])
                        asks = book.get("asks", [])
                        bid_price = bids[0][0] if bids else None
                        ask_price = asks[0][0] if asks else None
                        mid = (bid_price + ask_price) / 2 if (bid_price and ask_price) else None
                        new_entry = {"bid": bid_price, "ask": ask_price, "mid": mid, "bids": bids, "asks": asks}
                        if self.prices[ex_id].get(sym) != new_entry:
                            self.prices[ex_id][sym] = new_entry
                            changed = True
            if changed:
                await self.update_queue.put(self.get_all_prices())
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

    def get_all_prices(self) -> Dict[str, Dict[str, Optional[Union[float, Dict]]]]:
        return self.prices

    def get_current_exchanges(self) -> List[str]:
        return list(self.exchange_ids)

    def get_current_symbols(self) -> List[str]:
        return list(self.symbols)

async def discover_common_symbols(exchange_ids: List[str], min_exchanges: int = 2) -> List[str]:
    symbol_sets = {}
    for ex_id in exchange_ids:
        fetcher = SYMBOL_FETCHERS.get(ex_id.lower())
        if not fetcher:
            logger.warning("No symbol fetcher for %s, skipping", ex_id)
            continue
        try:
            symbols = await fetcher()
            if symbols:
                symbol_sets[ex_id] = set(symbols)
                logger.info("Fetched %d symbols from %s", len(symbols), ex_id)
            else:
                logger.warning("No symbols from %s", ex_id)
        except Exception as e:
            logger.error("Failed to fetch symbols from %s: %s", ex_id, e)
    if not symbol_sets:
        return []
    common = set.intersection(*symbol_sets.values())
    result = sorted(common)
    logger.info("Found %d common symbols", len(result))
    return result
