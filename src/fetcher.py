import logging
import asyncio
import ccxt.async_support as ccxt
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

async def fetch_prices_for_exchange(exchange_id: str, symbols: List[str]) -> Dict[str, Optional[float]]:
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({"enableRateLimit": True})
    try:
        if hasattr(exchange, "fetch_tickers"):
            tickers = await exchange.fetch_tickers()
            return {sym: tickers.get(sym, {}).get("last") for sym in symbols}
        else:
            async def fetch_one(sym):
                ticker = await exchange.fetch_ticker(sym)
                return ticker.get("last")
            tasks = [fetch_one(sym) for sym in symbols]
            prices = await asyncio.gather(*tasks)
            return dict(zip(symbols, prices))
    except Exception as e:
        logger.error("Error fetching from %s: %s", exchange_id, e)
        return {sym: None for sym in symbols}
    finally:
        await exchange.close()
