from typing import Dict, List, Optional, Any
from ..base import WebSocketPriceFetcher
from ..common import normalize_symbol
import httpx

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

async def fetch_mexc_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.mexc.com/api/v3/exchangeInfo")
        data = resp.json()
        return [normalize_symbol(s["symbol"]) for s in data["symbols"] if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"]
