import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from difflib import get_close_matches
import requests
from bs4 import BeautifulSoup
import json
import os

st.set_page_config(page_title="Mutual Fund Dashboard", layout="centered")

st.title("📈 Mutual Fund Recommendation Dashboard")

# --- Yahoo Mutual Fund Ticker Lookup with Cache ---
CACHE_FILE = "fund_ticker_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def fetch_yahoo_ticker(fund_name, cache):
    normalized_name = fund_name.strip().lower()
    if normalized_name in cache:
        return cache[normalized_name]
    try:
        query = fund_name.replace(" ", "+")
        url = f"https://finance.yahoo.com/lookup?s={query}&t=mutualfund"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find("table")
        if table:
            first_row = table.find("tr", class_="simpTblRow")
            if first_row:
                ticker = first_row.find("td").text.strip()
                cache[normalized_name] = ticker
                save_cache(cache)
                return ticker
    except Exception as e:
        st.warning(f"Could not fetch Yahoo Finance ticker: {e}")
    return None

# --- Fund Explorer Tab ---
tab1, tab2, tab3 = st.tabs(["🔍 Fund Explorer", "📂 Portfolio Analyzer", "🏆 Top Fund Rankings"])

with tab1:
    fund_input = st.text_input("Enter mutual fund name", "Quant Small Cap Fund")

    if fund_input:
        cache = load_cache()
        ticker = fetch_yahoo_ticker(fund_input, cache)

        if ticker:
            st.success(f"Found ticker: {ticker}")
        else:
            st.error("Unable to identify this fund on Yahoo Finance.")
            ticker = None

        if ticker:
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
        st.info("Please enter a mutual fund name to begin.")

# Retain tabs 2 and 3 unchanged for now...

# [Tabs 2 and 3 remain unchanged; omitted here for brevity. They should be reinserted in full during deployment.]
