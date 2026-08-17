from typing import Dict, List, Optional, Any, Tuple
from ..base import WebSocketPriceFetcher, OrderBookFetcher
from ..common import normalize_symbol
import httpx

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

async def fetch_kraken_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.kraken.com/0/public/AssetPairs")
        data = resp.json()
        if data.get("error") and len(data["error"]) > 0:
            return []
        pairs = data.get("result", {})
        return [p for p in pairs if p.endswith("USD") and "BTC" not in p]
