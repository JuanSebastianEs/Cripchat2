import requests
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from pandas_datareader import data as pdr

# Tasa actual JPY/USD con Alpha Vantage
API_KEY = "MK5N3CCZRD0R1ROR"
url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency=JPY&to_currency=USD&apikey={API_KEY}"
response = requests.get(url)
data = response.json()

# Verificar si la API devolvió datos válidos
if "Realtime Currency Exchange Rate" in data:
    tasa_actual = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
    print(f"💰 1 JPY = {tasa_actual} USD")
else:
    print("Error al obtener la tasa de cambio. Verifica tu API Key.")

# Descargar datos históricos de JPY/USD desde Yahoo Finance
df = yf.download("JPY=X", start="2018-01-01", end="2023-01-01")

print(df.head())  # Muestra las primeras filas del dataframe

# Función auxiliar para identificar la columna de precio de cierre
def get_close_column(df):
    if "Adj Close" in df.columns:
        return "Adj Close"
    elif "Close" in df.columns:
        return "Close"
    else:
        print("Error: No se encontró la columna 'Close' o 'Adj Close'. "
              f"Columnas disponibles: {df.columns.tolist()}")
        return None

# Obtener datos de inflación de Japón desde FRED
japan_cpi = pdr.get_data_fred("CPALTT01JPQ659N", start="2000-01-01")

# Gráfico de tasa de cambio e inflación en Japón
def plot_data(df, japan_cpi):
    close_col = get_close_column(df)
    if close_col is None:
        return

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(df.index, df[close_col], label="Tasa de cambio JPY/USD", color="blue")
    ax1.set_ylabel("Tasa de Cambio", color="blue")
    ax1.set_xlabel("Fecha")
    ax1.legend(loc="upper left")

    ax2 = ax1.twinx()
    ax2.plot(japan_cpi.index, japan_cpi, label="Inflación en Japón (CPI)", color="red")
    ax2.set_ylabel("CPI", color="red")
    ax2.legend(loc="upper right")

    plt.title("Tasa de Cambio JPY/USD vs. Inflación en Japón")
    plt.show()

# Análisis de la tasa de cambio
def analyze_exchange_rate(df):
    close_col = get_close_column(df)
    if close_col is None:
        return
    print("\nEstadísticas de la tasa de cambio JPY/USD:")
    print(df[close_col].describe())

# Ejecutar análisis
analyze_exchange_rate(df)
plot_data(df, japan_cpi)

import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";
import { GiCherryBlossom, GiJapan, GiGoldBar } from "react-icons/gi";
import axios from "axios";

export default function CripChatUI() {
  const [exchangeRate, setExchangeRate] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchExchangeRate();
    fetchHistoricalData();
  }, []);

  const fetchExchangeRate = async () => {
    setLoading(true);
    try {
      const response = await axios.get("https://api.cripchat.com/latest");
      setExchangeRate(response.data.JPY.USD);
    } catch (error) {
      console.error("Error fetching exchange rate", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoricalData = async () => {
    try {
      const response = await axios.get("https://api.cripchat.com/historical");
      setHistoricalData(response.data);
    } catch (error) {
      console.error("Error fetching historical data", error);
    }
  };

  return (
    <motion.div
      className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-r from-red-600 to-orange-400 p-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
    >
      <h1 className="text-5xl font-bold text-white mb-6 flex items-center gap-3">
        <GiJapan /> Bienvenido a CripChat Exchange!
      </h1>
      <Card className="p-6 bg-white shadow-2xl rounded-2xl w-full max-w-md text-center">
        <CardContent>
          <p className="text-2xl font-semibold text-red-700 flex items-center justify-center gap-2">
            <GiGoldBar /> Tasa de Cambio JPY/USD
          </p>
          <p className="text-4xl my-4 font-bold">
            {loading ? "Cargando..." : exchangeRate ? `${exchangeRate.toFixed(4)} USD` : "Error"}
          </p>
          <Button onClick={fetchExchangeRate} className="mt-4 bg-red-600 hover:bg-red-700 text-white text-lg">
            <GiCherryBlossom className="mr-2" />Actualizar
          </Button>
        </CardContent>
      </Card>

      <div className="mt-8 w-full max-w-2xl">
        <h2 className="text-xl text-white font-semibold text-center mb-4">Historial de la Tasa de Cambio</h2>
        <Card className="bg-white p-4 rounded-xl shadow-lg">
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={historicalData}>
                <XAxis dataKey="date" stroke="#ff4d4d" />
                <YAxis stroke="#ff4d4d" />
                <Tooltip />
                <Line type="monotone" dataKey="JPY.USD" stroke="#ff4d4d" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}


