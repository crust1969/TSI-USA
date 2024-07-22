import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import openai

# Funktion zur Ermittlung des aktuellen TSI USA Portfolios mit LLM
def get_current_tsi_usa_portfolio(api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Du bist ein Finanzexperte."},
            {"role": "user", "content": "ermittle das aktuelle TSI USA Portfolio und zeige an, welche Werte im Vergleich zum Portfolio vorher hinzugefügt wurden und welche entfernt wurden"}
        ]
    )
    return response['choices'][0]['message']['content']

# Funktion zum Laden der Kursdaten
def load_stock_data(tickers, start_date, end_date):
    stock_data = {}
    for ticker in tickers:
        stock_data[ticker] = yf.download(ticker, start=start_date, end=end_date)["Close"]
    return pd.DataFrame(stock_data)

# Streamlit App
st.title("TSI USA Aktien Portfolio")

# Sidebar zur Eingabe des OpenAI API-Schlüssels
api_key = st.sidebar.text_input("OpenAI API Schlüssel", type="password")

# Sidebar zur Ermittlung der aktuellen TSI USA Aktien
if st.sidebar.button("Ermittle aktuelle TSI USA Aktien") and api_key:
    tsi_usa_stocks_text = get_current_tsi_usa_portfolio(api_key)
    st.sidebar.success("Aktuelle TSI USA Aktien erfolgreich ermittelt!")
else:
    tsi_usa_stocks_text = ""

# Anzeige der TSI-Werte
if tsi_usa_stocks_text:
    st.header("Aktuelle TSI USA Aktien und Veränderungen")
    st.text(tsi_usa_stocks_text)
    
    # Parsing the response to get stock tickers and TSI values
    lines = tsi_usa_stocks_text.split('\n')
    tickers = [line.split(': ')[1] for line in lines if 'Ticker' in line]
    tsi_values = {line.split(': ')[0]: float(line.split(': ')[1]) for line in lines if 'TSI-Wert' in line}

    if tickers:
        st.header("TSI-Werte der TSI USA Aktien")
        tsi_df = pd.DataFrame(tsi_values.items(), columns=["Aktie", "TSI-Wert"])
        st.table(tsi_df)

        # Laden der Kursdaten des gesamten Portfolios
        st.header("Entwicklung des gesamten Portfolios")
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
    st.write("Bitte geben Sie Ihren OpenAI API-Schlüssel ein und klicken Sie auf den Button in der Sidebar, um die aktuellen TSI USA Aktien zu ermitteln.")
