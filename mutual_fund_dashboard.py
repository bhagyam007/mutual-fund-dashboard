import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from difflib import get_close_matches

st.set_page_config(page_title="Mutual Fund Recommendation Engine", layout="wide")
st.title("🔍 Mutual Fund Analysis & Recommendation Engine")

# --- Helper functions ---

def fetch_groww_data(fund_name):
    try:
        search_url = f"https://groww.in/mutual-funds/search?q={fund_name.replace(' ', '%20')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        search_page = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(search_page.text, 'html.parser')
        first_link = soup.find("a", href=True)
        if not first_link:
            return None

        fund_url = "https://groww.in" + first_link['href']
        fund_page = requests.get(fund_url, headers=headers, timeout=10)
        fund_soup = BeautifulSoup(fund_page.text, 'html.parser')

        data = {}
        metrics = fund_soup.find_all("div", class_="styles__SubHeading-sc-6y5mnn-1")
        for m in metrics:
            if "1Y" in m.text:
                data['1Y'] = m.text.strip()
            elif "3Y" in m.text:
                data['3Y'] = m.text.strip()
            elif "5Y" in m.text:
                data['5Y'] = m.text.strip()
            elif "Expense ratio" in m.text:
                data['Expense Ratio'] = m.find_next().text.strip()
            elif "Fund size" in m.text:
                data['AUM'] = m.find_next().text.strip()

        data['Fund URL'] = fund_url
        return data
    except:
        return {}

# [TRUNCATED FOR SPACE — assumes full script pasted here]
