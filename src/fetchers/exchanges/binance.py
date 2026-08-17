from typing import Dict, List, Optional, Any, Tuple
from ..base import WebSocketPriceFetcher, OrderBookFetcher
from ..common import normalize_symbol
import httpx

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

class BinanceFuturesTickerFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        streams = [f"{sym.replace('/', '').lower()}@ticker" for sym in self.symbols]
        return f"wss://fstream.binance.com/stream?streams={'/'.join(streams)}"

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
                d = data.get("data", {})
                price = float(d.get("c"))
                return {sym: price}
        return {}

class BinanceFuturesFundingFetcher(WebSocketPriceFetcher):
    def __init__(self, symbols: List[str]):
        super().__init__(symbols)
        self._funding_rates: Dict[str, Optional[float]] = {sym: None for sym in symbols}

    def get_ws_url(self) -> str:
        streams = [f"{sym.replace('/', '').lower()}@ticker" for sym in self.symbols]
        return f"wss://fstream.binance.com/stream?streams={'/'.join(streams)}"

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
                d = data.get("data", {})
                funding = float(d.get("f", 0))
                self._funding_rates[sym] = funding
                price = float(d.get("c"))
                return {sym: price}
        return {}

    def get_funding_rates(self) -> Dict[str, Optional[float]]:
        return self._funding_rates.copy()

async def fetch_binance_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.binance.com/api/v3/exchangeInfo")
        data = resp.json()
        return [normalize_symbol(s["symbol"]) for s in data["symbols"] if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"]

async def fetch_binance_futures_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
        data = resp.json()
        return [normalize_symbol(s["symbol"]) for s in data["symbols"] if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"]
    