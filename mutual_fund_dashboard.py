import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from difflib import get_close_matches

st.set_page_config(page_title="Mutual Fund Recommendation Engine", layout="wide")
st.title("🔍 Mutual Fund Analysis & Recommendation Engine")

def fetch_groww_data(fund_name):
    search_url = f"https://groww.in/mutual-funds/search?q={fund_name.replace(' ', '%20')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        search_page = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(search_page.text, 'html.parser')
        first_link = soup.find("a", href=True)
        if not first_link:
            return None

        fund_url = "https://groww.in" + first_link['href']
        fund_page = requests.get(fund_url, headers=headers, timeout=10)
        fund_soup = BeautifulSoup(fund_page.text, 'html.parser')

        data = {}
        metric_cards = fund_soup.find_all("div", class_="styles__SubHeading-sc-6y5mnn-1")
        for card in metric_cards:
            if "1Y" in card.text:
                data['1Y'] = card.text.strip()
            elif "3Y" in card.text:
                data['3Y'] = card.text.strip()
            elif "5Y" in card.text:
                data['5Y'] = card.text.strip()

        labels = fund_soup.find_all("div", class_="styles__SubHeading-sc-6y5mnn-1")
        for lbl in labels:
            if "Expense ratio" in lbl.text:
                data['Expense Ratio'] = lbl.find_next().text.strip()
            if "Fund size" in lbl.text:
                data['AUM'] = lbl.find_next().text.strip()

        data['Fund URL'] = fund_url
        return data
    except Exception as e:
        return {"Error": str(e)}

# (Truncated for brevity. We'll write the entire content in actual script file.)
