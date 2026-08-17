from typing import Dict, List, Optional, Any, Tuple
from ..base import WebSocketPriceFetcher, OrderBookFetcher
from ..common import normalize_symbol
import httpx

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

class OkxFuturesTickerFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://ws.okx.com:8443/ws/v5/public"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [{"channel": "tickers", "instId": sym.replace("/", "-") + "-SWAP"} for sym in symbols]
        return {"op": "subscribe", "args": args}

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if data.get("event") == "subscribe":
            return {}
        if "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                inst_id = item.get("instId")
                if inst_id and inst_id.endswith("-SWAP"):
                    symbol = inst_id.replace("-SWAP", "").replace("-", "/")
                    if symbol in self.symbols:
                        price = float(item.get("last", 0))
                        return {symbol: price}
        return {}

class OkxFuturesFundingFetcher(WebSocketPriceFetcher):
    def __init__(self, symbols: List[str]):
        super().__init__(symbols)
        self._funding_rates: Dict[str, Optional[float]] = {sym: None for sym in symbols}

    def get_ws_url(self) -> str:
        return "wss://ws.okx.com:8443/ws/v5/public"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [{"channel": "tickers", "instId": sym.replace("/", "-") + "-SWAP"} for sym in symbols]
        return {"op": "subscribe", "args": args}

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if data.get("event") == "subscribe":
            return {}
        if "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                inst_id = item.get("instId")
                if inst_id and inst_id.endswith("-SWAP"):
                    symbol = inst_id.replace("-SWAP", "").replace("-", "/")
                    if symbol in self.symbols:
                        funding = float(item.get("fundingRate", 0))
                        self._funding_rates[symbol] = funding
                        price = float(item.get("last", 0))
                        return {symbol: price}
        return {}

    def get_funding_rates(self) -> Dict[str, Optional[float]]:
        return self._funding_rates.copy()

async def fetch_okx_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://www.okx.com/api/v5/market/tickers?instType=SPOT")
        data = resp.json()
        if data["code"] == "0":
            return [normalize_symbol(s["instId"]) for s in data["data"] if s["instId"].endswith("-USDT")]
        return []

async def fetch_okx_futures_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://www.okx.com/api/v5/market/tickers?instType=SWAP")
        data = resp.json()
        if data["code"] == "0":
            result = []
            for s in data["data"]:
                inst = s["instId"]
                if inst.endswith("-USDT-SWAP"):
                    sym = inst.replace("-SWAP", "")
                    result.append(normalize_symbol(sym))
            return result
        return []
