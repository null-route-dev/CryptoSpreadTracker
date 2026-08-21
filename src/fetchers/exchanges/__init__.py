from .binance import (
    BinanceWebSocketFetcher,
    BinanceOrderBookFetcher,
    BinanceFuturesTickerFetcher,
    BinanceFuturesFundingFetcher,
    fetch_binance_symbols,
    fetch_binance_futures_symbols,
)
from .bybit import (
    BybitWebSocketFetcher,
    BybitOrderBookFetcher,
    BybitFuturesTickerFetcher,
    BybitFuturesFundingFetcher,
    fetch_bybit_symbols,
    fetch_bybit_futures_symbols,
)
from .okx import (
    OkxWebSocketFetcher,
    OkxOrderBookFetcher,
    OkxFuturesTickerFetcher,
    OkxFuturesFundingFetcher,
    fetch_okx_symbols,
    fetch_okx_futures_symbols,
)
from .kraken import KrakenWebSocketFetcher, KrakenOrderBookFetcher, fetch_kraken_symbols
from .kucoin import KuCoinWebSocketFetcher, KuCoinOrderBookFetcher, fetch_kucoin_symbols
from .gateio import GateIoWebSocketFetcher, GateIoOrderBookFetcher, fetch_gateio_symbols
from .huobi import HuobiWebSocketFetcher, fetch_huobi_symbols
from .bitget import BitgetWebSocketFetcher, fetch_bitget_symbols
from .mexc import MEXCWebSocketFetcher, fetch_mexc_symbols
from .bitfinex import BitfinexWebSocketFetcher, fetch_bitfinex_symbols
from .coinbase import CoinbaseWebSocketFetcher, fetch_coinbase_symbols

TICKER_MAP = {
    "binance": BinanceWebSocketFetcher,
    "bybit": BybitWebSocketFetcher,
    "kraken": KrakenWebSocketFetcher,
    "okx": OkxWebSocketFetcher,
    "kucoin": KuCoinWebSocketFetcher,
    "gateio": GateIoWebSocketFetcher,
    "huobi": HuobiWebSocketFetcher,
    "bitget": BitgetWebSocketFetcher,
    "mexc": MEXCWebSocketFetcher,
    "bitfinex": BitfinexWebSocketFetcher,
    "coinbase": CoinbaseWebSocketFetcher,
}

ORDERBOOK_MAP = {
    "binance": BinanceOrderBookFetcher,
    "bybit": BybitOrderBookFetcher,
    "kraken": KrakenOrderBookFetcher,
    "okx": OkxOrderBookFetcher,
    "kucoin": KuCoinOrderBookFetcher,
    "gateio": GateIoOrderBookFetcher,
}

FUTURES_TICKER_MAP = {
    "binance": BinanceFuturesTickerFetcher,
    "bybit": BybitFuturesTickerFetcher,
    "okx": OkxFuturesTickerFetcher,
}

FUTURES_FUNDING_MAP = {
    "binance": BinanceFuturesFundingFetcher,
    "bybit": BybitFuturesFundingFetcher,
    "okx": OkxFuturesFundingFetcher,
}
