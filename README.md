# CryptoSpreadTracker

**CryptoSpreadTracker** is a real‑time cryptocurrency arbitrage monitoring system that detects and visualises price differences (spreads) across multiple exchanges, including order‑book depth, VWAP, triangular arbitrage, perpetual futures, and a REST/WebSocket API.

> ✅ **Project Status:** Feature‑rich – WebSocket streaming, order‑book analysis, VWAP, triangular arbitrage, perpetual futures, interactive CLI, and full API are implemented.

---

## 🎯 About

CryptoSpreadTracker connects to exchanges via WebSocket, fetches live prices (ticker, order‑book depth, or perpetual futures), and computes:

- **Spread analysis** – rank arbitrage opportunities between exchanges.
- **VWAP** (Volume‑Weighted Average Price) for realistic execution prices.
- **Triangular arbitrage** – detect profitable cycles within a single exchange.
- **Cross‑exchange arbitrage summary** – find the best place to buy and sell each asset.
- **Perpetual futures monitoring** – track futures prices and funding rates across Binance, Bybit, and OKX.
- **Statistics** – track average, min, max, and standard deviation of spreads.

All data is available through a **CLI** with rich tables, an **interactive mode** for runtime control, and a **FastAPI** server with WebSocket streams for external integration.

---

## ✨ Current Features

- ✅ **Multi‑exchange WebSocket streaming** – Binance, Bybit, Kraken, OKX, KuCoin, Gate.io, Huobi, Bitget, MEXC (spot) + Binance, Bybit, OKX (futures).
- ✅ **Two data modes**: `ticker` (last price) and `orderbook` (depth levels).
- ✅ **VWAP calculation** – average price for a given amount (USDT) using order‑book liquidity.
- ✅ **Spread analysis** – rank opportunities across exchanges, filter by min spread and top N.
- ✅ **Automatic symbol discovery** (`--discover`) – finds common trading pairs across all selected exchanges and shows a buy/sell summary.
- ✅ **Triangular arbitrage** (`--triangular`) – detects profitable cycles within each exchange.
- ✅ **Perpetual futures** (`--futures`) – monitors futures prices and funding rates (Binance, Bybit, OKX).
- ✅ **Spread statistics** (`--stats-window`) – average, min, max, standard deviation over last N updates.
- ✅ **Interactive CLI** (`--interactive`) – add/remove exchanges and symbols, switch modes on the fly.
- ✅ **REST API** (`--api-port`) – endpoints for spreads, triangular opportunities, futures, exchanges, symbols, health.
- ✅ **WebSocket API** – real‑time streaming of spreads, arbitrage summary, triangular opportunities, and futures data.
- ✅ **Flexible configuration** – via CLI arguments, `.env` file, or YAML config (`config.yaml`).
- ✅ **Logging** – console and file (with rotation) support.

---

## 🧰 Tech Stack

- **Language:** Python 3.12+
- **Data fetching:** WebSocket (`websockets`), REST (`httpx`)
- **CLI & tables:** `argparse`, `rich`
- **Configuration:** `python-dotenv`, `pyyaml`
- **API:** `FastAPI`, `uvicorn`
- **Package management:** Poetry / pip / uv

---

## 🗺️ Roadmap

- [x] Phase 0 – Project setup & architecture.
- [x] Phase 1 – WebSocket ticker fetching (Binance, Bybit, Kraken).
- [x] Phase 2 – Spread analysis & CLI output.
- [x] Phase 3 – Order‑book depth & VWAP.
- [x] Phase 4 – Triangular arbitrage detection.
- [x] Phase 5 – Interactive CLI & runtime control.
- [x] Phase 6 – FastAPI + WebSocket API.
- [x] Phase 7 – Additional exchanges (OKX, KuCoin, Gate.io, Huobi, Bitget, MEXC).
- [x] Phase 8 – Perpetual futures support with funding rates.
- [ ] Phase 9 – Dashboard (Streamlit / Gradio) and alert system (Telegram/Email).
- [ ] Phase 10 – Advanced analytics (correlation, volatility, etc.).

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Poetry (recommended) or pip / uv

### Installation

```bash
# Clone the repository
git clone https://github.com/null-route-dev/CryptoSpreadTracker.git
cd CryptoSpreadTracker

# Install dependencies with Poetry
poetry install

# Or with pip
pip install -r requirements.txt

# Or with uv
uv pip install -r requirements.txt
```

### Configuration (optional)

Create a `.env` file:

```env
EXCHANGES=binance,bybit,kraken,okx
SYMBOLS=BTC/USDT,ETH/USDT,SOL/USDT
LOG_LEVEL=INFO
MODE=ticker
ORDERBOOK_DEPTH=10
ORDERBOOK_AMOUNT=1000
STATS_WINDOW=0
DISCOVER=false
INTERACTIVE=false
TRIANGULAR=false
FUTURES=false
```

Or use a `config.yaml` file (see example below).

---

## 📖 Usage Examples

### Basic ticker monitoring

```bash
python main.py -e binance,bybit,kraken -s BTC/USDT,ETH/USDT -i 5
```

### Order‑book mode with VWAP

```bash
python main.py -e binance,bybit,kraken,okx --mode orderbook --orderbook-depth 15 --orderbook-amount 2000 -i 5
```

### Automatic symbol discovery + arbitrage summary

```bash
python main.py --discover -e binance,bybit,kraken,okx,kucoin -i 10
```

### Triangular arbitrage detection

```bash
python main.py --triangular --triangular-min-profit 0.3 -e binance,bybit,okx -i 10
```

### Perpetual futures monitoring

```bash
python main.py --futures --discover -e binance,bybit,okx -i 5
```

### With spread statistics (last 30 updates)

```bash
python main.py --stats-window 30 --discover -e binance,bybit,kraken -i 5
```

### Interactive mode (runtime control)

```bash
python main.py --interactive -i 5 -e binance,bybit,kraken
```

While running, type commands like:
- `add okx`
- `remove kraken`
- `add_symbol SOL/USDT`
- `mode orderbook`
- `list`
- `quit`

### With REST API + WebSocket streaming

```bash
python main.py --api-port 8000 --discover -i 5 -e binance,bybit,kraken
```

Then connect to:
- `http://localhost:8000/spreads?min_spread=0.5&top=3`
- `http://localhost:8000/triangular?min_profit=0.2`
- `http://localhost:8000/futures` (if `--futures` enabled)
- WebSocket `ws://localhost:8000/ws/spreads` (spread updates)
- WebSocket `ws://localhost:8000/ws/arbitrage` (buy/sell summary)
- WebSocket `ws://localhost:8000/ws/triangular` (triangular opportunities)
- WebSocket `ws://localhost:8000/ws/futures` (futures data)

---

## 📊 Example Outputs

### Spread analysis (ticker mode)

```
📊 Spread Analysis for BTC/USDT
┏━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Exchange ┃         Bid  ┃      Ask ┃      Mid ┃  Spread % ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ binance  │     64686.00 │ 64686.00 │ 64686.00 │    +0.00% │
│ bybit    │     64683.60 │ 64683.60 │ 64683.60 │    -0.00% │
│ kraken   │     64680.50 │ 64680.50 │ 64680.50 │    -0.01% │
└──────────┴──────────────┴──────────┴──────────┴───────────┘
Best mid price: binance at 64686.00 USDT
```

### Arbitrage summary (with `--discover`)

```
🔄 Arbitrage Opportunities (Buy Low / Sell High)
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Symbol     ┃ Buy (min price)      ┃ Sell (max price)     ┃ Spread %  ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ BTC/USDT   │ bybit @ 64683.60     │ binance @ 64686.00   │  +0.0037% │
│ ETH/USDT   │ kraken @ 3456.78     │ binance @ 3457.90    │  +0.0324% │
└────────────┴──────────────────────┴──────────────────────┴───────────┘
```

### Triangular arbitrage (with `--triangular`)

```
🔺 Triangular Arbitrage Opportunities
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Exchange   ┃ Path                        ┃ Profit %  ┃ Price1    ┃ Price2    ┃ Price3    ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━┩
│ binance    │ USDT → BTC → ETH → USDT    │  +0.12%   │ 64686.00  │ 0.0534    │ 3457.90   │
│ bybit      │ USDT → BTC → ETH → USDT    │  +0.09%   │ 64683.60  │ 0.0533    │ 3456.78   │
└────────────┴────────────────────────────┴───────────┴───────────┴───────────┴───────────┘
```

### Order‑book mode with VWAP

```
📊 Spread Analysis for BTC/USDT
┏━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Exchange ┃    VWAP Bid  ┃   VWAP Ask   ┃      Mid ┃  Spread % ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ binance  │     64685.90 │     64686.10 │ 64686.00 │    +0.00% │
│ bybit    │     64683.50 │     64683.70 │ 64683.60 │    -0.00% │
└──────────┴──────────────┴──────────────┴──────────┴───────────┘
```

### Perpetual futures summary (with `--futures`)

```
🔮 Futures Arbitrage Summary
┏━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Symbol   ┃ Exchange ┃ Price ┃  Spread % ┃ Funding % ┃
┡━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━┩
│ BTC/USDT │ binance  │ 65000 │    +0.00% │  +0.0100% │
│ BTC/USDT │ bybit    │ 64980 │    -0.03% │  +0.0105% │
│ BTC/USDT │ okx      │ 64990 │    -0.02% │  +0.0098% │
│ ETH/USDT │ binance  │  3500 │    +0.00% │  +0.0200% │
│ ETH/USDT │ bybit    │  3498 │    -0.06% │  +0.0205% │
│ ETH/USDT │ okx      │  3499 │    -0.03% │  +0.0195% │
└──────────┴──────────┴───────┴───────────┴───────────┘
```

---

## 🔌 Adding New Exchanges

To add a new exchange:

1. **Ticker support** – create a class inheriting from `WebSocketPriceFetcher` in `websocket_fetcher.py` and implement `get_ws_url()`, `get_subscription_message()`, `parse_price()`. Then add it to `TICKER_MAP` in `fetcher.py`.

2. **Order‑book support** – create a class inheriting from `OrderBookFetcher` and implement the same methods, plus `parse_orderbook()`. Add it to `ORDERBOOK_MAP`.

3. **Symbol discovery** – add an async function in `symbol_fetcher.py` that returns a list of USDT pairs, and add it to `SYMBOL_FETCHERS` dictionary.

4. **Futures support** – for perpetual futures, add ticker and funding rate classes (similar to `BinanceFuturesTickerFetcher`), and add symbol discovery to `FUTURES_SYMBOL_FETCHERS`.

Example for a new exchange:
```python
class NewExchangeFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://api.newexchange.com/ws"
    def get_subscription_message(self, symbols):
        return {"subscribe": symbols}
    def parse_price(self, data):
        # parse and return {symbol: price}
        return {}
```

---

## 📁 Project Structure

```
CryptoSpreadTracker/
├── main.py                  # Entry point with argument parsing
├── config.yaml              # Example YAML configuration
├── .env                     # Environment variables
├── pyproject.toml           # Project metadata and dependencies
├── README.md                # This file
├── LICENSE                  # MIT License
├── src/
│   ├── cli.py               # CLI orchestration and main loop
│   ├── config.py            # Configuration loader (calls config_loader)
│   ├── config_loader.py     # Merges CLI, .env, and YAML
│   ├── fetcher.py           # PriceFetcherManager and exchange maps
│   ├── websocket_fetcher.py # All WebSocket client classes (ticker, orderbook, futures)
│   ├── symbol_fetcher.py    # REST API functions for symbol discovery (spot + futures)
│   ├── analyzer.py          # Spread and triangular logic
│   ├── display.py           # Rich table printing (spreads, summary, triangular, futures)
│   ├── stats.py             # SpreadStats class for sliding window statistics
│   └── api.py               # FastAPI app with REST and WebSocket endpoints
└── tests/                   # (future)
```

---

## 🤝 Contributing

At this early stage, contributions are not yet open. Once the core structure is stable, we will welcome community input. Stay tuned!

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## 📬 Contact

For any questions or suggestions, please open an issue or reach out via [GitHub Discussions](https://github.com/null-route-dev/CryptoSpreadTracker/discussions).

---

*Happy spread hunting!* 🚀
```
