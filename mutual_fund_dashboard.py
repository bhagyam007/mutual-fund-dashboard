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

HEADERS = {"User-Agent": "Mozilla/5.0"}

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def get_fund_candidates(query):
    url = f"https://finance.yahoo.com/lookup?s={query.replace(' ', '+')}&t=mutualfund"
    res = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table")
    candidates = []
    if table:
        rows = table.find_all("tr", class_="simpTblRow")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 2:
                ticker = cols[0].text.strip()
                name = cols[1].text.strip()
                candidates.append((name, ticker))
    return candidates

def fallback_scrape_base(query):
    # Broader scrape using base part of name
    words = query.split()
    base_query = " ".join(words[:3]) if len(words) >= 3 else query
    return get_fund_candidates(base_query)

# --- Fund Explorer Tab ---
tab1, tab2, tab3 = st.tabs(["🔍 Fund Explorer", "📂 Portfolio Analyzer", "🏆 Top Fund Rankings"])

with tab1:
    st.subheader("Enter mutual fund details")
    base_name = st.text_input("Start typing fund name (e.g. Quant Mid Cap Direct Growth)", "Quant Mid Cap Direct Growth")

    candidates = get_fund_candidates(base_name)
    if not candidates:
        candidates = fallback_scrape_base(base_name)

    auto_matches = [name for name, _ in candidates if base_name.lower() in name.lower()]

    if auto_matches:
        selected_auto = st.selectbox("Auto-detected fund names:", auto_matches)
        full_selected_name = selected_auto
    else:
        st.info("No matching fund suggestions yet. Try refining your input.")
        full_selected_name = base_name

    if full_selected_name:
        cache = load_cache()
        normalized_name = full_selected_name.strip().lower()

        if normalized_name in cache:
            ticker = cache[normalized_name]
        else:
            try:
                all_names = [name for name, _ in candidates]
                matches = get_close_matches(full_selected_name.lower(), [n.lower() for n in all_names], n=5, cutoff=0.4)

                if matches:
                    match_display = [name for name, _ in candidates if name.lower() in matches]
                    selected_name = st.selectbox("Choose the correct fund:", match_display)
                    ticker = next(ticker for name, ticker in candidates if name == selected_name)
                    cache[normalized_name] = ticker
                    save_cache(cache)
                else:
                    st.error("No close match found on Yahoo Finance.")
                    ticker = None
            except Exception as e:
                st.warning(f"Could not fetch Yahoo Finance ticker: {e}")
                ticker = None

        if ticker:
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
            st.info("Please enter a valid fund name or select from suggestions.")
    else:
        st.info("Please enter a mutual fund name to begin.")
