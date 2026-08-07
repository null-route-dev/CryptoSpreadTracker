# CryptoSpreadTracker

**CryptoSpreadTracker** is a real-time cryptocurrency arbitrage monitoring system designed to detect and visualize price differences (spreads) across multiple exchanges.

> ✅ **Project Status:** MVP in progress – basic price fetching from Binance is implemented.

---

## 🎯 About

CryptoSpreadTracker aims to provide traders and enthusiasts with a clear, actionable view of arbitrage opportunities in the cryptocurrency market. By continuously gathering and comparing prices from various trading platforms, the system highlights profitable spreads and helps users make informed decisions.

The project focuses on:
- **Real-time data** acquisition and processing.
- **User-friendly visualization** of spreads and trends.
- **Extensibility** – easy to add new exchanges or analytical modules.

---

## ✨ Planned Key Features

- **Multi-exchange price monitoring** – fetch live prices for major crypto pairs.
- **Spread detection** – calculate and rank arbitrage opportunities.
- **Historical data storage** – track spread evolution over time.
- **Interactive dashboard** – view current spreads, charts, and statistics.
- **Alert system** – receive notifications when profitable spreads appear.
- **API access** – allow external tools to consume data.

---

## 🧰 Planned Tech Stack

*This is a preliminary list and may change.*

- **Language:** Python (3.11+)
- **Data fetching:** Asynchronous HTTP/WebSocket clients
- **Backend API:** FastAPI (or Django REST Framework)
- **Database:** Time-series database (e.g., TimescaleDB/PostgreSQL) + Redis for caching
- **Frontend:** Modern JS framework (React/Vue) or lightweight dashboard (Streamlit/Gradio)
- **Containerization:** Docker & Docker Compose
- **CI/CD:** GitHub Actions
- **Orchestration/Background tasks:** Celery (or similar)

---

## 🗺️ Roadmap

- [x] **Phase 0:** Project setup, architecture design, and tech selection.
- [x] **Phase 1:** Implement basic price fetching from 2–3 exchanges.
- [x] **Phase 2:** Build spread calculation logic and a simple CLI output.
- [ ] **Phase 3:** Develop a REST API and a minimal web dashboard.
- [ ] **Phase 4:** Add historical data storage and basic charting.
- [ ] **Phase 5:** Introduce alerts (Telegram/email) and advanced analytics.
- [ ] **Phase 6:** Polish, testing, and documentation.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/)

### Installation

```bash
# Clone the repository
git clone https://github.com/null-route-dev/CryptoSpreadTracker.git
cd CryptoSpreadTracker

# Install dependencies with Poetry
poetry install

# Or with pip (if you don't use Poetry)
pip install -r requirements.txt
```

### Run the price fetcher

```bash
# With Poetry
poetry run python src/main.py

# Or directly
python src/main.py
```

### Example Output

```
📊 Spread Analysis for BTC/USDT:

Exchange     Price (USDT)    Spread (%)
----------------------------------------
binance      64686.00           +0.00%
okx          64683.60           -0.00%
----------------------------------------
Best price: binance at 64686.00 USDT
```

---

## 🤝 Contributing

At this early stage, contributions are not yet open. Once the core structure is stable, we will welcome community input. Stay tuned!

---

## 📄 License

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## 📬 Contact

For any questions or suggestions, please open an issue or reach out via [GitHub Discussions] (to be enabled).

---

*Happy spread hunting!* 🚀