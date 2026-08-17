import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from .config import get_config
from .fetchers import PriceFetcherManager, discover_common_symbols, discover_common_futures_symbols, discover_triangular_opportunities
from .analyzer import analyze_spreads
from .display import print_spreads, print_arbitrage_summary, print_triangular_summary, print_futures_summary
from .stats import SpreadStats

logger = logging.getLogger(__name__)

def setup_logging(config):
    log_level = getattr(logging, config["log_level"], logging.INFO)
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers = [logging.StreamHandler()]

    if config.get("log_file"):
        log_dir = os.path.dirname(config["log_file"])
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            config["log_file"],
            maxBytes=10*1024*1024,
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=handlers
    )

async def run_once_with_manager(manager, config):
    all_prices = manager.get_all_prices()
    prices_by_symbol = {}
    for ex_id, ex_prices in all_prices.items():
        for sym, data in ex_prices.items():
            if data is not None:
                prices_by_symbol.setdefault(sym, {})[ex_id] = data

    if config.get("triangular", False):
        opportunities = discover_triangular_opportunities(
            prices_by_symbol,
            min_profit=config.get("triangular_min_profit", 0.0)
        )
        print_triangular_summary(opportunities, config.get("triangular_min_profit", 0.0))
    elif config.get("futures", False):
        analysis = analyze_spreads(prices_by_symbol)
        print_futures_summary(analysis)
    else:
        analysis = analyze_spreads(prices_by_symbol)
        if config.get("stats_window", 0) > 0:
            stats = SpreadStats(config["stats_window"])
            for symbol, entries in analysis.items():
                for entry in entries:
                    exchange, mid, bid, ask, spread, vwap_bid, vwap_ask, funding = entry
                    stats.update(symbol, exchange, spread)
        else:
            stats = None
        if config.get("discover", False):
            print_arbitrage_summary(analysis)
        else:
            print_spreads(analysis, config["min_spread"], config["top"], stats)

async def interactive_loop(manager, config):
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    await loop.connect_read_pipe(lambda: asyncio.StreamReaderProtocol(reader), sys.stdin)
    print("\nInteractive mode enabled. Type 'help' for commands.\n")
    while True:
        try:
            line = await reader.readline()
            if not line:
                break
            cmd = line.decode().strip().lower()
            if not cmd:
                continue
            parts = cmd.split()
            command = parts[0]
            if command == "help":
                print("Available commands:")
                print("  add <exchange>         - add exchange")
                print("  remove <exchange>      - remove exchange")
                print("  add_symbol <symbol>    - add symbol")
                print("  remove_symbol <symbol> - remove symbol")
                print("  mode <ticker|orderbook> - switch mode")
                print("  list                   - show current exchanges and symbols")
                print("  quit / exit            - stop program")
            elif command == "add" and len(parts) == 2:
                ex = parts[1]
                await manager.add_exchange(ex)
                print(f"Added exchange: {ex}")
            elif command == "remove" and len(parts) == 2:
                ex = parts[1]
                await manager.remove_exchange(ex)
                print(f"Removed exchange: {ex}")
            elif command == "add_symbol" and len(parts) == 2:
                sym = parts[1].upper()
                await manager.add_symbol(sym)
                print(f"Added symbol: {sym}")
            elif command == "remove_symbol" and len(parts) == 2:
                sym = parts[1].upper()
                await manager.remove_symbol(sym)
                print(f"Removed symbol: {sym}")
            elif command == "mode" and len(parts) == 2:
                mode = parts[1]
                if mode not in ("ticker", "orderbook"):
                    print("Mode must be 'ticker' or 'orderbook'")
                else:
                    await manager.switch_mode(mode)
                    print(f"Switched to mode: {mode}")
            elif command == "list":
                exchanges = manager.get_current_exchanges()
                symbols = manager.get_current_symbols()
                print(f"Exchanges: {', '.join(exchanges)}")
                print(f"Symbols: {', '.join(symbols)}")
            elif command in ("quit", "exit"):
                print("Exiting interactive mode. Press Ctrl+C to stop.")
                return
            else:
                print("Unknown command. Type 'help' for list.")
        except Exception as e:
            logger.error("Interactive error: %s", e)

async def run_monitor(config):
    exchange_ids = config["exchanges"]
    symbols = config["symbols"]
    futures = config.get("futures", False)

    if config.get("discover", False) or config.get("triangular", False) or futures:
        logger.info("Discovering common symbols for %s mode...", "futures" if futures else "discover/triangular")
        if futures:
            symbols = await discover_common_futures_symbols(exchange_ids, min_exchanges=2)
        else:
            symbols = await discover_common_symbols(exchange_ids, min_exchanges=2)
        if not symbols:
            logger.error("No common symbols found. Exiting.")
            return None
        logger.info("Using %d common symbols: %s", len(symbols), symbols[:10])
        if len(symbols) > 50:
            symbols = symbols[:50]
            logger.info("Limited to 50 symbols for performance.")

    manager = PriceFetcherManager(
        exchange_ids,
        symbols,
        mode=config.get("mode", "ticker"),
        depth=config.get("orderbook_depth", 10),
        amount=config.get("orderbook_amount", 1000.0),
        futures=futures
    )
    await manager.start()
    return manager

async def run_cli_loop(manager, config):
    interactive_task = None
    if config.get("interactive", False):
        interactive_task = asyncio.create_task(interactive_loop(manager, config))
    try:
        if config["interval"] > 0:
            while True:
                await run_once_with_manager(manager, config)
                await asyncio.sleep(config["interval"])
        else:
            await asyncio.sleep(1.5)
            await run_once_with_manager(manager, config)
    finally:
        if interactive_task:
            interactive_task.cancel()
            try:
                await interactive_task
            except asyncio.CancelledError:
                pass
        await manager.stop()

async def run(args):
    config = get_config(args)
    setup_logging(config)
    manager = await run_monitor(config)
    if manager is None:
        return
    await run_cli_loop(manager, config)
