import yfinance as yf
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mutual Fund Dashboard", layout="centered")

st.title("📈 Mutual Fund Recommendation Dashboard")

# --- Tab Setup ---
tab1, tab2, tab3 = st.tabs(["🔍 Fund Explorer", "📂 Portfolio Analyzer", "🏆 Top Fund Rankings"])

# --- Fund Explorer Tab ---
with tab1:
    fund_tickers = st.text_input("Enter mutual fund or ETF tickers (comma-separated)", "ICICIPRULI.NS, KOTAKBANK.NS")
    tickers = [ticker.strip() for ticker in fund_tickers.split(",") if ticker.strip()]

    if tickers:
        st.subheader("Fund Overview")
        for ticker in tickers:
            try:
                fund = yf.Ticker(ticker)
                hist = fund.history(period="1y")

                st.markdown(f"### {ticker}")
                st.write(fund.info.get("longName", "No info available"))
                st.write("**Sector:**", fund.info.get("sector", "N/A"))
                st.write("**Market Cap:**", fund.info.get("marketCap", "N/A"))
                st.write("**1Y Return (%):**", round(((hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0]) * 100, 2))

                st.write("**Price Trend (1 Year)**")
                fig, ax = plt.subplots()
                ax.plot(hist.index, hist['Close'])
                ax.set_title(f"{ticker} Price History")
                ax.set_ylabel("Price")
                ax.set_xlabel("Date")
                st.pyplot(fig)

            except Exception as e:
                st.error(f"Failed to fetch data for {ticker}: {e}")
    else:
        st.info("Please enter at least one ticker to begin.")

# --- Portfolio Analyzer Tab ---
with tab2:
    st.subheader("Upload Your Mutual Fund Portfolio")
    uploaded_file = st.file_uploader("Upload a CSV file with columns: Ticker, Amount", type="csv")

    risk_profile = st.selectbox("Select your risk profile", ["Low", "Moderate", "High"])
    horizon_years = st.slider("Select your investment horizon (in years)", 1, 10, 3)

    if uploaded_file:
        portfolio_df = pd.read_csv(uploaded_file)

        if "Ticker" not in portfolio_df.columns or "Amount" not in portfolio_df.columns:
            st.error("CSV must contain 'Ticker' and 'Amount' columns.")
        else:
            st.write("### Your Portfolio")
            st.dataframe(portfolio_df)

            results = []

            for index, row in portfolio_df.iterrows():
                ticker = row['Ticker']
                amount = row['Amount']
                try:
                    fund = yf.Ticker(ticker)
                    hist = fund.history(period="1y")
                    ret_1y = round(((hist['Close'][-1] - hist['Close'][0]) / hist['Close'][0]) * 100, 2)

                    results.append({
                        "Ticker": ticker,
                        "Invested Amount": amount,
                        "1Y Return (%)": ret_1y
                    })
                except:
                    results.append({
                        "Ticker": ticker,
                        "Invested Amount": amount,
                        "1Y Return (%)": "Error fetching data"
                    })

            result_df = pd.DataFrame(results)
            st.write("### Portfolio Performance")
            st.dataframe(result_df)

            st.markdown("---")
            st.subheader("🔁 Fund Substitution Suggestions (Based on Profile)")
            st.write(f"Based on your profile (Risk: {risk_profile}, Horizon: {horizon_years} years), here are suggestions:")

            suggestions = {
                "Low": "PARAGPARIKH.NS",
                "Moderate": "AXISBLUECHIP.NS",
                "High": "QUANTMIDCAP.NS"
            }

            for row in result_df.itertuples():
                if isinstance(row._3, (int, float)) and row._3 < 15:
                    substitute = suggestions[risk_profile]
                    st.markdown(f"**{row.Ticker}** → Consider switching to `{substitute}` (better 1Y performance and profile match)")
    else:
        st.info("Upload a CSV to see personalized analysis and suggestions.")

# --- Top Fund Rankings Tab ---
with tab3:
    st.subheader("🏆 Mock Top Fund Rankings (By Category)")
    selected_category = st.selectbox("Select Fund Category", ["Large Cap", "Mid Cap", "ELSS", "Hybrid"])

    ranking_data = {
        "Large Cap": [
            {"Fund": "AXISBLUECHIP.NS", "1Y Return (%)": 21.2, "Rating": "5★"},
            {"Fund": "HDFCLARGECAP.NS", "1Y Return (%)": 18.9, "Rating": "4★"},
            {"Fund": "ICICILARGECAP.NS", "1Y Return (%)": 17.5, "Rating": "4★"},
        ],
        "Mid Cap": [
            {"Fund": "QUANTMIDCAP.NS", "1Y Return (%)": 27.3, "Rating": "5★"},
            {"Fund": "MOTILALMIDCAP.NS", "1Y Return (%)": 23.8, "Rating": "4★"},
            {"Fund": "NIPPMIDCAP.NS", "1Y Return (%)": 22.1, "Rating": "4★"},
        ],
        "ELSS": [
            {"Fund": "MIRAEEELSS.NS", "1Y Return (%)": 19.4, "Rating": "5★"},
            {"Fund": "CANARAELSS.NS", "1Y Return (%)": 18.3, "Rating": "4★"},
            {"Fund": "QUANTELSS.NS", "1Y Return (%)": 16.9, "Rating": "4★"},
        ],
        "Hybrid": [
            {"Fund": "HDFCHYBRID.NS", "1Y Return (%)": 13.4, "Rating": "4★"},
            {"Fund": "ICICIHYBRID.NS", "1Y Return (%)": 12.1, "Rating": "3★"},
            {"Fund": "AXISHYBRID.NS", "1Y Return (%)": 11.8, "Rating": "3★"},
        ]
    }

    top_funds_df = pd.DataFrame(ranking_data[selected_category])
    st.dataframe(top_funds_df)
