import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from difflib import get_close_matches
import json
import os
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Mutual Fund Dashboard", layout="wide")

st.title("📈 Mutual Fund Recommendation Dashboard")

# --- Yahoo Mutual Fund Ticker Lookup with Cache ---
CACHE_FILE = "fund_ticker_cache.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Load or create master list
MASTER_LIST_FILE = "fund_master_list.json"

AMFI_URL = "https://www.amfiindia.com/spages/NAVAll.txt"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def scrape_amfi_names():
    try:
        res = requests.get(AMFI_URL, timeout=10)
        lines = res.text.splitlines()
        names = set()
        for line in lines:
            parts = line.strip().split(';')
            if len(parts) >= 4 and parts[3]:
                names.add(parts[3].strip())
        return sorted(names)
    except:
        return []

def map_amfi_to_yahoo(amfi_names):
    tickers = {}
    for name in amfi_names:
        url = f"https://finance.yahoo.com/lookup?s={name.replace(' ', '+')}&t=mutualfund"
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            table = soup.find("table")
            if table:
                for row in table.find_all("tr", class_="simpTblRow"):
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        ticker = cols[0].text.strip()
                        yahoo_name = cols[1].text.strip()
                        if name.lower() in yahoo_name.lower():
                            tickers[name] = ticker
                            break
        except:
            continue
    return tickers

def scrape_master_list():
    amfi_names = scrape_amfi_names()
    yahoo_tickers = map_amfi_to_yahoo(amfi_names)
    return yahoo_tickers

def load_master_list():
    if os.path.exists(MASTER_LIST_FILE):
        with open(MASTER_LIST_FILE, "r") as f:
            return json.load(f)
    tickers = scrape_master_list()
    with open(MASTER_LIST_FILE, "w") as f:
        json.dump(tickers, f)
    return tickers

fund_master = load_master_list()

# --- Fund Explorer Tab ---
tab1, tab2, tab3 = st.tabs(["🔍 Fund Explorer", "📂 Portfolio Analyzer", "🏆 Top Fund Rankings"])

with tab1:
    st.subheader("Enter mutual fund details")
    fund_input = st.text_input("Start typing fund name (e.g. Quant Mid Cap Direct Growth)", "Quant Mid Cap Direct Growth")

    match_display = []
    if fund_input:
        all_names = list(fund_master.keys())
        matches = get_close_matches(fund_input.lower(), [n.lower() for n in all_names], n=5, cutoff=0.3)
        match_display = [name for name in all_names if name.lower() in matches or fund_input.lower() in name.lower()]

    if match_display:
        selected_name = st.selectbox("Select from closest matches:", match_display)
        ticker = fund_master[selected_name]

        st.success(f"Using ticker: {ticker}")
        try:
            fund = yf.Ticker(ticker)
            hist = fund.history(period="10y")

            st.subheader(f"Fund: {ticker}")
            st.write(fund.info.get("longName", "No info available"))
            st.write("**Fund Type:**", fund.info.get("fundFamily", "N/A"))
            st.write("**NAV (latest):**", hist['Close'][-1])

            def calc_return(years):
                if len(hist) < years * 252:
                    return "N/A"
                past_price = hist['Close'][-1 * years * 252]
                return round(((hist['Close'][-1] - past_price) / past_price) * 100, 2)

            st.write("**1Y Return (%):**", calc_return(1))
            st.write("**3Y Return (%):**", calc_return(3))
            st.write("**5Y Return (%):**", calc_return(5))
            st.write("**10Y Return (%):**", calc_return(10))

            fig, ax = plt.subplots()
            ax.plot(hist.index, hist['Close'])
            ax.set_title(f"{ticker} NAV History (10 Years)")
            ax.set_ylabel("NAV")
            ax.set_xlabel("Date")
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Failed to fetch data for {ticker}: {e}")
    else:
        st.warning("No matching fund names found. Try using a simpler version like 'Quant Small Cap'.")

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
    st.subheader("🏆 Top Performing Mutual Funds (Across All Categories)")

    fund_names = list(fund_master.keys())
    selected_funds = st.multiselect("Select funds to compare (leave empty to view all):", fund_names)

    if selected_funds:
        selected_items = {name: fund_master[name] for name in selected_funds if name in fund_master}
    else:
        selected_items = fund_master

    records = []
    for name, ticker in selected_items.items():
        try:
            fund = yf.Ticker(ticker)
            hist = fund.history(period="10y")
            nav = hist['Close'][-1]

            def safe_return(years):
                try:
                    if len(hist) < years * 252:
                        return "N/A"
                    past = hist['Close'][-1 * years * 252]
                    return round(((nav - past) / past) * 100, 2)
                except:
                    return "N/A"

            records.append({
                "Fund Name": name,
                "Ticker": ticker,
                "NAV": nav,
                "1Y Return (%)": safe_return(1),
                "3Y Return (%)": safe_return(3),
                "5Y Return (%)": safe_return(5),
                "10Y Return (%)": safe_return(10)
            })
        except:
            continue

    if records:
        df_top = pd.DataFrame(records)
        df_top = df_top.sort_values(by="1Y Return (%)", ascending=False)
        st.dataframe(df_top.reset_index(drop=True), use_container_width=True)
    else:
        st.warning("No fund data available to display.")