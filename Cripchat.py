import requests
import pandas as pd

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


# Desde FRED (ekemplo: inflación en Japón)
from pandas_datareader import data as pdr

japan_cpi = pdr.get_data_fred("CPALTT01JPQ659N", start="2000-01-01")

# Grafique la tasa de cambio y la inflacion de japón
Def plot_data(df, japan_cpi)
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(df.index, df["close"], label = "Tasa de cambio JPY/USD", color="blue")
    ax1.set_ylabel("Tasa de Cambio", color="blue")
    ax1-set_xlabel("fecha")
    ax1-legend(loc="upper left")

    ax2 = ax1.twinx()
    ax2.plot(df.index, df["close

