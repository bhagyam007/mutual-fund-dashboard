
import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from difflib import get_close_matches

st.set_page_config(page_title="Mutual Fund Dashboard", layout="centered")

st.title("📈 Mutual Fund Recommendation Dashboard")

# --- Known Fund Ticker Mapping ---
known_funds = {
    "Quant Mid Cap Fund Direct Growth": "QUANTMIDCAP.NS",
    "Axis Bluechip Fund Direct Growth": "AXISBLUECHIP.NS",
    "Parag Parikh Flexi Cap Fund": "PARAGPARIKH.NS",
    "Mirae Asset ELSS": "MIRAEEELSS.NS",
    "HDFC Large Cap Fund": "HDFCLARGECAP.NS",
    "ICICI Large Cap Fund": "ICICILARGECAP.NS"
}

# --- Fund Explorer Tab ---
tab1, tab2, tab3 = st.tabs(["🔍 Fund Explorer", "📂 Portfolio Analyzer", "🏆 Top Fund Rankings"])

with tab1:
    fund_input = st.text_input("Enter mutual fund name or ticker", "Quant Mid Cap Fund Direct Growth")

    if fund_input:
        ticker = known_funds.get(fund_input)

        # If not found, suggest closest match
        if not ticker:
            close_matches = get_close_matches(fund_input, known_funds.keys(), n=3, cutoff=0.4)
            if close_matches:
                st.warning("Did you mean:")
                ticker = st.selectbox("Select a matching fund", close_matches)
                ticker = known_funds.get(ticker)
            else:
                st.error("No close matches found. Try a different name.")
                ticker = None

        if ticker:
            try:
                fund = yf.Ticker(ticker)
                hist = fund.history(period="1y")

                st.subheader(f"Fund: {ticker}")
                st.write(fund.info.get("longName", "No info available"))
                st.write("**Sector:**", fund.info.get("sector", "N/A"))
                st.write("**Market Cap:**", fund.info.get("marketCap", "N/A"))
                st.write("**1Y Return (%):**", round(((hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0]) * 100, 2))

                fig, ax = plt.subplots()
                ax.plot(hist.index, hist['Close'])
                ax.set_title(f"{ticker} Price History")
                ax.set_ylabel("Price")
                ax.set_xlabel("Date")
                st.pyplot(fig)

            except Exception as e:
                st.error(f"Failed to fetch data for {ticker}: {e}")

    else:
        st.info("Please enter a mutual fund name or ticker to begin.")

# Retain tabs 2 and 3 unchanged for now...

# [Tabs 2 and 3 remain unchanged; omitted here for brevity. They should be reinserted in full during deployment.]
