import streamlit as st
import openai
import pandas as pd

# Initialize OpenAI
def initialize_openai(api_key):
    openai.api_key = api_key

# Funktion zur Ermittlung des aktuellen TSI USA Portfolios mit LLM
def get_current_tsi_usa_portfolio(api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du bist ein Finanzexperte."},
            {"role": "user", "content": "Ermittle das aktuelle TSI USA Portfolio und zeige an, welche Werte im Vergleich zum Portfolio vorher hinzugefügt wurden und welche entfernt wurden."}
        ]
    )
    return response['choices'][0]['message']['content']

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
    user_input = st.text_input("Ihre Frage an GPT-4:")
    if st.button("Senden"):
        if user_input:
            response = get_current_tsi_usa_portfolio(user_input, api_key)
            st.write("GPT-4 Antwort: ", response)
            st.session_state.last_response = response
        else:
            st.write("Bitte geben Sie eine Frage ein.")
    
    # Option to confirm the portfolio entry
    if 'last_response' in st.session_state:
        if st.button("Zum Portfolio hinzufügen"):
            portfolio.append(st.session_state.last_response)
            st.session_state.last_response = None

    # Display the current portfolio
    st.header("Aktuelles Portfolio")
    for entry in portfolio:
        st.write(entry)

    # Confirm and create DataFrame
    if st.sidebar.button("Portfolio bestätigen"):
        portfolio_data = [entry.split(",") for entry in portfolio]  # Assuming entries are comma-separated
        df = pd.DataFrame(portfolio_data, columns=["Stock", "Ticker"])
        st.session_state.portfolio_df = df
        st.write("Portfolio bestätigt!")

    # Fetch current stock prices
    if "portfolio_df" in st.session_state and st.sidebar.button("Aktuelle Aktienkurse abrufen"):
        tickers = st.session_state.portfolio_df['Ticker'].tolist()
        prices = fetch_stock_prices(tickers)
        st.session_state.stock_prices = prices
        
        # Display the DataFrame with current prices
        st.header("Portfolio mit aktuellen Aktienkursen")
        st.session_state.portfolio_df['Aktueller Kurs'] = st.session_state.portfolio_df['Ticker'].map(st.session_state.stock_prices)
        st.write(st.session_state.portfolio_df)
else:
    st.write("Bitte geben Sie Ihren OpenAI API-Schlüssel ein, um zu beginnen.")

# Funktion zum Abrufen der aktuellen Aktienkurse von Yahoo Finance
def fetch_stock_prices(tickers):
    stock_data = {}
    for ticker in tickers:
        stock_info = yf.Ticker(ticker)
        stock_data[ticker] = stock_info.history(period="1d")['Close'][0]
    return stock_data
