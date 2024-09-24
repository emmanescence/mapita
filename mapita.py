import yfinance as yf
import pandas as pd
import plotly.express as px
import streamlit as st

# Tickers
tickers_panel_lider = [
    'ALUA.BA', 'BBAR.BA', 'BMA.BA', 'BYMA.BA', 'CEPU.BA', 'COME.BA',
    'CRES.BA', 'CVH.BA', 'EDN.BA', 'GGAL.BA', 'HARG.BA', 'LOMA.BA',
    'MIRG.BA', 'METR.BA', 'PAMP.BA', 'SUPV.BA', 'TECO2.BA', 'TGNO4.BA', 'TGSU2.BA',
    'TRAN.BA', 'TXAR.BA', 'VALO.BA', 'YPFD.BA'
]

tickers_panel_general = [
    'AGRO.BA', 'AUSO.BA', 'BHIP.BA', 'BOLT.BA', 'BPAT.BA', 'CADO.BA', 'CAPX.BA', 'CARC.BA', 'CECO2.BA',
    'CELU.BA', 'CGPA2.BA', 'CTIO.BA', 'DGCE.BA', 'DGCU2.BA', 'DOME.BA', 'DYCA.BA', 'FERR.BA', 'FIPL.BA',
    'GARO.BA', 'GBAN.BA', 'GCDI.BA', 'GCLA.BA', 'GRIM.BA', 'HAVA.BA', 'INTR.BA', 'INVJ.BA', 'IRSA.BA',
    'LEDE.BA', 'LONG.BA', 'MOLA.BA', 'MOLI.BA', 'MORI.BA', 'OEST.BA', 'PATA.BA', 'RIGO.BA',
    'ROSE.BA', 'SAMI.BA', 'SEMI.BA'
]

# URL base de GitHub donde están alojados los logotipos (ajusta según tu repositorio)
base_url_logos = "https://raw.githubusercontent.com/usuario/repositorio/main/logos/"  # Ajusta esta URL

# Función para obtener datos
def get_data(tickers, period='1d', value_metric='Capitalización'):
    data = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period='1y')  # Obtener datos del último año
        if len(hist) > 1:
            # Determinar el periodo para el cálculo del rendimiento y el volumen
            if period == '1d':
                period_data = hist.tail(2)  # Últimos dos días
                volume_sum = hist['Volume'].iloc[-1]  # Volumen del último día
            elif period == '1wk':
                period_data = hist.resample('W').last().tail(2)  # Últimas dos semanas
                volume_sum = hist['Volume'].resample('W').sum().iloc[-1]  # Sumar volumen semanal
            elif period == '1mo':
                period_data = hist.resample('M').last().tail(2)  # Últimos dos meses
                volume_sum = hist['Volume'].resample('M').sum().iloc[-1]  # Sumar volumen mensual
            elif period == '1y':
                period_data = hist.resample('A').last().tail(2)  # Últimos dos años
                volume_sum = hist['Volume'].resample('A').sum().iloc[-1]  # Sumar volumen anual
            else:
                raise ValueError("Periodo no soportado")

            if len(period_data) >= 2:
                # Obtener precios de cierre
                last_close = period_data['Close'].iloc[-1]
                previous_close = period_data['Close'].iloc[-2]

                # Calcular el rendimiento
                performance = (last_close - previous_close) / previous_close * 100

                # Calcular la capitalización
                capi = volume_sum * last_close

                # Determinar el valor a mostrar según la métrica seleccionada
                value = capi if value_metric == 'Capitalización' else volume_sum

                # Agregar panel como 'Panel Líder' o 'Panel General'
                panel_type = 'Panel Líder' if ticker in tickers_panel_lider else 'Panel General'

                # Crear la URL del logotipo
                logo_url = f"{base_url_logos}{ticker}.png"

                data.append({
                    'Ticker': ticker,
                    'Panel': panel_type,
                    'Volumen': volume_sum,
                    'Rendimiento': performance,
                    'Capitalización': capi,
                    'Value': value,
                    'Logo': logo_url  # Agregar la URL del logo
                })
            else:
                continue  # Omitir si no hay suficientes datos para calcular el rendimiento
        else:
            continue  # Omitir si no hay suficientes datos históricos
    return pd.DataFrame(data)

# Configuración de la aplicación Streamlit
st.title('Análisis de Mercado Bursátil Argentino - https://x.com/iterAR_eco')
st.sidebar.header('Parámetros de Selección')

# Parámetros de selección en la barra lateral
panel = st.sidebar.selectbox('Seleccionar Panel', ('todos', 'panel_lider', 'panel_general'))
period = st.sidebar.selectbox('Seleccionar Periodo', ('diario', 'semana en curso', 'mes en curso', 'año en curso'))
value_metric = st.sidebar.selectbox('Métrica de Valor', ('Capitalización', 'Volumen'))
range_colors = st.sidebar.slider('Rango de Colores para Rendimiento', min_value=1, max_value=10, value=3)

# Mapear períodos a códigos
period_mapping = {
    'diario': '1d',
    'semana en curso': '1wk',
    'mes en curso': '1mo',
    'año en curso': '1y'
}

# Seleccionar tickers según el panel
if panel == 'panel_lider':
    tickers = tickers_panel_lider
elif panel == 'panel_general':
    tickers = tickers_panel_general
elif panel == 'todos':
    tickers = tickers_panel_lider + tickers_panel_general
else:
    st.error("Panel no soportado")

# Obtener datos
resultados = get_data(tickers, period_mapping.get(period, '1d'), value_metric)

# Filtrar datos válidos (remover NaNs)
resultados = resultados.dropna(subset=['Value', 'Rendimiento'])
resultados = resultados[resultados['Value'] > 0]

# Verificar si hay datos para mostrar
if not resultados.empty:
    # Crear el gráfico de treemap con etiquetas personalizadas y escala de colores ajustada
    fig = px.treemap(resultados,
                     path=['Panel', 'Ticker'],  # Incluir el nivel 'Panel' para el agrupamiento
                     values='Value',
                     color='Rendimiento',
                     color_continuous_scale=[(0, 'red'), (0.5, 'white'), (1, 'darkgreen')],
                     color_continuous_midpoint=0,  # Punto medio de la escala en 0%
                     range_color=[-range_colors, range_colors],  # Ajusta según el rango de rendimiento esperado
                     title=f"Panel general: {value_metric} y Rendimiento ({period})")

    # Ajustar el tamaño del gráfico
    fig.update_layout(width=2500, height=800)

    # Personalizar la información en las etiquetas
    fig.update_traces(textinfo="label+text+value",
                      texttemplate="<b>%{label}</b><br><b>%{customdata[0]:.2f}%</b>" if not pd.isna(resultados['Rendimiento']).any() else "<b>%{label}</b>")

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

    # Mostrar logotipos debajo del gráfico
    st.subheader('Logotipos de las Acciones:')
    for index, row in resultados.iterrows():
        st.image(row['Logo'], width=50, caption=row['Ticker'])

else:
    st.warning("No hay datos válidos para mostrar.")
