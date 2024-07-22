import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# Funktion zum Laden der CSV-Datei
def load_csv(file):
    return pd.read_csv(file)

# Funktion zum Abrufen der Aktienkurse von Yahoo Finance
def fetch_stock_prices(ticker):
    stock_info = yf.Ticker(ticker)
    return stock_info.history(period="5d")

# Funktion zur Anzeige der Kursdaten
def display_stock_data(stock_data, ticker, tsi_value):
    st.write(f"**{ticker} (TSI-Wert: {tsi_value})**")
    st.write(stock_data)
    st.line_chart(stock_data['Close'])

# Funktion zur Berechnung des gesamten Portfoliowerts
def calculate_portfolio_value(portfolio, tsi_df, investment=15000):
    portfolio_value = pd.DataFrame()
    investment_per_stock = investment / len(portfolio)
    for ticker in portfolio['Ticker']:
        stock_data = fetch_stock_prices(ticker)
        if not stock_data.empty:
            stock_data['Investment Value'] = stock_data['Close'] * (investment_per_stock / stock_data['Close'].iloc[0])
            if portfolio_value.empty:
                portfolio_value = stock_data[['Investment Value']].copy()
            else:
                portfolio_value['Investment Value'] += stock_data['Investment Value']
    return portfolio_value

# Streamlit App
st.title("TSI USA Portfolio Assistant")

# Sidebar zum Hochladen der CSV-Datei
st.sidebar.header("Upload CSV")
uploaded_file = st.sidebar.file_uploader("Upload your TSI USA Portfolio CSV file", type=["csv"])

if uploaded_file is not None:
    portfolio = load_csv(uploaded_file)
    if not portfolio.empty:
        st.write("Uploaded TSI USA Portfolio:")
        st.write(portfolio)

        # Dummy TSI Werte (Ersetzen Sie dies durch echte Daten)
        tsi_data = {'Ticker': portfolio['Ticker'], 'TSI Value': [95, 92, 88, 97, 94, 90, 93, 89, 91]}
        tsi_df = pd.DataFrame(tsi_data)

        st.header("Stock Data with TSI Values")
        for index, row in portfolio.iterrows():
            stock_data = fetch_stock_prices(row['Ticker'])
            if not stock_data.empty:
                tsi_value = tsi_df[tsi_df['Ticker'] == row['Ticker']]['TSI Value'].values[0]
                display_stock_data(stock_data, row['Ticker'], tsi_value)

        st.header("Portfolio Value Over Time")
        portfolio_value = calculate_portfolio_value(portfolio, tsi_df)
        if not portfolio_value.empty:
            st.line_chart(portfolio_value['Investment Value'])
            st.write(portfolio_value)
    else:
        st.write("The uploaded CSV file is empty. Please upload a valid CSV file.")
else:
    st.write("Please upload a CSV file to proceed.")
