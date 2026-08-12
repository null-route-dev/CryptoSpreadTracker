from rich.console import Console
from rich.table import Table
from typing import Dict, List, Tuple, Optional
from .stats import SpreadStats

console = Console()

def print_spreads(
    analysis: Dict[str, List[Tuple[str, float, float, float, float]]],
    min_spread: float = 0.0,
    top: int = None,
    stats: Optional[SpreadStats] = None
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
        if stats:
            table.add_column("Avg %", justify="right")
            table.add_column("Min %", justify="right")
            table.add_column("Max %", justify="right")
            table.add_column("Std %", justify="right")

        for exchange, mid, bid, ask, spread in filtered:
            color = "green" if spread >= 0 else "red"
            if abs(spread) > 1.0:
                color = "bright_cyan"
            row = [
                exchange,
                f"{bid:.2f}" if bid is not None else "N/A",
                f"{ask:.2f}" if ask is not None else "N/A",
                f"{mid:.2f}" if mid is not None else "N/A",
                f"[{color}]{spread:>+8.2f}%[/{color}]"
            ]
            if stats:
                stat_data = stats.get_stats(symbol, exchange)
                if stat_data:
                    row.append(f"{stat_data['avg']:>+6.2f}")
                    row.append(f"{stat_data['min']:>+6.2f}")
                    row.append(f"{stat_data['max']:>+6.2f}")
                    row.append(f"{stat_data['std']:>6.2f}")
                else:
                    row.extend(["", "", "", ""])
            table.add_row(*row)

        best_ex, best_mid, _, _, _ = filtered[0]
        table.add_section()
        table.add_row("", "", "", "", "")
        table.add_row("Best mid price:", f"{best_ex} at {best_mid:.2f} USDT", "", "", "")
        console.print(table)
        console.print()

def print_arbitrage_summary(analysis: Dict[str, List[Tuple[str, float, float, float, float]]]):
    if not analysis:
        console.print("❌ No data for arbitrage summary.")
        return

    rows = []
    for symbol, entries in analysis.items():
        if len(entries) < 2:
            continue
        min_price = min(e[1] for e in entries)  # mid price
        max_price = max(e[1] for e in entries)
        min_exchange = next(e[0] for e in entries if e[1] == min_price)
        max_exchange = next(e[0] for e in entries if e[1] == max_price)
        spread_pct = ((max_price - min_price) / min_price) * 100
        rows.append((symbol, min_exchange, max_exchange, spread_pct, min_price, max_price))

    if not rows:
        console.print("No arbitrage opportunities (need at least 2 exchanges per symbol).")
        return

    rows.sort(key=lambda x: x[3], reverse=True)

    table = Table(title="🔄 Arbitrage Opportunities (Buy Low / Sell High)", show_header=True, header_style="bold green")
    table.add_column("Symbol", style="cyan", no_wrap=True)
    table.add_column("Buy (min price)", justify="right")
    table.add_column("Sell (max price)", justify="right")
    table.add_column("Spread %", justify="right", style="bright_yellow")

    for symbol, buy_ex, sell_ex, spread, min_p, max_p in rows:
        table.add_row(
            symbol,
            f"{buy_ex} @ {min_p:.2f}",
            f"{sell_ex} @ {max_p:.2f}",
            f"{spread:>+6.2f}%"
        )

    console.print(table)
    console.print()
