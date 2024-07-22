import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Funktion zur Berechnung des TSI-Indikators
def calculate_tsi(data, r=25, s=13):
    delta = data.diff()
    abs_delta = delta.abs()
    
    # Erste Glättung
    ema1_delta = delta.ewm(span=r).mean()
    ema1_abs_delta = abs_delta.ewm(span=r).mean()
    
    # Zweite Glättung
    ema2_delta = ema1_delta.ewm(span=s).mean()
    ema2_abs_delta = ema1_abs_delta.ewm(span=s).mean()
    
    # TSI-Berechnung
    tsi = 100 * ema2_delta / ema2_abs_delta
    return tsi

# Funktion zur Überwachung der Portfolio-Performance und Berechnung des TSI
def check_portfolio_performance(portfolio, stop_loss_limits, official_tsi):
    tickers = list(portfolio.keys())
    investments = list(portfolio.values())

    # Historische Daten abrufen
    try:
        data = yf.download(tickers, period='1y')['Adj Close']
    except Exception as e:
        st.error(f"Fehler beim Abrufen der historischen Daten: {e}")
        return None, None, None, [], {}, {}

    # Überprüfung der Daten
    if data.empty:
        st.error("Keine historischen Daten verfügbar.")
        return None, None, None, [], {}, {}

    # TSI für jede Aktie berechnen
    tsi_data = pd.DataFrame()
    current_tsi = {}
    for ticker in tickers:
        tsi_series = calculate_tsi(data[ticker])
        tsi_data[ticker] = tsi_series
        current_tsi[ticker] = tsi_series.iloc[-1]

    # Normalisieren der Daten (alle Kurse starten bei 1)
    data_norm = data.div(data.iloc[0])

    # Berechnung des Portfoliowerts
    portfolio_value = (data_norm * investments).sum(axis=1)

    # Aktuelle Daten abrufen
    try:
        current_data = yf.download(tickers, period='1d')['Adj Close']
    except Exception as e:
        st.error(f"Fehler beim Abrufen der aktuellen Daten: {e}")
        return None, None, None, [], {}, {}

    if current_data.empty:
        st.error("Keine aktuellen Daten verfügbar.")
        return None, None, None, [], {}, {}

    current_prices = current_data.iloc[-1]

    # Bezeichnungen der Aktien abrufen
    ticker_names = {}
    for ticker in tickers:
        stock_info = yf.Ticker(ticker).info
        ticker_names[ticker] = stock_info.get('shortName', ticker)

    # Überprüfung der Stopp-Loss-Grenzen
    previous_prices = data.iloc[-2]
    stop_loss_alerts = []
    for ticker in tickers:
        current_price = current_prices[ticker]
        previous_price = previous_prices[ticker]
        if (previous_price - current_price) / previous_price * 100 >= stop_loss_limits[ticker]:
            stop_loss_alerts.append(f"Stopp-Loss erreicht für {ticker}: aktueller Preis = {current_price:.2f}, Vortagespreis = {previous_price:.2f}, Verlust = {((previous_price - current_price) / previous_price * 100):.2f}%")
    
    return portfolio_value, current_prices, tsi_data, stop_loss_alerts, current_tsi, ticker_names

# Funktion zum Abrufen der offiziellen TSI-Werte von "Der Aktionär"
def get_official_tsi():
    # Beispielhafte TSI-Werte vom Aktionär
    official_tsi = {
        'NVDA': 99.63,
        'TSLA': 99.72,
        'ASTH': 98.00,
        'ENPH': 98.00,
        'FSLR': 98.00,
        'VRTX': 98.00,
        'DDOG': 98.27,
        'PACB': 98.00,
        'SMCI': 98.00
    }
    return official_tsi

# Funktion zur Ermittlung des aktuellen TSI USA Portfolios von "Der Aktionär"
def fetch_current_tsi_usa_portfolio():
    # Hier wird die Web-Scraping Logik implementiert
    # Beispiel-URLs zur Recherche
    urls = [
        "https://www.deraktionaer.de/aktien/tsi-usa/",
        # Weitere relevante URLs hinzufügen
    ]

    portfolio = []

    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extrahieren der relevanten Daten (Dies muss basierend auf der tatsächlichen Webseitenstruktur angepasst werden)
        for row in soup.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) > 1:
                ticker = columns[0].text.strip()
                tsi_value = columns[1].text.strip()
                portfolio.append({'Ticker': ticker, 'TSI': tsi_value})

    return pd.DataFrame(portfolio)

# Streamlit App
st.title("Portfolio Performance Monitor mit TSI")
st.write("Überwachung der täglichen Performance, TSI und Stopp-Loss-Grenzen Ihres Portfolios")

# Portfolio aus CSV-Datei laden
uploaded_file = st.sidebar.file_uploader("Laden Sie Ihre Portfolio CSV-Datei hoch", type="csv")

# Monatliche Portfolio-Aktualisierung
if st.sidebar.button("Monatliches Portfolio-Update"):
    current_portfolio_df = fetch_current_tsi_usa_portfolio()
    st.write("Aktualisiertes TSI USA Portfolio für den aktuellen Monat:")
    st.write(current_portfolio_df)

    # Vergleich mit dem hochgeladenen Portfolio
    if uploaded_file is not None:
        old_portfolio_df = pd.read_csv(uploaded_file)
        old_portfolio_df.columns = [col.strip() for col in old_portfolio_df.columns]  # Spaltennamen bereinigen
        current_portfolio_df.columns = [col.strip() for col in current_portfolio_df.columns]  # Spaltennamen bereinigen

        old_tickers = set(old_portfolio_df['Ticker'])
        new_tickers = set(current_portfolio_df['Ticker'])

        added_tickers = new_tickers - old_tickers
        removed_tickers = old_tickers - new_tickers

        st.write("Neu hinzugefügte Positionen:")
        st.write(current_portfolio_df[current_portfolio_df['Ticker'].isin(added_tickers)])

        st.write("Entfernte Positionen:")
        st.write(old_portfolio_df[old_portfolio_df['Ticker'].isin(removed_tickers)])

if uploaded_file is not None:
    portfolio_df = pd.read_csv(uploaded_file)
    portfolio_df.columns = [col.strip() for col in portfolio_df.columns]  # Spaltennamen bereinigen
    
    # Überprüfung der Spaltennamen
    expected_columns = ['Ticker', 'Investment', 'StopLoss']
    if not all(column in portfolio_df.columns for column in expected_columns):
        st.error(f"Die hochgeladene Datei muss die folgenden Spalten enthalten: {', '.join(expected_columns)}")
    else:
        st.sidebar.write("Hochgeladenes Portfolio:")
        st.sidebar.write(portfolio_df)

        portfolio = portfolio_df.set_index('Ticker')['Investment'].to_dict()
        stop_loss_limits = portfolio_df.set_index('Ticker')['StopLoss'].to_dict()
        official_tsi = get_official_tsi()

        # Schaltfläche zum Überprüfen der Performance
        if st.sidebar.button("Portfolio überprüfen"):
            performance, current_prices, tsi_data, stop_loss_alerts, current_tsi, ticker_names = check_portfolio_performance(portfolio, stop_loss_limits, official_tsi)

            if performance is not None and current_prices is not None:
                # Plot der Portfolio-Performance
                st.subheader("Portfolio Performance")
                st.line_chart(performance)

                # Anzeige der aktuellen Preise und TSI-Werte
                st.subheader("Aktuelle Preise und TSI-Werte")
                current_info = pd.DataFrame({
                    'Bezeichnung': [ticker_names[ticker] for ticker in current_prices.index],
                    'Aktueller Preis': current_prices.values,
                    'Aktueller TSI (berechnet)': [current_tsi[ticker] for ticker in current_prices.index],
                    'TSI vom Aktionär': [official_tsi[ticker] for ticker in current_prices.index]
                }, index=current_prices.index)
                st.write(current_info)

                # Anzeige der TSI-Daten
                st.subheader("TSI-Daten")
                tsi_start_date = tsi_data.index.min()
                tsi_end_date = tsi_data.index.max()
                date_slider = st
