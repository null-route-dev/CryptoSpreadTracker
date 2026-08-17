from typing import Dict, List, Union, Any

def discover_triangular_opportunities(prices_by_symbol: Dict[str, Dict[str, Union[float, Dict]]], min_profit: float = 0.0) -> List[Dict]:
    opportunities = []
    for exchange, symbols_data in prices_by_symbol.items():
        available_symbols = set(symbols_data.keys())
        for sym1 in available_symbols:
            if "/" not in sym1:
                continue
            base1, quote1 = sym1.split("/")
            for sym2 in available_symbols:
                if "/" not in sym2 or sym2 == sym1:
                    continue
                base2, quote2 = sym2.split("/")
                if base1 != quote2:
                    continue
                sym3 = f"{base2}/{quote1}"
                if sym3 not in available_symbols:
                    continue
                if sym1 == sym3 or sym2 == sym3:
                    continue
                price1 = symbols_data[sym1]
                price2 = symbols_data[sym2]
                price3 = symbols_data[sym3]
                if isinstance(price1, dict):
                    price1 = price1.get("mid")
                if isinstance(price2, dict):
                    price2 = price2.get("mid")
                if isinstance(price3, dict):
                    price3 = price3.get("mid")
                if price1 is None or price2 is None or price3 is None:
                    continue
                theoretical = price1 * price2
                profit_pct = ((price3 / theoretical) - 1) * 100
                if profit_pct < min_profit:
                    continue
                opportunities.append({
                    "exchange": exchange,
                    "path": f"{quote1} -> {base1} -> {base2} -> {quote1}",
                    "profit": profit_pct,
                    "price1": price1,
                    "price2": price2,
                    "price3": price3,
                    "symbols": (sym1, sym2, sym3)
                })
    opportunities.sort(key=lambda x: x["profit"], reverse=True)
    return opportunities
