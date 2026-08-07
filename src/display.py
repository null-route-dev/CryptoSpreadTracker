from colorama import Fore, Style, init
from typing import Dict, List, Tuple

init(autoreset=True)

def print_spreads(analysis: Dict[str, List[Tuple[str, float, float]]]):
    if not analysis:
        print("\n❌ No prices fetched from any exchange.\n")
        return

    for symbol, entries in analysis.items():
        print(f"\n📊 Spread Analysis for {symbol}:\n")
        print(f"{'Exchange':<12} {'Price (USDT)':<15} {'Spread (%)':<10}")
        print("-" * 40)

        for exchange, price, spread in entries:
            color = Fore.GREEN if spread >= 0 else Fore.RED
            print(f"{exchange:<12} {price:<15.2f} {color}{spread:>+8.2f}%{Style.RESET_ALL}")

        print("-" * 40)
        best_ex, best_price, _ = entries[0]
        print(f"Best price: {best_ex} at {best_price:.2f} USDT\n")
