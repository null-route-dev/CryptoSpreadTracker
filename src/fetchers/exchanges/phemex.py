from typing import Dict, List, Optional
from ..base import WebSocketPriceFetcher
from ..common import normalize_symbol
import httpx

class PhemexWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://phemex.com/ws"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [f"{sym.replace('/', '')}.ticker" for sym in symbols]
        return {
            "method": "subscribe",
            "params": args,
            "id": 1
        }

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if data.get("result") and data["result"].get("data"):
            ticker = data["result"]["data"]
            raw_symbol = ticker.get("symbol")
            if raw_symbol:
                price = float(ticker.get("lastPrice", 0))
                for sym in self.symbols:
                    if sym.replace("/", "") == raw_symbol:
                        return {sym: price}
        return {}

async def fetch_phemex_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.phemex.com/public/products")
        data = resp.json()
        if data.get("code") == 0:
            return [normalize_symbol(s["symbol"]) for s in data["data"]["products"] if s["quoteCurrency"] == "USDT" and s["status"] == "Listed"]
        return []
