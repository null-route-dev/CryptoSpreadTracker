import abc
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any

import websockets


class WebSocketPriceFetcher(abc.ABC):

    def __init__(self, symbols: List[str]):
        self.symbols = symbols
        self._prices: Dict[str, Optional[float]] = {sym: None for sym in symbols}
        self._websocket = None
        self._task = None
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
        url = self.get_ws_url()
        self._websocket = await websockets.connect(url)
        self._task = asyncio.create_task(self._receive_messages())

    async def _receive_messages(self):
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
        except Exception as e:
            self._logger.error("Error receiving messages: %s", e)

    async def subscribe(self):
        msg = self.get_subscription_message(self.symbols)
        if msg is not None:
            await self._websocket.send(json.dumps(msg))

    async def get_prices(self) -> Dict[str, Optional[float]]:
        timeout = 2.0
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < timeout:
            if all(price is not None for price in self._prices.values()):
                break
            await asyncio.sleep(0.1)
        return self._prices.copy()

    async def close(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._websocket:
            await self._websocket.close()


class BinanceWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        streams = [f"{sym.replace('/', '').lower()}@ticker" for sym in self.symbols]
        return f"wss://stream.binance.com:9443/stream?streams={'/'.join(streams)}"

    def get_subscription_message(self, symbols: List[str]) -> Any:
        return None

    async def subscribe(self):
        pass

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        stream = data.get("stream")
        if not stream:
            return {}
        raw_symbol = stream.split("@")[0].upper()
        for sym in self.symbols:
            if sym.replace("/", "") == raw_symbol:
                price = float(data.get("data", {}).get("c"))
                return {sym: price}
        return {}


class BybitWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://stream.bybit.com/v5/public/spot"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [f"tickers.{sym.replace('/', '')}" for sym in symbols]
        return {"op": "subscribe", "args": args}

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if "topic" in data and "data" in data:
            topic = data["topic"]
            if topic.startswith("tickers."):
                raw_symbol = topic.split(".")[1]
                for sym in self.symbols:
                    if sym.replace("/", "") == raw_symbol:
                        price = float(data["data"]["lastPrice"])
                        return {sym: price}
        return {}


class KrakenWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://ws.kraken.com/v2"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        return {
            "method": "subscribe",
            "params": {
                "channel": "ticker",
                "symbol": symbols
            }
        }

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if data.get("channel") == "ticker" and "data" in data:
            for item in data["data"]:
                symbol = item.get("symbol")
                if symbol in self.symbols:
                    price = float(item["last"])
                    return {symbol: price}
        return {}
