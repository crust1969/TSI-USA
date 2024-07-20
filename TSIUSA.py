import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

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
def check_portfolio_performance(portfolio, stop_loss_limits):
    tickers = list(portfolio.keys())
    investments = list(portfolio.values())

    # Historische Daten abrufen
    try:
        data = yf.download(tickers, period='1y')['Adj Close']
    except Exception as e:
        st.error(f"Fehler beim Abrufen der historischen Daten: {e}")
        return None, None, None, []

    # Überprüfung der Daten
    if data.empty:
        st.error("Keine historischen Daten verfügbar.")
        return None, None, None, []

    # TSI für jede Aktie berechnen
    tsi_data = pd.DataFrame()
    for ticker in tickers:
        tsi_data[ticker] = calculate_tsi(data[ticker])

    # Normalisieren der Daten (alle Kurse starten bei 1)
    data_norm = data.div(data.iloc[0])

    # Berechnung des Portfoliowerts
    portfolio_value = (data_norm * investments).sum(axis=1)

    # Aktuelle Daten abrufen
    try:
        current_data = yf.download(tickers, period='1d')['Adj Close']
    except Exception as e:
        st.error(f"Fehler beim Abrufen der aktuellen Daten: {e}")
        return None, None, None, []

    if current_data.empty:
        st.error("Keine aktuellen Daten verfügbar.")
        return None, None, None, []

    current_prices = current_data.iloc[-1]

    # Überprüfung der Stopp-Loss-Grenzen
    previous_prices = data.iloc[-2]
    stop_loss_alerts = []
    for ticker in tickers:
        current_price = current_prices[ticker]
        previous_price = previous_prices[ticker]
        if (previous_price - current_price) / previous_price * 100 >= stop_loss_limits[ticker]:
            stop_loss_alerts.append(f"Stopp-Loss erreicht für {ticker}: aktueller Preis = {current_price:.2f}, Vortagespreis = {previous_price:.2f}, Verlust = {((previous_price - current_price) / previous_price * 100):.2f}%")
    
    return portfolio_value, current_prices, tsi_data, stop_loss_alerts

# Streamlit App
st.title("Portfolio Performance Monitor mit TSI")
st.write("Überwachung der täglichen Performance, TSI und Stopp-Loss-Grenzen Ihres Portfolios")

# Portfolio aus CSV-Datei laden
uploaded_file = st.sidebar.file_uploader("Laden Sie Ihre Portfolio CSV-Datei hoch", type="csv")

if uploaded_file is not None:
    portfolio_df = pd.read_csv(uploaded_file)
    st.sidebar.write("Hochgeladenes Portfolio:")
    st.sidebar.write(portfolio_df)

    portfolio = portfolio_df.set_index('Ticker')['Investment'].to_dict()
    stop_loss_limits = portfolio_df.set_index('Ticker')['StopLoss'].to_dict()

    # Schaltfläche zum Überprüfen der Performance
    if st.sidebar.button("Portfolio überprüfen"):
        performance, current_prices, tsi_data, stop_loss_alerts = check_portfolio_performance(portfolio, stop_loss_limits)

        if performance is not None and current_prices is not None:
            # Plot der Portfolio-Performance
            st.subheader("Portfolio Performance")
            st.line_chart(performance)

            # Anzeige der aktuellen Preise
            st.subheader("Aktuelle Preise")
            st.write(current_prices)

            # Anzeige der TSI-Daten
            st.subheader("TSI-Daten")
            st.line_chart(tsi_data)

            # Anzeige der Stopp-Loss-Warnungen
            st.subheader("Stopp-Loss-Warnungen")
            if stop_loss_alerts:
                for alert in stop_loss_alerts:
                    st.warning(alert)
            else:
                st.success("Keine Stopp-Loss-Grenzen erreicht.")

            # Erstellen und Anzeigen des Plots
            st.subheader("Portfolio Verteilung")
            labels = list(portfolio.keys())
            sizes = list(portfolio.values())
            colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'lightgreen', 'pink']

            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig)
else:
    st.sidebar.write("Bitte laden Sie eine Portfolio CSV-Datei hoch.")
