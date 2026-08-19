from fastapi import FastAPI
from .routes import health, spreads, triangular, futures
from .websocket import spreads as ws_spreads, arbitrage as ws_arbitrage, triangular as ws_triangular, futures as ws_futures

app = FastAPI(title="CryptoSpreadTracker API")

app.include_router(health)
app.include_router(spreads)
app.include_router(triangular)
app.include_router(futures)
app.include_router(ws_spreads)
app.include_router(ws_arbitrage)
app.include_router(ws_triangular)
app.include_router(ws_futures)
