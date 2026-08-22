from typing import Dict, List, Tuple
from collections import defaultdict

def aggregate_orderbooks(all_orderbooks: Dict[str, Dict[str, Dict[str, List[Tuple[float, float]]]]]) -> Dict[str, List[Dict]]:
    result = {}
    for symbol, exchanges in all_orderbooks.items():
        bids = defaultdict(float)
        asks = defaultdict(float)
        bid_sources = defaultdict(list)
        ask_sources = defaultdict(list)
        for exchange, books in exchanges.items():
            for bid_price, bid_vol in books.get("bids", []):
                bids[bid_price] += bid_vol
                bid_sources[bid_price].append(exchange)
            for ask_price, ask_vol in books.get("asks", []):
                asks[ask_price] += ask_vol
                ask_sources[ask_price].append(exchange)
        sorted_bids = sorted(bids.items(), key=lambda x: x[0], reverse=True)
        sorted_asks = sorted(asks.items(), key=lambda x: x[0])
        result[symbol] = {
            "bids": [
                {"price": price, "volume": volume, "sources": bid_sources[price]}
                for price, volume in sorted_bids
            ],
            "asks": [
                {"price": price, "volume": volume, "sources": ask_sources[price]}
                for price, volume in sorted_asks
            ]
        }
    return result
