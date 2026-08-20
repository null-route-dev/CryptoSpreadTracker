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

def fetch_fees():
    try:
        resp = requests.get(f"{API_URL}/fees")
        if resp.status_code == 200:
            data = resp.json()
            fees_dict = data.get("fees", {})
            return ",".join([f"{ex}:{fee}" for ex, fee in fees_dict.items()])
        else:
            return ""
    except:
        return ""

def fetch_spreads(min_spread=0.0, top=10, include_fees=False, fees_str=""):
    try:
        params = {"min_spread": min_spread, "top": top}
        if include_fees:
            params["include_fees"] = True
            if fees_str:
                params["fees"] = fees_str
        resp = requests.get(f"{API_URL}/spreads", params=params)
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

default_fees = fetch_fees()
fees_input = sidebar.text_input("Fees (exchange:fee, e.g. binance:0.1,bybit:0.075)", value=default_fees)
include_fees = bool(fees_input.strip())

if sidebar.button("Refresh now"):
    st.session_state.last_update = None

if auto_refresh:
    time.sleep(0.1)

data = fetch_spreads(min_spread, top, include_fees, fees_input)

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
                "Net Spread %": entry.get("net_spread"),
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
                net_spread = None
                if include_fees:
                    net_rows = symbol_df[symbol_df["Net Spread %"].notna()]
                    if not net_rows.empty:
                        net_spread = net_rows["Net Spread %"].mean()
                summary_rows.append({
                    "Symbol": symbol,
                    "Buy": f"{buy_exchange} @ {min_price:.2f}",
                    "Sell": f"{sell_exchange} @ {max_price:.2f}",
                    "Spread %": spread_pct,
                    "Net Spread %": net_spread if include_fees else None
                })
            summary_df = pd.DataFrame(summary_rows)
            summary_df = summary_df.sort_values("Spread %", ascending=False)
            if include_fees:
                st.dataframe(
                    summary_df.style.background_gradient(subset=["Spread %", "Net Spread %"], cmap="RdYlGn"),
                    width="stretch"
                )
            else:
                st.dataframe(
                    summary_df.style.background_gradient(subset=["Spread %"], cmap="RdYlGn"),
                    width="stretch"
                )
        else:
            df = df.sort_values("Spread %", ascending=False)
            if include_fees:
                st.dataframe(
                    df.style.background_gradient(subset=["Spread %", "Net Spread %"], cmap="RdYlGn"),
                    width="stretch"
                )
            else:
                st.dataframe(
                    df.style.background_gradient(subset=["Spread %"], cmap="RdYlGn"),
                    width="stretch"
                )
    else:
        st.info("No data for the selected filters.")
else:
    st.info("No data received from API.")

st.sidebar.markdown("---")
st.sidebar.write(f"Last update: {st.session_state.last_update.strftime('%H:%M:%S') if st.session_state.last_update else 'Never'}")
