from typing import Dict, List, Optional
from ..base import WebSocketPriceFetcher
from ..common import normalize_symbol
import httpx

class CoinbaseWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://ws-feed.exchange.coinbase.com"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        return {
            "type": "subscribe",
            "channels": [{
                "name": "ticker",
                "product_ids": [sym.replace("/", "-") for sym in symbols]
            }]
        }

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if data.get("type") == "ticker":
            product = data.get("product_id")
            if product:
                price = float(data.get("price", 0))
                for sym in self.symbols:
                    if sym.replace("/", "-") == product:
                        return {sym: price}
        return {}

async def fetch_coinbase_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.exchange.coinbase.com/products")
        data = resp.json()
        result = []
        for item in data:
            if item.get("quote_currency") == "USDT":
                sym = f"{item['base_currency']}/{item['quote_currency']}"
                result.append(normalize_symbol(sym))
        return result
