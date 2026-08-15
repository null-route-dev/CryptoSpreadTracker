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

class BinanceOrderBookFetcher(OrderBookFetcher):
    def get_ws_url(self) -> str:
        streams = [f"{sym.replace('/', '').lower()}@depth20" for sym in self.symbols]
        return f"wss://stream.binance.com:9443/stream?streams={'/'.join(streams)}"

    def get_subscription_message(self, symbols: List[str]) -> Any:
        return None

    async def subscribe(self):
        pass

    def parse_orderbook(self, data: dict) -> Dict[str, Dict[str, List[Tuple[float, float]]]]:
        stream = data.get("stream")
        if not stream:
            return {}
        raw_symbol = stream.split("@")[0].upper()
        for sym in self.symbols:
            if sym.replace("/", "") == raw_symbol:
                d = data.get("data", {})
                bids = [(float(b[0]), float(b[1])) for b in d.get("bids", [])]
                asks = [(float(a[0]), float(a[1])) for a in d.get("asks", [])]
                return {sym: {"bids": bids, "asks": asks}}
        return {}

class BybitOrderBookFetcher(OrderBookFetcher):
    def get_ws_url(self) -> str:
        return "wss://stream.bybit.com/v5/public/spot"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [f"orderbook.200.{sym.replace('/', '')}" for sym in symbols]
        return {"op": "subscribe", "args": args}

    def parse_orderbook(self, data: dict) -> Dict[str, Dict[str, List[Tuple[float, float]]]]:
        if "topic" in data and "data" in data:
            topic = data["topic"]
            if topic.startswith("orderbook.200."):
                raw_symbol = topic.split(".")[2]
                for sym in self.symbols:
                    if sym.replace("/", "") == raw_symbol:
                        book = data["data"]
                        bids = [(float(b[0]), float(b[1])) for b in book.get("b", [])]
                        asks = [(float(a[0]), float(a[1])) for a in book.get("a", [])]
                        return {sym: {"bids": bids, "asks": asks}}
        return {}

class KrakenOrderBookFetcher(OrderBookFetcher):
    def get_ws_url(self) -> str:
        return "wss://ws.kraken.com/v2"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        return {
            "method": "subscribe",
            "params": {
                "channel": "book",
                "symbol": symbols,
                "depth": 20
            }
        }

    def parse_orderbook(self, data: dict) -> Dict[str, Dict[str, List[Tuple[float, float]]]]:
        if data.get("channel") == "book" and "data" in data:
            for item in data["data"]:
                symbol = item.get("symbol")
                if symbol in self.symbols:
                    bids = [(float(b[0]), float(b[1])) for b in item.get("bids", [])]
                    asks = [(float(a[0]), float(a[1])) for a in item.get("asks", [])]
                    return {symbol: {"bids": bids, "asks": asks}}
        return {}

class OkxOrderBookFetcher(OrderBookFetcher):
    def get_ws_url(self) -> str:
        return "wss://ws.okx.com:8443/ws/v5/public"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [{"channel": "books", "instId": sym.replace("/", "-")} for sym in symbols]
        return {"op": "subscribe", "args": args}

    def parse_orderbook(self, data: dict) -> Dict[str, Dict[str, List[Tuple[float, float]]]]:
        if data.get("event") == "subscribe":
            return {}
        if "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                inst_id = item.get("instId")
                if inst_id:
                    symbol = inst_id.replace("-", "/")
                    if symbol in self.symbols:
                        bids = [(float(b[0]), float(b[1])) for b in item.get("bids", [])]
                        asks = [(float(a[0]), float(a[1])) for a in item.get("asks", [])]
                        return {symbol: {"bids": bids, "asks": asks}}
        return {}

class KuCoinOrderBookFetcher(OrderBookFetcher):
    def get_ws_url(self) -> str:
        return "wss://ws-api.kucoin.com/endpoint"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [f"{sym.replace('/', '-')}" for sym in symbols]
        return {
            "id": 1,
            "type": "subscribe",
            "topic": f"/market/level2:{','.join(args)}",
            "privateChannel": False,
            "response": True
        }

    def parse_orderbook(self, data: dict) -> Dict[str, Dict[str, List[Tuple[float, float]]]]:
        if data.get("type") == "message" and "data" in data:
            topic = data.get("topic", "")
            if topic.startswith("/market/level2:"):
                raw_symbol = topic.split(":")[1]
                for sym in self.symbols:
                    if sym.replace("/", "-") == raw_symbol:
                        book = data["data"]
                        bids = [(float(b[0]), float(b[1])) for b in book.get("bids", [])]
                        asks = [(float(a[0]), float(a[1])) for a in book.get("asks", [])]
                        return {sym: {"bids": bids, "asks": asks}}
        return {}

class GateIoOrderBookFetcher(OrderBookFetcher):
    def get_ws_url(self) -> str:
        return "wss://ws.gate.io/v4/"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [f"spot.order_book.{sym.replace('/', '_')}" for sym in symbols]
        return {
            "time": 123456,
            "channel": "spot.order_book",
            "event": "subscribe",
            "payload": args
        }

    def parse_orderbook(self, data: dict) -> Dict[str, Dict[str, List[Tuple[float, float]]]]:
        if data.get("channel") == "spot.order_book" and "result" in data:
            for item in data["result"]:
                symbol = item.get("currency_pair")
                if symbol:
                    for sym in self.symbols:
                        if sym.replace("/", "_") == symbol:
                            bids = [(float(b[0]), float(b[1])) for b in item.get("bids", [])]
                            asks = [(float(a[0]), float(a[1])) for a in item.get("asks", [])]
                            return {sym: {"bids": bids, "asks": asks}}
        return {}

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

class HuobiWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://api.huobi.pro/ws"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [f"market.{sym.replace('/', '').lower()}.ticker" for sym in symbols]
        return {"sub": ",".join(args), "id": 1}

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if "tick" in data and "ch" in data:
            channel = data["ch"]
            if channel.startswith("market.") and channel.endswith(".ticker"):
                raw_symbol = channel.split(".")[1].upper()
                for sym in self.symbols:
                    if sym.replace("/", "") == raw_symbol:
                        price = float(data["tick"]["close"])
                        return {sym: price}
        return {}

class BitgetWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://ws.bitget.com/mix/v1/stream"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [{"instType": "SP", "channel": "ticker", "instId": sym.replace("/", "")} for sym in symbols]
        return {"op": "subscribe", "args": args}

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if "action" in data and data["action"] == "snapshot" and "data" in data:
            for item in data["data"]:
                inst_id = item.get("instId")
                if inst_id:
                    for sym in self.symbols:
                        if sym.replace("/", "") == inst_id:
                            price = float(item.get("last", 0))
                            return {sym: price}
        return {}

class MEXCWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://wbs.mexc.com/ws"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [f"{sym.replace('/', '').lower()}@ticker" for sym in symbols]
        return {"method": "SUBSCRIPTION", "params": args, "id": 1}

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if "d" in data and "s" in data.get("d", {}):
            raw_symbol = data["d"]["s"].upper()
            for sym in self.symbols:
                if sym.replace("/", "") == raw_symbol:
                    price = float(data["d"]["c"])
                    return {sym: price}
        return {}
