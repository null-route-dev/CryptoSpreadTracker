from typing import Dict, List, Tuple, Union, Optional

def analyze_spreads(all_prices: Dict[str, Dict[str, Union[float, Dict]]]) -> Dict[str, List[Tuple[str, float, float, float, float, Optional[float], Optional[float]]]]:
    result = {}
    for symbol, exchange_data in all_prices.items():
        mids = {}
        vwap_data = {}
        for ex, data in exchange_data.items():
            if isinstance(data, dict) and "mid" in data:
                if data["mid"] is not None:
                    mids[ex] = data["mid"]
                    vwap_data[ex] = {
                        "vwap_bid": data.get("vwap_bid"),
                        "vwap_ask": data.get("vwap_ask"),
                        "bid": data.get("bid"),
                        "ask": data.get("ask")
                    }
            elif isinstance(data, (int, float)):
                mids[ex] = data
                vwap_data[ex] = {"vwap_bid": None, "vwap_ask": None, "bid": data, "ask": data}
        if not mids:
            continue
        sorted_exchanges = sorted(mids.items(), key=lambda x: x[1], reverse=True)
        best_price = sorted_exchanges[0][1]
        entries = []
        for ex, mid in sorted_exchanges:
            spread = ((mid - best_price) / best_price) * 100
            vwap_info = vwap_data.get(ex, {})
            vwap_bid = vwap_info.get("vwap_bid")
            vwap_ask = vwap_info.get("vwap_ask")
            bid = vwap_info.get("bid")
            ask = vwap_info.get("ask")
            entries.append((ex, mid, bid, ask, spread, vwap_bid, vwap_ask))
        result[symbol] = entries
    return result
