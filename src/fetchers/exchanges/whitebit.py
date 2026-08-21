from typing import Dict, List, Optional
from ..base import WebSocketPriceFetcher
from ..common import normalize_symbol
import httpx

class WhiteBITWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://api.whitebit.com/ws"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [f"{sym.replace('/', '_')}@ticker" for sym in symbols]
        return {
            "id": 1,
            "method": "subscribe",
            "params": args
        }

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if data.get("params") and data["params"].get("data"):
            ticker = data["params"]["data"]
            raw_symbol = ticker.get("symbol")
            if raw_symbol:
                price = float(ticker.get("last", 0))
                for sym in self.symbols:
                    if sym.replace("/", "_") == raw_symbol:
                        return {sym: price}
        return {}

async def fetch_whitebit_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.whitebit.com/api/v4/public/ticker")
        data = resp.json()
        result = []
        for sym in data.keys():
            if sym.endswith("_USDT"):
                result.append(normalize_symbol(sym))
        return result
