from rich.console import Console
from rich.table import Table
from typing import Dict, List, Tuple

console = Console()

def print_spreads(
    analysis: Dict[str, List[Tuple[str, float, float, float, float]]],
    min_spread: float = 0.0,
    top: int = None
):
    if not analysis:
        console.print("\n❌ No prices fetched from any exchange.\n")
        return

    for symbol, entries in analysis.items():
        filtered = [e for e in entries if abs(e[4]) >= min_spread]
        if not filtered:
            continue

        filtered.sort(key=lambda x: abs(x[4]), reverse=True)

        if top and top > 0:
            filtered = filtered[:top]

        table = Table(title=f"📊 Spread Analysis for {symbol}", show_header=True, header_style="bold magenta")
        table.add_column("Exchange", style="cyan", no_wrap=True)
        table.add_column("Bid", justify="right", style="green")
        table.add_column("Ask", justify="right", style="red")
        table.add_column("Mid", justify="right", style="yellow")
        table.add_column("Spread %", justify="right")

        for exchange, mid, bid, ask, spread in filtered:
            color = "green" if spread >= 0 else "red"
            if abs(spread) > 1.0:
                color = "bright_cyan"
            table.add_row(
                exchange,
                f"{bid:.2f}" if bid is not None else "N/A",
                f"{ask:.2f}" if ask is not None else "N/A",
                f"{mid:.2f}" if mid is not None else "N/A",
                f"[{color}]{spread:>+8.2f}%[/{color}]"
            )

        best_ex, best_mid, _, _, _ = filtered[0]
        table.add_section()
        table.add_row("", "", "", "", "")
        table.add_row("Best mid price:", f"{best_ex} at {best_mid:.2f} USDT", "", "", "")

        console.print(table)
        console.print()
