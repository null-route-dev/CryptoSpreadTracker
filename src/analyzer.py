from typing import Dict, List, Tuple

def analyze_spreads(all_prices: Dict[str, Dict[str, float]]) -> Dict[str, List[Tuple[str, float, float]]]:
    result = {}
    for symbol, prices in all_prices.items():
        if not prices:
            continue
        sorted_exchanges = sorted(prices.items(), key=lambda x: x[1], reverse=True)
        best_price = sorted_exchanges[0][1]
        entries = []
        for exchange, price in sorted_exchanges:
            spread = ((price - best_price) / best_price) * 100
            entries.append((exchange, price, spread))
        result[symbol] = entries
    return result
