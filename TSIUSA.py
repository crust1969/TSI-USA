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
def check_portfolio_performance(portfolio, stop_loss_limits, official_tsi, use_official_tsi):
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
    
    if use_official_tsi:
        tsi_data = pd.DataFrame(official_tsi, index=[0]).T
        tsi_data.columns = ['TSI']
        current_tsi = official_tsi

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

# Streamlit App
st.title("Portfolio Performance Monitor mit TSI")
st.write("Überwachung der täglichen Performance, TSI und Stopp-Loss-Grenzen Ihres Portfolios")

# Portfolio aus CSV-Datei laden
uploaded_file = st.sidebar.file_uploader("Laden Sie Ihre Portfolio CSV-Datei hoch", type="csv")

if uploaded_file is not None:
    portfolio_df = pd.read_csv(uploaded_file)
    
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
            use_official_tsi = st.sidebar.checkbox("TSI vom Aktionär verwenden", value=False)
            performance, current_prices, tsi_data, stop_loss_alerts, current_tsi, ticker_names = check_portfolio_performance(portfolio, stop_loss_limits, official_tsi, use_official_tsi)

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
                date_slider = st.slider(
                    "Zeitraum auswählen",
                    min_value=tsi_start_date.to_pydatetime(),
                    max_value=tsi_end_date.to_pydatetime(),
                    value=(tsi_start_date.to_pydatetime(), tsi_end_date.to_pydatetime())
                )
                filtered_tsi_data = tsi_data[date_slider[0]:date_slider[1]]
                st.line_chart(filtered_tsi_data)

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

                # Unterschied in der Berechnungsmethode erklären
                st.subheader("Unterschiede in der TSI-Berechnung")
                st.write("""
                    Die TSI-Werte, die in dieser App berechnet werden, basieren auf einer Standardformel, die zwei exponentielle gleitende Durchschnitte (EMAs) der Preisänderungen verwendet. Diese Methode ist allgemein bekannt und weit verbreitet.
                    Im Gegensatz dazu verwendet "Der Aktionär" eine proprietäre Methode zur Berechnung des TSI, die möglicherweise zusätzliche Glättungs- und Gewichtungsfaktoren beinhaltet, die nicht in der Standard-TSI-Berechnung verwendet werden. 
                    Dies kann zu unterschiedlichen Ergebnissen führen, obwohl beide Methoden darauf abzielen, die relative Stärke einer Aktie im Vergleich zu einem Index zu messen.
                """)
else:
    st.sidebar.write("Bitte laden Sie eine Portfolio CSV-Datei hoch.")
