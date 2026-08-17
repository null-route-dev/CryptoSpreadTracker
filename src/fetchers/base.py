import abc
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
import websockets

class WebSocketPriceFetcher(abc.ABC):
    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self._prices: Dict[str, Optional[float]] = {sym: None for sym in symbols}
        self._websocket = None
        self._task = None
        self._stop = False
        self._logger = logging.getLogger(self.__class__.__name__)

    @abc.abstractmethod
    def get_ws_url(self) -> str:
        pass

    @abc.abstractmethod
    def get_subscription_message(self, symbols: List[str]) -> Any:
        pass

    @abc.abstractmethod
    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        pass

    async def connect(self):
        self._stop = False
        self._task = asyncio.create_task(self._reconnect_loop())

    async def _reconnect_loop(self):
        retry_delay = 1.0
        while not self._stop:
            try:
                url = self.get_ws_url()
                async with websockets.connect(url) as websocket:
                    self._websocket = websocket
                    await self.subscribe()
                    await self._receive_messages_forever()
            except Exception as e:
                self._logger.error("Connection lost: %s. Reconnecting in %.1fs", e, retry_delay)
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 30)
            finally:
                self._websocket = None

    async def _receive_messages_forever(self):
        try:
            async for message in self._websocket:
                data = json.loads(message)
                prices = self.parse_price(data)
                if prices:
                    for sym, price in prices.items():
                        if price is not None:
                            self._prices[sym] = price
        except websockets.exceptions.ConnectionClosed:
            self._logger.warning("WebSocket connection closed")
            raise
        except Exception as e:
            self._logger.error("Error receiving messages: %s", e)
            raise

    async def subscribe(self):
        msg = self.get_subscription_message(self.symbols)
        if msg is not None:
            await self._websocket.send(json.dumps(msg))

    def get_current_prices(self) -> Dict[str, Optional[float]]:
        return self._prices.copy()

    async def close(self):
        self._stop = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._websocket:
            await self._websocket.close()

class OrderBookFetcher(abc.ABC):
    def __init__(self, symbols: List[str], depth: int = 10, amount: float = 1000.0):
        self.symbols = symbols
        self.depth = depth
        self.amount = amount
        self._bids: Dict[str, List[Tuple[float, float]]] = {}
        self._asks: Dict[str, List[Tuple[float, float]]] = {}
        self._websocket = None
        self._task = None
        self._stop = False
        self._logger = logging.getLogger(self.__class__.__name__)

    @abc.abstractmethod
    def get_ws_url(self) -> str:
        pass

    @abc.abstractmethod
    def get_subscription_message(self, symbols: List[str]) -> Any:
        pass

    @abc.abstractmethod
    def parse_orderbook(self, data: dict) -> Dict[str, Dict[str, List[Tuple[float, float]]]]:
        pass

    @staticmethod
    def calculate_vwap(levels: List[Tuple[float, float]], amount: float) -> Optional[float]:
        if not levels or amount <= 0:
            return None
        total_cost = 0.0
        total_volume = 0.0
        for price, vol in levels:
            if total_volume >= amount:
                break
            remaining = amount - total_volume
            if vol >= remaining:
                total_cost += price * remaining
                total_volume += remaining
            else:
                total_cost += price * vol
                total_volume += vol
        if total_volume == 0:
            return None
        return total_cost / total_volume

    async def connect(self):
        self._stop = False
        self._task = asyncio.create_task(self._reconnect_loop())

    async def _reconnect_loop(self):
        retry_delay = 1.0
        while not self._stop:
            try:
                url = self.get_ws_url()
                async with websockets.connect(url) as websocket:
                    self._websocket = websocket
                    await self.subscribe()
                    await self._receive_messages_forever()
            except Exception as e:
                self._logger.error("Connection lost: %s. Reconnecting in %.1fs", e, retry_delay)
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 30)
            finally:
                self._websocket = None

    async def _receive_messages_forever(self):
        try:
            async for message in self._websocket:
                data = json.loads(message)
                books = self.parse_orderbook(data)
                if books:
                    for sym, book in books.items():
                        self._bids[sym] = book.get("bids", [])[:self.depth]
                        self._asks[sym] = book.get("asks", [])[:self.depth]
        except websockets.exceptions.ConnectionClosed:
            self._logger.warning("WebSocket connection closed")
            raise
        except Exception as e:
            self._logger.error("Error receiving messages: %s", e)
            raise

    async def subscribe(self):
        msg = self.get_subscription_message(self.symbols)
        if msg is not None:
            await self._websocket.send(json.dumps(msg))

    def get_current_orderbooks(self) -> Dict[str, Dict[str, List[Tuple[float, float]]]]:
        result = {}
        for sym in self.symbols:
            result[sym] = {
                "bids": self._bids.get(sym, []),
                "asks": self._asks.get(sym, [])
            }
        return result

    async def close(self):
        self._stop = True
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._websocket:
            await self._websocket.close()
