from typing import Dict, List, Optional, Any
from ..base import WebSocketPriceFetcher
from ..common import normalize_symbol
import httpx

class BitgetWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://ws.bitget.com/mix/v1/stream"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [{"instType": "SP", "channel": "ticker", "instId": sym.replace("/", "")} for sym in symbols]
        return {"op": "subscribe", "args": args}

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if "action" in data and data["action"] == "snapshot" and "data" in data:
            for item in data["data"]:
                inst_id = item.get("instId")
                if inst_id:
                    for sym in self.symbols:
                        if sym.replace("/", "") == inst_id:
                            price = float(item.get("last", 0))
                            return {sym: price}
        return {}

async def fetch_bitget_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.bitget.com/api/v2/spot/public/symbols")
        data = resp.json()
        if data["code"] == "00000":
            return [normalize_symbol(s["symbolName"]) for s in data["data"] if s["quoteCoin"] == "USDT"]
        return []
