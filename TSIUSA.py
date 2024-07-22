import streamlit as st
import openai
import yfinance as yf
import pandas as pd

# Initialize OpenAI
def initialize_openai(api_key):
    openai.api_key = api_key

# Function to chat with GPT-4
def chat_with_gpt(prompt, api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a finance assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

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

# Initialize empty list to collect portfolio entries
portfolio = []

if api_key:
    initialize_openai(api_key)

    # Step-by-step chat with GPT-4 to gather portfolio entries
    st.header("Chat with GPT-4 to gather TSI USA portfolio")
    user_input = st.text_input("Your question to GPT-4:")
    if st.button("Send"):
        if user_input:
            response = chat_with_gpt(user_input, api_key)
            st.write("GPT-4 response: ", response)
            st.session_state.last_response = response
        else:
            st.write("Please enter a question.")
    
    # Option to confirm the portfolio entry
    if 'last_response' in st.session_state:
        if st.button("Add to Portfolio"):
            portfolio.append(st.session_state.last_response)
            st.session_state.last_response = None

    # Display the current portfolio
    st.header("Current Portfolio")
    for entry in portfolio:
        st.write(entry)

    # Confirm and create DataFrame
    if st.sidebar.button("Confirm Portfolio"):
        portfolio_data = [entry.split(",") for entry in portfolio]  # Assuming entries are comma-separated
        df = pd.DataFrame(portfolio_data, columns=["Stock", "Ticker"])
        st.session_state.portfolio_df = df
        st.write("Portfolio confirmed!")

    # Fetch current stock prices
    if "portfolio_df" in st.session_state and st.sidebar.button("Fetch Stock Prices"):
        tickers = st.session_state.portfolio_df['Ticker'].tolist()
        prices = fetch_stock_prices(tickers)
        st.session_state.stock_prices = prices
        
        # Display the DataFrame with current prices
        st.header("Portfolio with Current Stock Prices")
        st.session_state.portfolio_df['Current Price'] = st.session_state.portfolio_df['Ticker'].map(st.session_state.stock_prices)
        st.write(st.session_state.portfolio_df)
else:
    st.write("Please enter your OpenAI API key to start.")
