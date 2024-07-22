import streamlit as st
import openai
import pandas as pd
import yfinance as yf

# Initialize OpenAI
def initialize_openai(api_key):
    openai.api_key = api_key

# Function to get current TSI USA portfolio using GPT-4
def get_tsi_usa_portfolio(api_key, previous_portfolio=None):
    initialize_openai(api_key)
    prompt = (
        "Du bist ein Finanzanalyst mit Zugriff auf alle Quellen zur Ermittlung des TSI USA Portfolios. "
        "Ermittle die aktuellen 9 Aktien des TSI USA Portfolios mit den zugehörigen TSI-Werten. "
        "Falls möglich, vergleiche das aktuelle Portfolio mit dem Vorgängerportfolio, um festzustellen, "
        "welche Werte neu aufgenommen wurden und welche herausgenommen wurden."
    )
    if previous_portfolio:
        prompt += f"\nVorheriges Portfolio: {previous_portfolio}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# Function to fetch stock prices from Yahoo Finance
def fetch_stock_prices(tickers):
    stock_data = {}
    for ticker in tickers:
        stock_info = yf.Ticker(ticker)
        stock_data[ticker] = stock_info.history(period="1d")['Close'][0]
    return stock_data

# Streamlit App
st.title("TSI USA Portfolio Assistant")

# Sidebar for API key input
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# Input for previous portfolio
previous_portfolio = st.sidebar.text_area("Vorheriges Portfolio", placeholder="Optional: Geben Sie das vorherige Portfolio ein")

# Button to fetch the TSI USA Portfolio
if st.sidebar.button("Fetch TSI USA Portfolio") and api_key:
    portfolio_info = get_tsi_usa_portfolio(api_key, previous_portfolio)
    st.session_state.portfolio_info = portfolio_info

# Display the fetched TSI USA Portfolio
if "portfolio_info" in st.session_state:
    st.header("Aktuelles TSI USA Portfolio und Änderungen")
    st.text(st.session_state.portfolio_info)

    # Parse the portfolio information to create a DataFrame
    lines = st.session_state.portfolio_info.split('\n')
    portfolio_data = []
    for line in lines:
        if 'Ticker:' in line and 'TSI-Wert:' in line:
            parts = line.split(',')
            stock = parts[0].split(':')[1].strip()
            ticker = parts[1].split(':')[1].strip()
            tsi_value = parts[2].split(':')[1].strip()
            portfolio_data.append((stock, ticker, tsi_value))
    
    df_portfolio = pd.DataFrame(portfolio_data, columns=["Stock", "Ticker", "TSI Value"])
    st.write(df_portfolio)

    # Button to fetch current stock prices
    if st.sidebar.button("Fetch Current Stock Prices"):
        tickers = df_portfolio["Ticker"].tolist()
        prices = fetch_stock_prices(tickers)
        df_portfolio["Current Price"] = df_portfolio["Ticker"].map(prices)
        st.write(df_portfolio)
else:
    st.write("Geben Sie den OpenAI API-Schlüssel ein und klicken Sie auf den Button in der Sidebar, um das TSI USA Portfolio abzurufen.")
