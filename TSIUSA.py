import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests

# Funktion zum Scraping der TSI USA Aktien von "Der Aktionär"
def get_tsi_usa_stocks():
    url = "https://www.deraktionaer.de/tsi-usa"  # Beispiel-URL
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Hier wird angenommen, dass die TSI USA Aktienliste in einer Tabelle auf der Webseite steht
    # Diese Logik muss entsprechend der tatsächlichen Webseite angepasst werden
    table = soup.find('table', {'class': 'some-class-name'})  # Platzhalter-Klassenname
    tickers = []
    for row in table.find_all('tr')[1:]:  # Überspringe die Header-Zeile
        ticker = row.find_all('td')[1].text.strip()  # Platzhalter für die Spalte mit den Tickers
        tickers.append(ticker)

    return tickers

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

    # Sidebar für dynamische Ermittlung des TSI USA Portfolios
    st.sidebar.header("Optionen")
    if st.sidebar.button("TSI USA Portfolio ermitteln"):
        tickers = get_tsi_usa_stocks()
        if tickers:
            data = yf.download(tickers, start="2020-01-01")

            # Schließen-Daten extrahieren
            close_data = data['Close']

            # TSI für jede Aktie berechnen
            tsi_data = pd.DataFrame()
            for ticker in tickers:
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
        else:
            st.error("Konnte keine TSI USA Aktien von 'Der Aktionär' ermitteln.")
    else:
        st.sidebar.write("Klicken Sie auf den Button, um die TSI USA Aktien zu ermitteln.")

# Streamlit App starten
if __name__ == "__main__":
    main()
