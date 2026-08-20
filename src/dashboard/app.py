import streamlit as st
import requests
import pandas as pd
import time
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Crypto Spread Tracker", layout="wide")
st.title("📊 Crypto Spread Tracker – Arbitrage Opportunities")

if "last_update" not in st.session_state:
    st.session_state.last_update = None

def fetch_spreads(min_spread=0.0, top=10):
    try:
        resp = requests.get(f"{API_URL}/spreads", params={"min_spread": min_spread, "top": top})
        if resp.status_code == 200:
            return resp.json()
        else:
            st.error(f"API error: {resp.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Make sure the API server is running (python main.py --api-port 8000)")
        return None

sidebar = st.sidebar
sidebar.header("Settings")

min_spread = sidebar.slider("Min Spread %", 0.0, 5.0, 0.0, 0.1)
top = sidebar.slider("Top N", 1, 50, 10)
refresh_interval = sidebar.slider("Refresh interval (sec)", 1, 30, 5)
auto_refresh = sidebar.checkbox("Auto refresh", value=True)

view_mode = sidebar.radio("View mode", ["Summary (Buy/Sell)", "Detailed (all exchanges)"])

if sidebar.button("Refresh now"):
    st.session_state.last_update = None

if auto_refresh:
    time.sleep(0.1)

data = fetch_spreads(min_spread, top)

if data:
    st.session_state.last_update = datetime.now()
    rows = []
    for symbol, entries in data.items():
        for entry in entries:
            rows.append({
                "Symbol": symbol,
                "Exchange": entry["exchange"],
                "Price": entry["price"],
                "Spread %": entry["spread"],
                "VWAP Bid": entry.get("vwap_bid"),
                "VWAP Ask": entry.get("vwap_ask"),
                "Funding Rate": entry.get("funding_rate")
            })
    df = pd.DataFrame(rows)
    if not df.empty:
        if view_mode == "Summary (Buy/Sell)":
            summary_rows = []
            for symbol in df["Symbol"].unique():
                symbol_df = df[df["Symbol"] == symbol]
                min_price = symbol_df["Price"].min()
                max_price = symbol_df["Price"].max()
                buy_exchange = symbol_df[symbol_df["Price"] == min_price]["Exchange"].iloc[0]
                sell_exchange = symbol_df[symbol_df["Price"] == max_price]["Exchange"].iloc[0]
                spread_pct = ((max_price - min_price) / min_price) * 100
                summary_rows.append({
                    "Symbol": symbol,
                    "Buy (min price)": f"{buy_exchange} @ {min_price:.2f}",
                    "Sell (max price)": f"{sell_exchange} @ {max_price:.2f}",
                    "Spread %": spread_pct
                })
            summary_df = pd.DataFrame(summary_rows)
            summary_df = summary_df.sort_values("Spread %", ascending=False)
            st.dataframe(
                summary_df.style.background_gradient(subset=["Spread %"], cmap="RdYlGn"),
                use_container_width=True
            )
        else:
            st.dataframe(
                df.style.background_gradient(subset=["Spread %"], cmap="RdYlGn"),
                use_container_width=True
            )
    else:
        st.info("No data for the selected filters.")
else:
    st.info("No data received from API.")

st.sidebar.markdown("---")
st.sidebar.write(f"Last update: {st.session_state.last_update.strftime('%H:%M:%S') if st.session_state.last_update else 'Never'}")
