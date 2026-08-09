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


class OkxWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://ws.okx.com:8443/ws/v5/public"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [{"channel": "tickers", "instId": sym.replace("/", "-")} for sym in symbols]
        return {"op": "subscribe", "args": args}

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if data.get("event") == "subscribe":
            return {}
        if "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                inst_id = item.get("instId")
                if inst_id:
                    symbol = inst_id.replace("-", "/")
                    if symbol in self.symbols:
                        price = float(item.get("last", 0))
                        return {symbol: price}
        return {}


class KuCoinWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://ws-api.kucoin.com/endpoint"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [f"{sym.replace('/', '-')}" for sym in symbols]
        return {
            "id": 1,
            "type": "subscribe",
            "topic": "/market/ticker:{}".format(",".join(args)),
            "privateChannel": False,
            "response": True
        }

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if data.get("type") == "message" and "data" in data:
            ticker_data = data["data"]
            symbol = ticker_data.get("symbol")
            if symbol:
                price = float(ticker_data.get("price", 0))
                for sym in self.symbols:
                    if sym.replace("/", "-") == symbol:
                        return {sym: price}
        return {}


class GateIoWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://ws.gate.io/v4/"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [f"spot.tickers.{sym.replace('/', '_')}" for sym in symbols]
        return {
            "time": 123456,
            "channel": "spot.tickers",
            "event": "subscribe",
            "payload": args
        }

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if data.get("channel") == "spot.tickers" and "result" in data:
            for item in data["result"]:
                symbol = item.get("currency_pair")
                if symbol:
                    price = float(item.get("last", 0))
                    for sym in self.symbols:
                        if sym.replace("/", "_") == symbol:
                            return {sym: price}
        return {}
