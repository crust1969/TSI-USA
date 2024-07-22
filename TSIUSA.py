import streamlit as st
import openai
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup
import requests

# Initialize OpenAI
def initialize_openai(api_key):
    openai.api_key = api_key

# Function to get current TSI USA portfolio using web scraping
def get_tsi_usa_portfolio():
    url = "https://www.deraktionaer.de/aktien/tsi-usa"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    portfolio = []
    for item in soup.select("article"):
        try:
            stock = item.select_one("h2").text.strip()
            ticker = item.select_one("span.ticker").text.strip()
            tsi_value = item.select_one("span.tsi-value").text.strip()
            portfolio.append((stock, ticker, tsi_value))
        except AttributeError:
            continue
    
    return portfolio

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

# Button to fetch the TSI USA Portfolio
if st.sidebar.button("Fetch TSI USA Portfolio"):
    portfolio = get_tsi_usa_portfolio()
    st.session_state.portfolio = portfolio

# Display the fetched TSI USA Portfolio
if "portfolio" in st.session_state:
    st.header("Current TSI USA Portfolio")
    df_portfolio = pd.DataFrame(st.session_state.portfolio, columns=["Stock", "Ticker", "TSI Value"])
    st.write(df_portfolio)

    # Button to fetch current stock prices
    if st.sidebar.button("Fetch Current Stock Prices"):
        tickers = df_portfolio["Ticker"].tolist()
        prices = fetch_stock_prices(tickers)
        df_portfolio["Current Price"] = df_portfolio["Ticker"].map(prices)
        st.write(df_portfolio)
else:
    st.write("Click the button in the sidebar to fetch the TSI USA Portfolio.")
