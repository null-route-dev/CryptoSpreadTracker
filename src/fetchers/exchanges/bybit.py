from typing import Dict, List, Optional, Any, Tuple
from ..base import WebSocketPriceFetcher, OrderBookFetcher
from ..common import normalize_symbol
import httpx

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

class BybitFuturesTickerFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://stream.bybit.com/v5/public/linear"

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

class BybitFuturesFundingFetcher(WebSocketPriceFetcher):
    def __init__(self, symbols: List[str]):
        super().__init__(symbols)
        self._funding_rates: Dict[str, Optional[float]] = {sym: None for sym in symbols}

    def get_ws_url(self) -> str:
        return "wss://stream.bybit.com/v5/public/linear"

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
                        d = data["data"]
                        funding = float(d.get("fundingRate", 0))
                        self._funding_rates[sym] = funding
                        price = float(d["lastPrice"])
                        return {sym: price}
        return {}

    def get_funding_rates(self) -> Dict[str, Optional[float]]:
        return self._funding_rates.copy()

async def fetch_bybit_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.bybit.com/v5/market/instruments-info?category=spot")
        data = resp.json()
        if data["retCode"] == 0:
            return [normalize_symbol(s["symbol"]) for s in data["result"]["list"] if s["quoteCoin"] == "USDT" and s["status"] == "Trading"]
        return []

async def fetch_bybit_futures_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.bybit.com/v5/market/instruments-info?category=linear")
        data = resp.json()
        if data["retCode"] == 0:
            return [normalize_symbol(s["symbol"]) for s in data["result"]["list"] if s["quoteCoin"] == "USDT" and s["status"] == "Trading"]
        return []
