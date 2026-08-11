from typing import Dict, List, Tuple, Union

def analyze_spreads(all_prices: Dict[str, Dict[str, Union[float, Dict]]]) -> Dict[str, List[Tuple[str, float, float, float, float]]]:
    result = {}
    for symbol, exchange_data in all_prices.items():
        mids = {}
        for ex, data in exchange_data.items():
            if isinstance(data, dict) and "mid" in data:
                if data["mid"] is not None:
                    mids[ex] = data["mid"]
            elif isinstance(data, (int, float)):
                mids[ex] = data
        if not mids:
            continue
        sorted_exchanges = sorted(mids.items(), key=lambda x: x[1], reverse=True)
        best_price = sorted_exchanges[0][1]
        entries = []
        for ex, mid in sorted_exchanges:
            spread = ((mid - best_price) / best_price) * 100
            ex_data = exchange_data.get(ex)
            if isinstance(ex_data, dict):
                bid = ex_data.get("bid")
                ask = ex_data.get("ask")
            else:
                bid = ask = mid
            entries.append((ex, mid, bid, ask, spread))
        result[symbol] = entries
    return result
