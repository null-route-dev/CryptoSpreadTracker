from typing import Dict
from rich.console import Console
from rich.table import Table

console = Console()

def print_spreads(analysis, min_spread, top, stats=None, fees=None):
    if fees is None:
        fees = {}
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
        has_funding = any(e[7] is not None for e in filtered)
        has_vwap = any(e[5] is not None or e[6] is not None for e in filtered)
        has_fees = bool(fees)
        table = Table(title=f"📊 Spread Analysis for {symbol}", show_header=True, header_style="bold magenta")
        table.add_column("Exchange", style="cyan", no_wrap=True)
        if has_vwap:
            table.add_column("VWAP Bid", justify="right", style="green")
            table.add_column("VWAP Ask", justify="right", style="red")
        else:
            table.add_column("Bid", justify="right", style="green")
            table.add_column("Ask", justify="right", style="red")
        table.add_column("Mid", justify="right", style="yellow")
        table.add_column("Spread %", justify="right")
        if has_fees:
            table.add_column("Net Spread %", justify="right", style="bright_green")
        if has_funding:
            table.add_column("Funding %", justify="right", style="magenta")
        if stats:
            table.add_column("Avg %", justify="right")
            table.add_column("Min %", justify="right")
            table.add_column("Max %", justify="right")
            table.add_column("Std %", justify="right")
        for entry in filtered:
            exchange, mid, bid, ask, spread, vwap_bid, vwap_ask, funding = entry
            color = "green" if spread >= 0 else "red"
            if abs(spread) > 1.0:
                color = "bright_cyan"
            if has_vwap:
                bid_display = f"{vwap_bid:.2f}" if vwap_bid is not None else "N/A"
                ask_display = f"{vwap_ask:.2f}" if vwap_ask is not None else "N/A"
            else:
                bid_display = f"{bid:.2f}" if bid is not None else "N/A"
                ask_display = f"{ask:.2f}" if ask is not None else "N/A"
            row = [
                exchange,
                bid_display,
                ask_display,
                f"{mid:.2f}" if mid is not None else "N/A",
                f"[{color}]{spread:>+8.2f}%[/{color}]"
            ]
            if has_fees:
                fee = fees.get(exchange, 0.0)
                net_spread = spread - fee
                row.append(f"{net_spread:>+8.2f}%")
            if has_funding:
                row.append(f"{funding:>+8.4f}%" if funding is not None else "N/A")
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
        best_ex, best_mid, _, _, _, _, _, _ = filtered[0]
        table.add_section()
        table.add_row("", "", "", "", "")
        table.add_row("Best mid price:", f"{best_ex} at {best_mid:.2f} USDT", "", "", "")
        console.print(table)
        console.print()

def print_arbitrage_summary(analysis, fees=None):
    if fees is None:
        fees = {}
    if not analysis:
        console.print("❌ No data for arbitrage summary.")
        return
    rows = []
    for symbol, entries in analysis.items():
        if len(entries) < 2:
            continue
        min_price = min(e[1] for e in entries)
        max_price = max(e[1] for e in entries)
        min_exchange = next(e[0] for e in entries if e[1] == min_price)
        max_exchange = next(e[0] for e in entries if e[1] == max_price)
        spread_pct = ((max_price - min_price) / min_price) * 100
        fee_buy = fees.get(min_exchange, 0.0)
        fee_sell = fees.get(max_exchange, 0.0)
        net_spread = spread_pct - fee_buy - fee_sell
        rows.append((symbol, min_exchange, max_exchange, spread_pct, net_spread, min_price, max_price))
    if not rows:
        console.print("No arbitrage opportunities (need at least 2 exchanges per symbol).")
        return
    rows.sort(key=lambda x: x[3], reverse=True)
    table = Table(title="🔄 Arbitrage Opportunities (Buy Low / Sell High)", show_header=True, header_style="bold green")
    table.add_column("Symbol", style="cyan", no_wrap=True)
    table.add_column("Buy (min price)", justify="right")
    table.add_column("Sell (max price)", justify="right")
    table.add_column("Spread %", justify="right", style="bright_yellow")
    if fees:
        table.add_column("Net Spread %", justify="right", style="bright_green")
    for symbol, buy_ex, sell_ex, spread, net_spread, min_p, max_p in rows:
        row = [
            symbol,
            f"{buy_ex} @ {min_p:.2f}",
            f"{sell_ex} @ {max_p:.2f}",
            f"{spread:>+6.2f}%"
        ]
        if fees:
            row.append(f"{net_spread:>+6.2f}%")
        table.add_row(*row)
    console.print(table)
    console.print()

def print_triangular_summary(opportunities, min_profit):
    if not opportunities:
        console.print("❌ No triangular arbitrage opportunities found.")
        return
    filtered = [o for o in opportunities if o["profit"] >= min_profit]
    if not filtered:
        console.print(f"❌ No triangular opportunities with profit >= {min_profit:.2f}%.")
        return
    table = Table(title="🔺 Triangular Arbitrage Opportunities", show_header=True, header_style="bold cyan")
    table.add_column("Exchange", style="cyan", no_wrap=True)
    table.add_column("Path", style="yellow")
    table.add_column("Profit %", justify="right", style="bright_green")
    table.add_column("Price1", justify="right")
    table.add_column("Price2", justify="right")
    table.add_column("Price3", justify="right")
    for opp in filtered:
        table.add_row(
            opp["exchange"],
            opp["path"],
            f"{opp['profit']:>+6.2f}%",
            f"{opp['price1']:.6f}",
            f"{opp['price2']:.6f}",
            f"{opp['price3']:.6f}"
        )
    console.print(table)
    console.print()

def print_futures_summary(analysis):
    if not analysis:
        console.print("❌ No futures data.")
        return
    table = Table(title="🔮 Futures Arbitrage Summary", show_header=True, header_style="bold cyan")
    table.add_column("Symbol", style="yellow", no_wrap=True)
    table.add_column("Exchange", style="cyan")
    table.add_column("Price", justify="right", style="green")
    table.add_column("Spread %", justify="right")
    table.add_column("Funding %", justify="right", style="magenta")
    for symbol, entries in analysis.items():
        for exchange, mid, bid, ask, spread, vwap_bid, vwap_ask, funding in entries:
            table.add_row(
                symbol,
                exchange,
                f"{mid:.2f}",
                f"{spread:>+8.2f}%",
                f"{funding:>+8.4f}%" if funding is not None else "N/A"
            )
    console.print(table)
    console.print()

def print_aggregated_orderbook(aggregated: Dict[str, Dict], top: int = 10):
    if not aggregated:
        console.print("❌ No orderbook data.")
        return
    for symbol, data in aggregated.items():
        bids = data.get("bids", [])[:top]
        asks = data.get("asks", [])[:top]
        table = Table(title=f"📊 Synthetic Orderbook for {symbol}", show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan", no_wrap=True)
        table.add_column("Price (USDT)", justify="right", style="green")
        table.add_column("Volume", justify="right", style="yellow")
        table.add_column("Sources", style="blue")
        for bid in bids:
            table.add_row("Bid", f"{bid['price']:.2f}", f"{bid['volume']:.4f}", ", ".join(bid['sources']))
        for ask in asks:
            table.add_row("Ask", f"{ask['price']:.2f}", f"{ask['volume']:.4f}", ", ".join(ask['sources']))
        if bids and asks:
            best_bid = bids[0]
            best_ask = asks[0]
            spread = ((best_ask['price'] - best_bid['price']) / best_bid['price']) * 100
            table.add_section()
            table.add_row("", "", "", "")
            table.add_row("Best bid:", f"{best_bid['price']:.2f}", f"{best_bid['volume']:.4f}", ", ".join(best_bid['sources']))
            table.add_row("Best ask:", f"{best_ask['price']:.2f}", f"{best_ask['volume']:.4f}", ", ".join(best_ask['sources']))
            table.add_row("Spread:", f"{spread:.4f}%", "", "")
        console.print(table)
        console.print()
