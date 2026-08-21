from .exchanges import (
    fetch_binance_symbols,
    fetch_bybit_symbols,
    fetch_kraken_symbols,
    fetch_okx_symbols,
    fetch_kucoin_symbols,
    fetch_gateio_symbols,
    fetch_huobi_symbols,
    fetch_bitget_symbols,
    fetch_mexc_symbols,
    fetch_bitfinex_symbols,
    fetch_coinbase_symbols,
    fetch_binance_futures_symbols,
    fetch_bybit_futures_symbols,
    fetch_okx_futures_symbols,
)

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
    "bitfinex": fetch_bitfinex_symbols,
    "coinbase": fetch_coinbase_symbols,
}

FUTURES_SYMBOL_FETCHERS = {
    "binance": fetch_binance_futures_symbols,
    "bybit": fetch_bybit_futures_symbols,
    "okx": fetch_okx_futures_symbols,
}
