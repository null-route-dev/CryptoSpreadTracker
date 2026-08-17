def normalize_symbol(symbol: str) -> str:
    symbol = symbol.upper()
    symbol = symbol.replace("-", "/").replace("_", "/")
    if not symbol.endswith("/USDT"):
        if symbol.endswith("USDT"):
            symbol = symbol[:-4] + "/USDT"
        else:
            symbol = symbol + "/USDT"
    return symbol
