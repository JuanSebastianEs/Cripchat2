import requests
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader import data as pdr

# Tasa actual JPY/USD con Alpha Vantage
API_KEY = "MK5N3CCZRD0R1ROR"
url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=JPY&to_currency=USD&apikey={API_KEY}"
response = requests.get(url)
data = response.json()
tasa_actual = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
print(f"💰 1 JPY = {tasa_actual} USD")

# Usando pandas_detareader (Yahoo Finance)

import yfinance as yf

# Descargar datos históricos de JPY/USD desde Yahoo Finance
df = yf.download("JPY=X", start="2018-01-01", end="2023-01-01")

print(df.head())  # Muestra las primeras filas del dataframe

#Función auxiliar para identificar la columna de precio de cierre
def get_close_column(df):
    """
    Retorna el nombre de la columna que contiene el precio de cierre (Close o Adj Close).
    Si no la encuentra, imprime un mensaje de error y retorna None.
    """
    if "Adj Close" in df.columns:
        return "Adj Close"
    elif "Close" in df.columns:
        return "Close"
    else:
        print("Error: No se encontró la columna 'Close' o 'Adj Close'. "
              f"Columnas disponibles: {df.columns.tolist()}")
        return None


# Desde FRED (ekemplo: inflación en Japón)
from pandas_datareader import data as pdr

japan_cpi = pdr.get_data_fred("CPALTT01JPQ659N", start="2000-01-01")

# Grafique la tasa de cambio y la inflacion de japón
def plot_data(df, japan_cpi):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(df.index, df["Adj close"], label = "Tasa de cambio JPY/USD", color="blue")
    ax1.set_ylabel("Tasa de Cambio", color="blue")
    ax1.set_xlabel("fecha")
    ax1.legend(loc="upper left")

    ax2 = ax1.twinx()
    ax2.plot(japan_cpi.index, japan_cpi, label="Inflación en Japón (CPI)", color="red")
    ax2.set_ylabel("CPI", color="red")
    ax2.legend(loc="upper right")

    plt.title("Tasa de Cambio JPY/USD vs. Inflación en Japón")
    plt.show()

# Análisis de la tasa de cambio
def analyze_exchange_rate(df):
    print("\n estadísticas de la tasa de cambio JPY/USD:")
    print(df["close"].describe())

# Ejecutar análisis de la tasa de cambío
def analyze_exchange_rate(df):
  close_col = get_close_column(df)
  if close_col is not None:
    return
    print("\nEstadísticas de la tasa de cambio JPY/USD:")
    print(df[close_col].describe())

#Ejecutar análisis
analyze_exchange_rate(df)
plot_data(df, japan_cpi)
