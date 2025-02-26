from fastapi import FastAPI, HTTPException, Query
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import logging
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Configurar logging para ver errores detallados
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API de Finanzas", description="Chatbot para conversión de divisas, datos históricos y predicciones")

# Configuración CORS para permitir acceso desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear directorio para datos históricos si no existe
os.makedirs("datos", exist_ok=True)

# Función para obtener una fecha de referencia pasada válida
def obtener_fecha_referencia():
    # Usamos una fecha fija pasada para asegurar que haya datos disponibles
    return datetime(2023, 1, 31)  # 31 de enero de 2023

# Ruta principal
@app.get("/")
def home():
    return {"mensaje": "Bienvenido al chatbot de finanzas", 
            "endpoints": [
                "/cambio?de=USD&a=COP",
                "/historico?base=USD&destino=COP",
                "/graficar?base=USD&destino=COP",
                "/predecir?base=USD&destino=COP&dias=5"
            ]}

# Ruta de prueba simple
@app.get("/test")
def test():
    return {"test": "ok", "timestamp": obtener_fecha_referencia().isoformat()}

# Obtener tasa de cambio en tiempo real (usando Exchange Rates API - gratuita)
@app.get("/cambio")

# API Key para ExchangeRate-API (reemplázala con la tuya)

# 🔹 Ruta principal
@app.get("/")
def home():
    return {"mensaje": "Bienvenido al chatbot de divisas"}

API_KEY = "5bc7d18c9c7a81a000681a3a9"

# 🔹 Obtener tasa de cambio en tiempo real desde ExchangeRate-API
@app.get("/cambio")
def obtener_cambio(moneda: str = "USD"):
    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{moneda}"
    respuesta = requests.get(url)
    
    if respuesta.status_code == 200:
        datos = respuesta.json()
        return {"moneda_base": moneda, "tasas": datos["conversion_rates"]}
    else:
        return {"error": "No se pudo obtener la información"}

# Obtener datos históricos
@app.get("/historico")
def obtener_historico(
    base: str = Query("USD", description="Moneda base"),
    destino: str = Query("COP", description="Moneda destino"),
    dias: int = Query(30, description="Días históricos (máximo 365)")
):
    # Verificar el valor de días
    dias_valor = dias
    if dias_valor > 365:
        dias_valor = 365  # Limitamos a 1 año
        
    try:
        logger.info(f"Obteniendo histórico de {base} a {destino} para {dias_valor} días")
        
        # Usar fecha de referencia fija
        fecha_referencia = obtener_fecha_referencia()
        fechas = []
        datos = []
        
        # Vamos a consultar día por día para mayor fiabilidad
        for i in range(dias_valor):
            # Generamos fechas hacia atrás desde nuestra fecha de referencia
            fecha = fecha_referencia - timedelta(days=i)
            fecha_str = fecha.strftime("%Y-%m-%d")
            fechas.append(fecha_str)
            
            # Usamos API gratuita sin límites
            url = f"https://api.exchangerate.host/{fecha_str}?base={base}&symbols={destino}"
            logger.info(f"Consultando URL: {url}")
            
            respuesta = requests.get(url)
            
            if respuesta.status_code == 200:
                resultado = respuesta.json()
                if "rates" in resultado and destino in resultado["rates"]:
                    tasa = resultado["rates"][destino]
                    datos.append({"fecha": fecha_str, "tasa": tasa})
                    logger.info(f"Tasa para {fecha_str}: {tasa}")
            else:
                logger.warning(f"No se pudo obtener datos para {fecha_str}: {respuesta.status_code}")
        
        # Guardar en CSV
        if datos:
            df = pd.DataFrame(datos)
            df = df.sort_values(by="fecha")  # Ordenar cronológicamente
            filename = f"datos/historico_{base}_{destino}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"Datos guardados en {filename}")
            
            return {
                "mensaje": f"Datos históricos obtenidos para {base} a {destino}",
                "datos": datos,
                "archivo": filename
            }
        else:
            logger.error("No se obtuvieron datos históricos")
            return {"error": "No se pudieron obtener datos históricos"}
            
    except Exception as e:
        logger.exception("Error en histórico")
        return {"error": str(e)}

# Generar gráfico de datos históricos
@app.get("/graficar")
def graficar_historico(
    base: str = Query("USD", description="Moneda base"),
    destino: str = Query("COP", description="Moneda destino")
):
    try:
        logger.info(f"Generando gráfico para {base} a {destino}")
        filename = f"datos/historico_{base}_{destino}.csv"
        
        # Si no existe el archivo, intentamos obtener los datos primero
        if not os.path.exists(filename):
            logger.info("Archivo no encontrado, obteniendo datos primero")
            # Llamamos a obtener_historico con los valores extraídos directamente
            resultado = obtener_historico(base, destino, 30)  # Usamos 30 días por defecto
            
            # Verificar nuevamente
            if not os.path.exists(filename):
                logger.error("No se pudieron obtener datos históricos")
                return {"error": "No hay datos históricos disponibles"}
        
        # Cargar datos
        df = pd.read_csv(filename)
        logger.info(f"Datos cargados: {len(df)} registros")
        
        # Generar gráfico
        plt.figure(figsize=(12, 6))
        plt.plot(df["fecha"], df["tasa"], marker="o", linestyle="-", color="blue")
        plt.title(f"Evolución del tipo de cambio {base} a {destino}")
        plt.xlabel("Fecha")
        plt.ylabel(f"Valor en {destino}")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Guardar gráfico
        img_filename = f"datos/grafico_{base}_{destino}.png"
        plt.savefig(img_filename)
        plt.close()
        logger.info(f"Gráfico guardado como {img_filename}")
        
        # Devolver URL para ver el gráfico
        return FileResponse(img_filename, media_type="image/png")
            
    except Exception as e:
        logger.exception("Error al generar gráfico")
        return {"error": str(e)}

# Realizar predicción de valores futuros
@app.get("/predecir")
def predecir(
    base: str = Query("USD", description="Moneda base"),
    destino: str = Query("COP", description="Moneda destino"),
    dias: int = Query(5, description="Días a predecir (máximo 30)")
):
    # Verificar el valor de días
    dias_valor = dias
    if dias_valor > 30:
        dias_valor = 30  # Limitamos a 30 días para predicciones razonables
        
    try:
        logger.info(f"Prediciendo {base} a {destino} para {dias_valor} días")
        filename = f"datos/historico_{base}_{destino}.csv"
        
        # Si no existe el archivo, intentamos obtener los datos primero
        if not os.path.exists(filename):
            logger.info("Archivo no encontrado, obteniendo datos primero")
            resultado = obtener_historico(base, destino, 30)  # Usamos 30 días por defecto
            
            # Verificar nuevamente
            if not os.path.exists(filename):
                logger.error("No hay datos históricos disponibles")
                return {"error": "No hay suficientes datos históricos para predicción"}
        
        # Cargar datos
        df = pd.read_csv(filename)
        logger.info(f"Datos cargados: {len(df)} registros")
        
        if len(df) < 7:  # Necesitamos al menos 7 días para una predicción razonable
            logger.warning("Datos insuficientes para predicción")
            return {"error": "Se necesitan al menos 7 días de datos históricos para predecir"}
        
        # Preparar datos para entrenamiento
        df['fecha_num'] = np.arange(len(df))
        X = df['fecha_num'].values.reshape(-1, 1)
        y = df['tasa'].values.reshape(-1, 1)
        
        # Entrenar modelo
        modelo = LinearRegression()
        modelo.fit(X, y)
        logger.info("Modelo entrenado")
        
        # Predecir valores futuros
        ultima_fecha_num = df['fecha_num'].max()
        fechas_futuras = np.arange(ultima_fecha_num + 1, ultima_fecha_num + dias_valor + 1).reshape(-1, 1)
        predicciones = modelo.predict(fechas_futuras)
        
        # Generar fechas para los resultados
        ultima_fecha = datetime.strptime(df['fecha'].iloc[-1], "%Y-%m-%d")
        fechas_prediccion = [(ultima_fecha + timedelta(days=i+1)).strftime("%Y-%m-%d") 
                            for i in range(dias_valor)]
        
        # Preparar resultados
        resultados = []
        for i in range(dias_valor):
            resultados.append({
                "fecha": fechas_prediccion[i],
                "prediccion": round(float(predicciones[i][0]), 4)
            })
        
        # Generar gráfico con datos históricos y predicción
        plt.figure(figsize=(12, 6))
        
        # Datos históricos
        plt.plot(df["fecha"], df["tasa"], marker="o", linestyle="-", color="blue", label="Histórico")
        
        # Predicciones
        plt.plot(fechas_prediccion, predicciones, marker="x", linestyle="--", color="red", label="Predicción")
        
        plt.title(f"Predicción del tipo de cambio {base} a {destino}")
        plt.xlabel("Fecha")
        plt.ylabel(f"Valor en {destino}")
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        
        # Guardar gráfico
        img_filename = f"datos/prediccion_{base}_{destino}.png"
        plt.savefig(img_filename)
        plt.close()
        logger.info(f"Gráfico de predicción guardado como {img_filename}")
        
        return {
            "base": base,
            "destino": destino,
            "predicciones": resultados,
            "grafico": f"/ver_grafico?archivo=prediccion_{base}_{destino}.png"
        }
            
    except Exception as e:
        logger.exception("Error al realizar predicción")
        return {"error": str(e)}

# Endpoint para ver gráficos generados
@app.get("/ver_grafico")
def ver_grafico(archivo: str = Query(..., description="Nombre del archivo de gráfico")):
    try:
        ruta = f"datos/{archivo}"
        if os.path.exists(ruta):
            return FileResponse(ruta, media_type="image/png")
        else:
            return {"error": "Gráfico no encontrado"}
    except Exception as e:
        logger.exception("Error al mostrar gráfico")
        return {"error": str(e)}

# Función para ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    logger.info("Iniciando servidor...")
    # Ejecutamos con localhost (127.0.0.1) en lugar de 0.0.0.0 para mejor compatibilidad
    uvicorn.run("Cripchat:app", host="127.0.0.1", port=8000, reload=True)

