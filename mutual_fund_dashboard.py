
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

def fetch_groww_data(fund_name):
    log_msg(f"Fetching Groww data for: {fund_name}")
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

def fetch_moneycontrol_data(fund_name):
    log_msg(f"Fetching Moneycontrol data for: {fund_name}")
    try:
        search_url = f"https://www.moneycontrol.com/mutual-funds/search/?searchstr={fund_name.replace(' ', '%20')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        rating = soup.find("span", class_="mct_rating_star")
        risk_tag = soup.find(text="Riskometer")
        risk = risk_tag.find_next("span").text.strip() if risk_tag else "N/A"

        returns = {"MC 1Y": "N/A", "MC 3Y": "N/A", "MC 5Y": "N/A"}
        return_table = soup.find("table", class_="performanceTbl")
        if return_table:
            for row in return_table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 2:
                    label, value = cols[0].text.strip(), cols[1].text.strip()
                    if "1 year" in label.lower():
                        returns["MC 1Y"] = value
                    elif "3 year" in label.lower():
                        returns["MC 3Y"] = value
                    elif "5 year" in label.lower():
                        returns["MC 5Y"] = value

        return {"MC Rating": rating.text.strip() if rating else "N/A", "MC Risk": risk, **returns}
    except:
        return {}

def fetch_value_research_data(fund_name):
    log_msg(f"Fetching Value Research data for: {fund_name}")
    try:
        search_url = f"https://www.valueresearchonline.com/funds/fundSelector/default.asp?search={fund_name.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        rating = soup.find("div", class_="rating-stars")
        category = soup.find("div", class_="snapshotTitle")
        risk = soup.find("span", class_="riskLabel")

        returns = {"VR 1Y": "N/A", "VR 3Y": "N/A", "VR 5Y": "N/A"}
        return_table = soup.find("table", class_="snapshot-performance")
        if return_table:
            for row in return_table.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 2:
                    label, value = cols[0].text.strip(), cols[1].text.strip()
                    if "1 year" in label.lower():
                        returns["VR 1Y"] = value
                    elif "3 year" in label.lower():
                        returns["VR 3Y"] = value
                    elif "5 year" in label.lower():
                        returns["VR 5Y"] = value

        return {
            "VR Rating": rating['title'] if rating and rating.has_attr('title') else "N/A",
            "VR Category": category.text.strip() if category else "N/A",
            "VR Risk": risk.text.strip() if risk else "N/A",
            **returns
        }
    except:
        return {}

def fetch_additional_sources(fund_name):
    return {"Additional Source": "N/A"}

def suggest_alternatives(category, y3_return):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        mock_funds = [
            ("Axis Midcap Fund", 20.3),
            ("Mirae Emerging Bluechip", 18.7),
            ("Canara Robeco Small Cap", 17.2)
        ]
        return [f"{name} ({ret}% 3Y)" for name, ret in mock_funds if ret > y3_return]
    except:
        return ["⚠️ Unable to fetch suggestions"]

# --- UI ---

fund_base = st.text_input("Enter Mutual Fund Name")
fund_type = st.selectbox("Select Plan Type", ["Direct", "Regular"])
fund_option = st.selectbox("Select Option", ["Growth", "IDCW"])
fund_name = f"{fund_base.strip()} {fund_type.strip()} {fund_option.strip()}".strip()

if fund_base.strip():
    log_msg("🟡 Starting data fetch and analysis...")
    with st.spinner("Fetching real-time data and analyzing fund..."):
        formatted_name = fund_name.replace("  ", " ").strip()
        groww_data = fetch_groww_data(formatted_name)
        mc_data = fetch_moneycontrol_data(formatted_name)
        vr_data = fetch_value_research_data(formatted_name)
        add_data = fetch_additional_sources(formatted_name)

        if not groww_data or "Error" in groww_data:
            st.warning("🔎 No exact match found. Try one of the suggestions:")
            suggestions = get_close_matches(fund_name, [
                "Quant Mid Cap Fund Direct Growth",
                "Mirae Asset Tax Saver Fund Direct Growth",
                "SBI Small Cap Fund Direct Growth",
                "ICICI Prudential Bluechip Fund Direct Growth"
            ], n=5, cutoff=0.4)
            for s in suggestions:
                st.markdown(f"- {s}")
        else:
            st.subheader("📊 Fund Snapshot")
            st.markdown(f"[🌐 View on Groww]({groww_data['Fund URL']})")
            all_data = {**groww_data, **mc_data, **vr_data, **add_data}
            st.table(pd.DataFrame.from_dict(all_data, orient='index', columns=['Value']))

            st.subheader("✅ Verdict")
            try:
                groww_y3 = float(groww_data.get('3Y', '0').replace('%','')) if '3Y' in groww_data else 0
                vr_score = 5 if vr_data.get("VR Rating") == "5 Star" else 3 if vr_data.get("VR Rating") == "4 Star" else 1
                mc_score = 5 if mc_data.get("MC Rating") == "5 Star" else 3 if mc_data.get("MC Rating") == "4 Star" else 1
                overall_score = (groww_y3 * 0.4) + (vr_score * 3 * 0.3) + (mc_score * 3 * 0.3)

                category = vr_data.get("VR Category", "Mid Cap")

                if overall_score < 12:
                    st.error("❌ Recommendation: SELL")
                    st.write("Suggested Alternatives:")
                    for alt in suggest_alternatives(category, groww_y3):
                        st.markdown(f"- {alt}")
                elif overall_score < 15:
                    st.warning("🟡 Recommendation: HOLD")
                    st.write("Monitor performance quarterly.")
                else:
                    st.success("✅ Recommendation: BUY")
                    st.write("This fund is performing well in its category.")
            except:
                st.warning("⚠️ Not enough data for a verdict.")

st.sidebar.markdown("---")
st.sidebar.markdown("ℹ️ Data sources: Groww, Moneycontrol, Value Research")
