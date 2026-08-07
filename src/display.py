from colorama import Fore, Style, init
from typing import Dict, List, Tuple

init(autoreset=True)

def print_spreads(
    analysis: Dict[str, List[Tuple[str, float, float]]],
    min_spread: float = 0.0,
    top: int = None
):
    if not analysis:
        print("\n❌ No prices fetched from any exchange.\n")
        return

    for symbol, entries in analysis.items():
        filtered = [e for e in entries if abs(e[2]) >= min_spread]
        if not filtered:
            continue

        filtered.sort(key=lambda x: abs(x[2]), reverse=True)

        if top and top > 0:
            filtered = filtered[:top]

        print(f"\n📊 Spread Analysis for {symbol}:\n")
        print(f"{'Exchange':<12} {'Price (USDT)':<15} {'Spread (%)':<10}")
        print("-" * 40)

        for exchange, price, spread in filtered:
            color = Fore.GREEN if spread >= 0 else Fore.RED
            if abs(spread) > 1.0:
                color = Fore.CYAN + Style.BRIGHT
            print(f"{exchange:<12} {price:<15.2f} {color}{spread:>+8.2f}%{Style.RESET_ALL}")

        print("-" * 40)
        best_ex, best_price, _ = filtered[0]
        print(f"Best price: {best_ex} at {best_price:.2f} USDT\n")
