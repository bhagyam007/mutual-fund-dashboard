
import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from difflib import get_close_matches
import json
import os
import requests
from bs4 import BeautifulSoup
import traceback

st.set_page_config(page_title="Mutual Fund Dashboard", layout="wide")

st.title("📈 Mutual Fund Recommendation Dashboard")

# Console logger
log_area = st.sidebar.expander("🛠️ Console / Logs", expanded=False)

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
    except Exception as e:
        log_area.write("[AMFI Scrape Error] " + str(e))
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
        except Exception as e:
            log_area.write(f"[Yahoo Lookup Error for {name}] {e}")
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

with st.spinner("🔄 Initializing fund database from AMFI and Yahoo Finance..."):
    try:
        fund_master = load_master_list()
        st.success(f"✅ Loaded {len(fund_master)} mutual funds.")
    except Exception as e:
        log_area.write("[Initialization Error] " + str(e))
        log_area.write(traceback.format_exc())
