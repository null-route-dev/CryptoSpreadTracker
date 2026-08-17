from typing import Dict, List, Optional, Any, Tuple
from ..base import WebSocketPriceFetcher, OrderBookFetcher
from ..common import normalize_symbol
import httpx

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

async def fetch_gateio_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.gateio.ws/api/v4/spot/currency_pairs")
        data = resp.json()
        return [normalize_symbol(s["id"]) for s in data if s["quote"] == "USDT"]
