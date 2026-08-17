from typing import Dict, List, Optional, Any
from ..base import WebSocketPriceFetcher
from ..common import normalize_symbol
import httpx

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

async def fetch_huobi_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.huobi.pro/v1/common/symbols")
        data = resp.json()
        if data["status"] == "ok":
            return [normalize_symbol(s["symbol"]) for s in data["data"] if s["quote-currency"] == "usdt"]
        return []
