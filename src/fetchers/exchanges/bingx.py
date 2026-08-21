from typing import Dict, List, Optional
from ..base import WebSocketPriceFetcher
from ..common import normalize_symbol
import httpx

class BingXWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://open-api-ws.bingx.com/market"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [f"{sym.replace('/', '').lower()}@ticker" for sym in symbols]
        return {
            "id": 1,
            "method": "SUBSCRIBE",
            "params": args
        }

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if data.get("data") and data["data"].get("s"):
            raw_symbol = data["data"]["s"].upper()
            price = float(data["data"]["c"])
            for sym in self.symbols:
                if sym.replace("/", "") == raw_symbol:
                    return {sym: price}
        return {}

async def fetch_bingx_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://open-api.bingx.com/openApi/spot/v1/common/symbols")
        data = resp.json()
        if data.get("code") == 0:
            return [normalize_symbol(s["symbol"]) for s in data["data"] if s["quoteAsset"] == "USDT" and s["status"] == 1]
        return []
