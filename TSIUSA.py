import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Funktion zum Berechnen des TSI (Trend Strength Indicator)
def calculate_tsi(close_prices, long_window=25, short_window=13):
    diff = close_prices.diff(1)
    abs_diff = abs(diff)

    double_smoothed_diff = diff.ewm(span=long_window, adjust=False).mean().ewm(span=short_window, adjust=False).mean()
    double_smoothed_abs_diff = abs_diff.ewm(span=long_window, adjust=False).mean().ewm(span=short_window, adjust=False).mean()

    tsi = 100 * (double_smoothed_diff / double_smoothed_abs_diff)
    return tsi

# Hauptfunktion
def main():
    st.title("TSI USA Aktien Portfolio Analyse")

    # Eingabefeld für Aktien-Ticker
    tickers = st.text_input("Geben Sie die Aktien-Ticker ein, getrennt durch Kommas (z.B. AAPL, MSFT, GOOGL):")

    if tickers:
        ticker_list = [ticker.strip() for ticker in tickers.split(",")]
        data = yf.download(ticker_list, start="2020-01-01")

        # Schließen-Daten extrahieren
        close_data = data['Close']

        # TSI für jede Aktie berechnen
        tsi_data = pd.DataFrame()
        for ticker in ticker_list:
            tsi_data[ticker] = calculate_tsi(close_data[ticker])

        # TSI-Werte tabellarisch darstellen
        st.subheader("TSI-Werte der Aktien")
        st.write(tsi_data)

        # Portfolioentwicklung darstellen
        st.subheader("Portfolioentwicklung")
        portfolio_close = close_data.mean(axis=1)

        fig, ax = plt.subplots()
        portfolio_close.plot(ax=ax, title='Portfolio Close Price Over Time')
        ax.set_xlabel('Datum')
        ax.set_ylabel('Durchschnittlicher Schlusskurs')

        st.pyplot(fig)

# Streamlit App starten
if __name__ == "__main__":
    main()
