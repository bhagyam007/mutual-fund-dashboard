
import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from difflib import get_close_matches
import json
import os
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Mutual Fund Dashboard", layout="centered")

st.title("📈 Mutual Fund Recommendation Dashboard")

# --- Yahoo Mutual Fund Ticker Lookup with Cache ---
CACHE_FILE = "fund_ticker_cache.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def search_yahoo_tickers(query):
    url = f"https://finance.yahoo.com/lookup?s={query.replace(' ', '+')}&t=mutualfund"
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")
        results = []
        if table:
            for row in table.find_all("tr", class_="simpTblRow"):
                cols = row.find_all("td")
                if len(cols) >= 2:
                    ticker = cols[0].text.strip()
                    name = cols[1].text.strip()
                    results.append((name, ticker))
        return results
    except:
        return []

# --- Fund Explorer Tab ---
tab1, tab2, tab3 = st.tabs(["🔍 Fund Explorer", "📂 Portfolio Analyzer", "🏆 Top Fund Rankings"])

with tab1:
    st.subheader("Enter mutual fund details")
    fund_input = st.text_input("Start typing fund name (e.g. Quant Mid Cap Direct Growth)", "Quant Mid Cap Direct Growth")

    results = search_yahoo_tickers(fund_input)

    if not results:
        words = fund_input.split()
        fallback_query = " ".join(words[:2]) if len(words) >= 2 else fund_input
        results = search_yahoo_tickers(fallback_query)

    match_display = [name for name, _ in results if fund_input.lower() in name.lower()]

    if not match_display and results:
        all_names = [name for name, _ in results]
        matches = get_close_matches(fund_input.lower(), [n.lower() for n in all_names], n=5, cutoff=0.4)
        match_display = [name for name in all_names if name.lower() in matches]

    if match_display:
        selected_name = st.selectbox("Select from closest matches:", match_display)
        ticker = next(ticker for name, ticker in results if name == selected_name)

        # Cache the match
        cache = load_cache()
        normalized_name = selected_name.strip().lower()
        cache[normalized_name] = ticker
        save_cache(cache)

        st.success(f"Using ticker: {ticker}")
        try:
            fund = yf.Ticker(ticker)
            hist = fund.history(period="1y")

            st.subheader(f"Fund: {ticker}")
            st.write(fund.info.get("longName", "No info available"))
            st.write("**Fund Type:**", fund.info.get("fundFamily", "N/A"))
            st.write("**NAV (latest):**", hist['Close'][-1])
            st.write("**1Y Return (%):**", round(((hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0]) * 100, 2))

            fig, ax = plt.subplots()
            ax.plot(hist.index, hist['Close'])
            ax.set_title(f"{ticker} NAV History (1 Year)")
            ax.set_ylabel("NAV")
            ax.set_xlabel("Date")
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Failed to fetch data for {ticker}: {e}")
    else:
        st.warning("No matching fund names found. Please refine input.")

# --- Portfolio Analyzer Tab ---
with tab2:
    st.subheader("📂 Analyze Your Portfolio")
    uploaded_file = st.file_uploader("Upload your mutual fund CSV file", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("Your uploaded portfolio:", df)
        if "Fund Name" in df.columns:
            st.info("🔄 Recommendation engine coming soon to suggest better performing alternatives.")
        else:
            st.warning("CSV must contain a 'Fund Name' column.")

# --- Top Fund Rankings Tab ---
with tab3:
    st.subheader("🏆 Top Performing Mutual Funds")
    top_funds = {
        "Quant Small Cap Fund": "0P0000XW4X.BO",
        "Axis Bluechip Fund": "0P0000XW3Y.BO",
        "Parag Parikh Flexi Cap": "0P0000XW4Z.BO"
    }
    selected = st.selectbox("Choose a top fund to view details", list(top_funds.keys()))
    if selected:
        ticker = top_funds[selected]
        try:
            fund = yf.Ticker(ticker)
            hist = fund.history(period="1y")
            st.write("**NAV (latest):**", hist['Close'][-1])
            st.write("**1Y Return (%):**", round(((hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0]) * 100, 2))
            fig, ax = plt.subplots()
            ax.plot(hist.index, hist['Close'])
            ax.set_title(f"{ticker} NAV History (1 Year)")
            ax.set_ylabel("NAV")
            ax.set_xlabel("Date")
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Failed to fetch data for {ticker}: {e}")
