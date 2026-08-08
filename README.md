# CryptoSpreadTracker

**CryptoSpreadTracker** is a real-time cryptocurrency arbitrage monitoring system designed to detect and visualize price differences (spreads) across multiple exchanges using WebSocket connections for live data streaming.

> ✅ **Project Status:** MVP – WebSocket price fetching implemented for Binance, Bybit, and Kraken.

---

## 🎯 About

CryptoSpreadTracker provides traders and enthusiasts with a clear, actionable view of arbitrage opportunities in the cryptocurrency market. By continuously gathering and comparing prices from various trading platforms via WebSocket connections, the system highlights profitable spreads and helps users make informed decisions in real-time.

The project focuses on:
- **Real-time data** acquisition via WebSocket streaming.
- **Low-latency** price updates.
- **User-friendly visualization** of spreads directly in the CLI.
- **Extensibility** – easy to add new exchanges by implementing a simple interface.

---

## ✨ Current Features

- ✅ **Multi-exchange price monitoring** via WebSocket (Binance, Bybit, Kraken)
- ✅ **Real-time spread analysis** – calculate and rank arbitrage opportunities
- ✅ **Flexible filtering** – filter by minimum spread and top N opportunities
- ✅ **CLI interface** with colored output for easy reading
- ✅ **Configurable** via command-line arguments or `.env` file
- ✅ **Async architecture** for efficient concurrent data fetching

### Planned Features

- [ ] Interactive dashboard – view current spreads, charts, and statistics
- [ ] Alert system – receive notifications when profitable spreads appear
- [ ] API access – allow external tools to consume data
- [ ] Support for more exchanges (OKX, KuCoin, etc.)

---

## 🧰 Tech Stack

- **Language:** Python 3.12+
- **Data fetching:** WebSocket (via `websockets` library)
- **CLI interface:** `argparse` + `colorama` for colored output
- **Configuration:** `python-dotenv` for environment variables
- **Package management:** Poetry / pip

---

## 🗺️ Roadmap

- [x] **Phase 0:** Project setup, architecture design, and tech selection.
- [x] **Phase 1:** Implement basic price fetching from exchanges.
- [x] **Phase 2:** Build spread calculation logic and CLI output.
- [ ] **Phase 3:** Develop a REST API and a minimal web dashboard.
- [ ] **Phase 5:** Introduce alerts (Telegram/email) and advanced analytics.
- [ ] **Phase 6:** Add support for more exchanges (OKX, KuCoin, etc.)
- [ ] **Phase 7:** Polish, testing, and documentation.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Poetry (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/null-route-dev/CryptoSpreadTracker.git
cd CryptoSpreadTracker

# Install dependencies with Poetry
poetry install

# Or with pip
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root (optional):

```env
EXCHANGES=binance,bybit,kraken
SYMBOLS=BTC/USDT,ETH/USDT
LOG_LEVEL=INFO
```

### Usage

```bash
# Single run with default settings
python main.py

# Continuous monitoring every 5 seconds
python main.py -i 5

# Custom exchanges and symbols
python main.py -e binance,kraken -s BTC/USDT,SOL/USDT

# Filter by minimum spread and show top 3 opportunities
python main.py --min-spread 0.5 --top 3

# Show all available options
python main.py --help
```

### Example Output

```
📊 Spread Analysis for BTC/USDT:

Exchange     Price (USDT)    Spread (%)
----------------------------------------
binance      64686.00           +0.00%
bybit        64683.60           -0.00%
kraken       64680.50           -0.01%
----------------------------------------
Best price: binance at 64686.00 USDT

📊 Spread Analysis for ETH/USDT:

Exchange     Price (USDT)    Spread (%)
----------------------------------------
kraken       3456.78           +0.00%
binance      3455.90           -0.03%
bybit        3454.20           -0.07%
----------------------------------------
Best price: kraken at 3456.78 USDT
```

---

## 🔌 Adding New Exchanges

To add support for a new exchange:

1. Create a new class inheriting from `WebSocketPriceFetcher` in `websocket_fetcher.py`.
2. Implement the required methods:
   - `get_ws_url()` – WebSocket endpoint URL
   - `get_subscription_message()` – subscription payload
   - `parse_price()` – extract price from incoming messages
3. Register the class in `EXCHANGE_FETCHER_MAP` in `fetcher.py`.

Example for OKX:
```python
class OkxWebSocketFetcher(WebSocketPriceFetcher):
    def get_ws_url(self) -> str:
        return "wss://ws.okx.com:8443/ws/v5/public"
    # ... implement other methods
```

---

## 📁 Project Structure

```
CryptoSpreadTracker/
├── main.py              # Entry point
├── src/
│   ├── cli.py           # CLI orchestration
│   ├── config.py        # Configuration management
│   ├── fetcher.py       # Exchange data fetching
│   ├── analyzer.py      # Spread calculation logic
│   ├── display.py       # Output formatting
│   └── websocket_fetcher.py  # WebSocket clients for exchanges
├── .env.example         # Example environment variables
├── pyproject.toml       # Project configuration
├── README.md            # This file
└── LICENSE              # MIT License
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
