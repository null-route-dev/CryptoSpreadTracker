from typing import Dict, List, Optional
from ..base import WebSocketPriceFetcher
from ..common import normalize_symbol
import httpx

class BitfinexWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://api-pub.bitfinex.com/ws/2"

    def get_subscription_message(self, symbols: List[str]) -> dict:
        args = [f"ticker:{sym.replace('/', '')}" for sym in symbols]
        return {
            "event": "subscribe",
            "channel": "ticker",
            "symbol": args
        }

    def parse_price(self, data: dict) -> Dict[str, Optional[float]]:
        if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
            for sym in self.symbols:
                raw = sym.replace("/", "")
                if data[0] == f"ticker:{raw}":
                    price = float(data[1][6])
                    return {sym: price}
        return {}

async def fetch_bitfinex_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api-pub.bitfinex.com/v2/tickers?symbols=ALL")
        data = resp.json()
        result = []
        for item in data:
            if item[0].startswith("t") and item[0].endswith("UST"):
                sym = item[0][1:].replace("UST", "/USDT")
                result.append(normalize_symbol(sym))
        return result
