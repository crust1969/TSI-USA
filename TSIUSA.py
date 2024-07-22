import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Funktion zum Abrufen der aktuellen TSI USA Aktien und TSI-Werte
def get_tsi_usa_stocks():
    # Dies ist ein Platzhalter. Die tatsächlichen Werte sollten von der Website "Der Aktionär" oder einer anderen verlässlichen Quelle abgerufen werden.
    tsi_usa_stocks = {
        "Nvidia": {"ticker": "NVDA", "tsi_value": 99.72},
        "Tesla": {"ticker": "TSLA", "tsi_value": 99.63},
        "Vertex Pharmaceuticals": {"ticker": "VRTX", "tsi_value": 98.85},
        "Enphase Energy": {"ticker": "ENPH", "tsi_value": 98.77},
        "First Solar": {"ticker": "FSLR", "tsi_value": 98.66},
        "Amazon.com": {"ticker": "AMZN", "tsi_value": 98.27},
        "Apollo Medical Holdings": {"ticker": "AMEH", "tsi_value": 98.15},
        "Workhorse Group": {"ticker": "WKHS", "tsi_value": 97.99},
        "Plug Power": {"ticker": "PLUG", "tsi_value": 97.88}
    }
    return tsi_usa_stocks

# Funktion zum Laden der Kursdaten
def load_stock_data(tickers, start_date, end_date):
    stock_data = {}
    for ticker in tickers:
        stock_data[ticker] = yf.download(ticker, start=start_date, end=end_date)["Close"]
    return pd.DataFrame(stock_data)

# Streamlit App
st.title("TSI USA Aktien Portfolio")

# Sidebar zur Ermittlung der aktuellen TSI USA Aktien
if st.sidebar.button("Ermittle aktuelle TSI USA Aktien"):
    tsi_usa_stocks = get_tsi_usa_stocks()
    st.sidebar.success("Aktuelle TSI USA Aktien erfolgreich ermittelt!")
else:
    tsi_usa_stocks = {}

# Anzeige der TSI-Werte
if tsi_usa_stocks:
    st.header("Aktuelle TSI-Werte der TSI USA Aktien")
    tsi_values = {stock: data["tsi_value"] for stock, data in tsi_usa_stocks.items()}
    tsi_df = pd.DataFrame(tsi_values.items(), columns=["Aktie", "TSI-Wert"])
    st.table(tsi_df)

    # Laden der Kursdaten des gesamten Portfolios
    st.header("Entwicklung des gesamten Portfolios")
    tickers = [data["ticker"] for stock, data in tsi_usa_stocks.items()]
    stock_data = load_stock_data(tickers, start_date="2023-01-01", end_date="2024-12-31")

    # Berechnung des Portfolio-Werts
    portfolio_value = stock_data.mean(axis=1)

    # Plotten der Kursdaten des gesamten Portfolios
    st.subheader("Kursverlauf des gesamten Portfolios")
    fig, ax = plt.subplots()
    ax.plot(portfolio_value.index, portfolio_value, label="Portfolio-Wert")
    ax.set_xlabel("Datum")
    ax.set_ylabel("Preis in USD")
    ax.set_title("Entwicklung des TSI USA Portfolios")
    ax.legend()
    st.pyplot(fig)
else:
    st.write("Bitte klicken Sie auf den Button in der Sidebar, um die aktuellen TSI USA Aktien zu ermitteln.")
