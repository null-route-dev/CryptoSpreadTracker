from typing import Dict, List, Optional, Any, Tuple
from ..base import WebSocketPriceFetcher, OrderBookFetcher
from ..common import normalize_symbol
import httpx

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

async def fetch_kucoin_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.kucoin.com/api/v1/symbols")
        data = resp.json()
        if data["code"] == "200000":
            return [normalize_symbol(s["symbol"]) for s in data["data"] if s["quoteCurrency"] == "USDT"]
        return []
