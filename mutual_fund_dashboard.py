import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from difflib import get_close_matches

st.set_page_config(page_title="Mutual Fund Recommendation Engine", layout="wide")
log_lines = []
def log_msg(msg):
    log_lines.append(msg)
    st.sidebar.text_area("📋 Debug Console", value="\n".join(log_lines), height=250, disabled=True)
st.title("🔍 Mutual Fund Analysis & Recommendation Engine")

# --- Helper functions ---
# [TRUNCATED — same working script from the canvas above]
