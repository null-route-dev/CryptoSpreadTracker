import asyncio
from src.analyzers import analyze_spreads, discover_triangular_opportunities

_manager = None
_clients = {
    "spreads": [],
    "arbitrage": [],
    "triangular": [],
    "futures": []
}

def set_manager(manager):
    global _manager
    _manager = manager
    if manager:
        asyncio.create_task(_broadcast_loop("spreads", _broadcast_spreads))
        asyncio.create_task(_broadcast_loop("arbitrage", _broadcast_arbitrage))
        asyncio.create_task(_broadcast_loop("triangular", _broadcast_triangular))
        if manager.futures:
            asyncio.create_task(_broadcast_loop("futures", _broadcast_futures))

def get_manager():
    return _manager

def add_websocket_client(ws, channel):
    if channel in _clients:
        _clients[channel].append(ws)

def remove_websocket_client(ws, channel):
    if channel in _clients and ws in _clients[channel]:
        _clients[channel].remove(ws)

async def _broadcast_loop(channel, broadcast_func):
    if not _manager:
        return
    while True:
        try:
            raw_prices = await _manager.update_queue.get()
            await broadcast_func(raw_prices, channel)
        except Exception:
            continue

async def _broadcast_spreads(raw_prices, channel):
    prices_by_symbol = {}
    for ex_id, ex_prices in raw_prices.items():
        for sym, price in ex_prices.items():
            if price is not None:
                prices_by_symbol.setdefault(sym, {})[ex_id] = price
    analysis = analyze_spreads(prices_by_symbol)
    message = {"type": "spreads", "data": analysis}
    for ws in _clients[channel][:]:
        try:
            await ws.send_json(message)
        except:
            pass

async def _broadcast_arbitrage(raw_prices, channel):
    prices_by_symbol = {}
    for ex_id, ex_prices in raw_prices.items():
        for sym, price in ex_prices.items():
            if price is not None:
                prices_by_symbol.setdefault(sym, {})[ex_id] = price
    analysis = analyze_spreads(prices_by_symbol)
    rows = []
    for symbol, entries in analysis.items():
        if len(entries) < 2:
            continue
        min_price = min(e[1] for e in entries)
        max_price = max(e[1] for e in entries)
        min_exchange = next(e[0] for e in entries if e[1] == min_price)
        max_exchange = next(e[0] for e in entries if e[1] == max_price)
        spread_pct = ((max_price - min_price) / min_price) * 100
        rows.append({
            "symbol": symbol,
            "buy_exchange": min_exchange,
            "buy_price": min_price,
            "sell_exchange": max_exchange,
            "sell_price": max_price,
            "spread_pct": spread_pct
        })
    rows.sort(key=lambda x: x["spread_pct"], reverse=True)
    message = {"type": "arbitrage", "data": rows}
    for ws in _clients[channel][:]:
        try:
            await ws.send_json(message)
        except:
            pass

async def _broadcast_triangular(raw_prices, channel):
    prices_by_symbol = {}
    for ex_id, ex_prices in raw_prices.items():
        for sym, price in ex_prices.items():
            if price is not None:
                prices_by_symbol.setdefault(sym, {})[ex_id] = price
    opportunities = discover_triangular_opportunities(prices_by_symbol, 0.0)
    message = {"type": "triangular", "data": opportunities}
    for ws in _clients[channel][:]:
        try:
            await ws.send_json(message)
        except:
            pass

async def _broadcast_futures(raw_prices, channel):
    prices_by_symbol = {}
    for ex_id, ex_prices in raw_prices.items():
        for sym, data in ex_prices.items():
            if data is not None and isinstance(data, dict) and "price" in data:
                prices_by_symbol.setdefault(sym, {})[ex_id] = data
    analysis = analyze_spreads(prices_by_symbol)
    message = {"type": "futures", "data": analysis}
    for ws in _clients[channel][:]:
        try:
            await ws.send_json(message)
        except:
            pass
