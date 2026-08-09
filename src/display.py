from rich.console import Console
from rich.table import Table
from typing import Dict, List, Tuple

console = Console()

def print_spreads(
    analysis: Dict[str, List[Tuple[str, float, float]]],
    min_spread: float = 0.0,
    top: int = None
):
    if not analysis:
        console.print("\n❌ No prices fetched from any exchange.\n")
        return

    for symbol, entries in analysis.items():
        filtered = [e for e in entries if abs(e[2]) >= min_spread]
        if not filtered:
            continue

        filtered.sort(key=lambda x: abs(x[2]), reverse=True)

        if top and top > 0:
            filtered = filtered[:top]

        table = Table(title=f"📊 Spread Analysis for {symbol}", show_header=True, header_style="bold magenta")
        table.add_column("Exchange", style="cyan", no_wrap=True)
        table.add_column("Price (USDT)", justify="right", style="green")
        table.add_column("Spread (%)", justify="right")

        for exchange, price, spread in filtered:
            color = "green" if spread >= 0 else "red"
            if abs(spread) > 1.0:
                color = "bright_cyan"
            table.add_row(exchange, f"{price:.2f}", f"[{color}]{spread:>+8.2f}%[/{color}]")

        best_ex, best_price, _ = filtered[0]
        table.add_section()
        table.add_row("", "", "")
        table.add_row("Best price:", f"{best_ex} at {best_price:.2f} USDT", "")

        console.print(table)
        console.print()
