import httpx
from typing import List

def normalize_symbol(symbol: str) -> str:
    symbol = symbol.upper()
    symbol = symbol.replace("-", "/").replace("_", "/")
    if not symbol.endswith("/USDT"):
        if symbol.endswith("USDT"):
            symbol = symbol[:-4] + "/USDT"
        else:
            symbol = symbol + "/USDT"
    return symbol

async def fetch_binance_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.binance.com/api/v3/exchangeInfo")
        data = resp.json()
        return [normalize_symbol(s["symbol"]) for s in data["symbols"] if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"]

async def fetch_bybit_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.bybit.com/v5/market/instruments-info?category=spot")
        data = resp.json()
        if data["retCode"] == 0:
            return [normalize_symbol(s["symbol"]) for s in data["result"]["list"] if s["quoteCoin"] == "USDT" and s["status"] == "Trading"]
        return []

async def fetch_kraken_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.kraken.com/0/public/AssetPairs")
        data = resp.json()
        if data.get("error") and len(data["error"]) > 0:
            return []
        return []

async def fetch_okx_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://www.okx.com/api/v5/market/tickers?instType=SPOT")
        data = resp.json()
        if data["code"] == "0":
            return [normalize_symbol(s["instId"]) for s in data["data"] if s["instId"].endswith("-USDT")]
        return []

async def fetch_kucoin_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.kucoin.com/api/v1/symbols")
        data = resp.json()
        if data["code"] == "200000":
            return [normalize_symbol(s["symbol"]) for s in data["data"] if s["quoteCurrency"] == "USDT"]
        return []

async def fetch_gateio_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.gateio.ws/api/v4/spot/currency_pairs")
        data = resp.json()
        return [normalize_symbol(s["id"]) for s in data if s["quote"] == "USDT"]

async def fetch_huobi_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.huobi.pro/v1/common/symbols")
        data = resp.json()
        if data["status"] == "ok":
            return [normalize_symbol(s["symbol"]) for s in data["data"] if s["quote-currency"] == "usdt"]
        return []

async def fetch_bitget_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.bitget.com/api/v2/spot/public/symbols")
        data = resp.json()
        if data["code"] == "00000":
            return [normalize_symbol(s["symbolName"]) for s in data["data"] if s["quoteCoin"] == "USDT"]
        return []

async def fetch_mexc_symbols() -> List[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://api.mexc.com/api/v3/exchangeInfo")
        data = resp.json()
        return [normalize_symbol(s["symbol"]) for s in data["symbols"] if s["quoteAsset"] == "USDT" and s["status"] == "TRADING"]

SYMBOL_FETCHERS = {
    "binance": fetch_binance_symbols,
    "bybit": fetch_bybit_symbols,
    "kraken": fetch_kraken_symbols,
    "okx": fetch_okx_symbols,
    "kucoin": fetch_kucoin_symbols,
    "gateio": fetch_gateio_symbols,
    "huobi": fetch_huobi_symbols,
    "bitget": fetch_bitget_symbols,
    "mexc": fetch_mexc_symbols,
}
