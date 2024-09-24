import os
import requests
import plotly.express as px
import yfinance as yf
import pandas as pd
import streamlit as st

# Define la lista de tickers
tickers = ['BMA.BA', 'GGAL.BA', 'YPFD.BA']  # Agrega los tickers que necesites
tickers_panel_lider = ['BMA.BA']  # Define tus paneles según sea necesario

# Función para descargar logos
def download_logo(ticker):
    logo_url = f"https://example.com/logos/{ticker.split('.')[0]}.png"  # Cambia esta URL a donde se encuentran los logotipos
    logo_path = f"logos/{ticker.split('.')[0]}.png"
    
    # Crea el directorio si no existe
    os.makedirs(os.path.dirname(logo_path), exist_ok=True)
    
    # Descarga la imagen
    response = requests.get(logo_url)
    if response.status_code == 200:
        with open(logo_path, 'wb') as f:
            f.write(response.content)
        return logo_path
    else:
        return None  # Retorna None si no se puede descargar

# Función para obtener datos
def get_data(tickers, period='1d', value_metric='Capitalización'):
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1y')  # Obtener datos del último año
        if len(hist) > 1:
            if period == '1d':
                period_data = hist.tail(2)
                volume_sum = hist['Volume'].iloc[-1]
            elif period == '1wk':
                period_data = hist.resample('W').last().tail(2)
                volume_sum = hist['Volume'].resample('W').sum().iloc[-1]
            elif period == '1mo':
                period_data = hist.resample('M').last().tail(2)
                volume_sum = hist['Volume'].resample('M').sum().iloc[-1]
            elif period == '1y':
                period_data = hist.resample('A').last().tail(2)
                volume_sum = hist['Volume'].resample('A').sum().iloc[-1]
            else:
                raise ValueError("Periodo no soportado")

            if len(period_data) >= 2:
                last_close = period_data['Close'].iloc[-1]
                previous_close = period_data['Close'].iloc[-2]
                performance = (last_close - previous_close) / previous_close * 100
                capi = volume_sum * last_close

                panel_type = 'Panel Líder' if ticker in tickers_panel_lider else 'Panel General'
                logo_path = download_logo(ticker)

                data.append({
                    'Ticker': ticker,
                    'Panel': panel_type,
                    'Volumen': volume_sum,
                    'Rendimiento': performance,
                    'Capitalización': capi,
                    'Value': capi,  # O volumen según el valor deseado
                    'Logo': logo_path  # Guarda la ruta del logo descargado
                })
    return pd.DataFrame(data)

# Configuración de la aplicación Streamlit
st.title("Análisis de Acciones")

# Selección del periodo
period = st.selectbox("Selecciona el periodo", ['1d', '1wk', '1mo', '1y'])

# Selección del valor
value_metric = st.selectbox("Selecciona el valor a mostrar", ['Capitalización', 'Volumen'])

# Obtener datos
resultados = get_data(tickers, period, value_metric)

# Filtrar datos válidos
resultados = resultados.dropna(subset=['Value', 'Rendimiento'])
resultados = resultados[resultados['Value'] > 0]

# Verificar si hay datos para mostrar
if not resultados.empty:
    # Crear el gráfico de treemap
    fig = px.treemap(resultados,
                     path=['Panel', 'Ticker'],
                     values='Value',
                     color='Rendimiento',
                     color_continuous_scale=[(0, 'red'), (0.5, 'white'), (1, 'darkgreen')],
                     color_continuous_midpoint=0,
                     title=f"Panel general: {value_metric} y Rendimiento ({period})")

    # Agregar imágenes de logotipos
    for index, row in resultados.iterrows():
        if row['Logo'] is not None:  # Verificar si se descargó el logo
            fig.add_layout_image(
                source=row['Logo'],
                x=row['Value'],  # Posicionar en el gráfico
                y=row['Rendimiento'],
                xref="x",
                yref="y",
                sizex=0.05,  # Ajustar el tamaño según sea necesario
                sizey=0.05,
                xanchor="center",
                yanchor="middle"
            )

    # Ajustar el tamaño del gráfico
    fig.update_layout(width=2500, height=800)

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)
else:
    st.warning("No hay datos válidos para mostrar.")


