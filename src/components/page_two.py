import streamlit as st
import os
import yfinance as yf
import seaborn as sns
#from yfinance import EquityQuery
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta, date
from utils.helpers import get_top_15_tickers, get_all_tickers_with_sectors

# Fetch stock data based on the ticker, period, and interval
def fetch_data_timeframe(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def show_comparative_graph(selected_tickers, start_date, end_date):
    if not selected_tickers:
        return None
    # Fetch historical data for each ticker
    all_data = {}
    for ticker in selected_tickers:
        try:
            data = fetch_data_timeframe(ticker, start_date, end_date)
            if not data.empty:
                data['pct_change'] = data['Close'].pct_change() * 100
                data['normalized'] = (100 + data['pct_change'].cumsum())
                all_data[ticker] = data['normalized']
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")

    #  graph comparativo
    if all_data:
        comparison_df = pd.DataFrame(all_data)
        fig = px.line(comparison_df, title='Comparação de Preços Normalizados')
        fig.update_layout(xaxis_title="Data", yaxis_title="Preço Normalizado (%)")
        st.plotly_chart(fig)

def show_correlation_matrix(data, column_name: str):
    if not data.empty:
        try:
            df_corr = data[[column_name]].corr(method='spearman')
            cm = sns.color_palette("Blues", as_cmap=True)
            st.dataframe(df_corr.style.background_gradient(cmap=cm), use_container_width=True)
        except Exception as e:
            st.error(f"Error showing correlation matrix: {e}")

# Sidebar for user input parameters
with st.sidebar:
    # Mapping of time periods to data intervals
    time_period = {
        '1 dia': ['1d', '5m'],
        '5 dias': ['5d', '30m'],
        '1 mês': ['1mo', '1h'],
        '6 meses': ['6mo', '1d'],
        '1 ano': ['1y', '1wk'],
        '5 anos': ['5y', '1mo'],
        'máximo': ['max', '3mo']
    }

    # Mapping of sectors to tickers
    sector_mapping = {
        'all': "Todos",
        'Basic Materials': "Commodities",
        'Communication Services': "Telecomunicações",
        'Consumer Cyclical': "Consumo Cíclico",
        'Consumer Defensive': "Consumo Defensivo",
        'Energy': "Energia",
        'Financial Services': "Serviços Financeiros",
        'Healthcare': "Saúde",
        'Industrials': "Indústrias",
        'Real Estate': "Imóveis",
        'Technology': "Tecnologia",
        'Utilities': "Utilidades"
    }

    st.markdown('## Parâmetros de Busca', help='Este dashboard fornece dados de ações e indicadores técnicos para diferentes períodos de tempo. Use a barra lateral para personalizar sua visualização.')

    selected_sector = st.selectbox("Selecionar o Setor", list(sector_mapping.values()))
    selected_sector_key = [key for key, value in sector_mapping.items() if value == selected_sector]

    #tickers_list = get_top_15_tickers()
    tickers_list = get_all_tickers_with_sectors(selected_sector_key)

    
    selected_tickers = st.multiselect("Selecionar os Tickers", tickers_list, key="grafico_tickers", max_selections=4)

    start_date = st.date_input("Data Inicial", date(2023, 1, 1))
    end_date = st.date_input("Data Final", date.today())

    # Sidebar information section
    st.subheader('Sobre')
    st.warning('As relações apresentadas não são recomendações de compra ou venda, mas sim uma ferramenta de visualização de dados.', icon=':material/warning:')

# Update the dashboard based on user input
if len(selected_tickers) > 0:
    st.spinner('Carregando dados...')
    try:
        data = fetch_data_timeframe(selected_tickers, start_date, end_date)
        if not data.empty:
            st.header(f'Comparação de Preços Normalizados - {selected_sector}', )
            show_comparative_graph(selected_tickers, start_date, end_date)

            option_map = {
                "Fechamento": "Close",
                "Abertura": "Open",
                "Máximo": "High",
                "Mínimo": "Low",
                "Volume": "Volume"
            }
            st.subheader(f'Correlação por:')
            selection = st.segmented_control(
                "Correlação por:",
                options=option_map.keys(),
                selection_mode="single",
                default="Fechamento",
                label_visibility="hidden"
            )
            show_correlation_matrix(data, option_map[selection])
    except Exception as e:
        st.error(f"Error fetching data: {e}")
    
else:
    st.info('Nenhum dado selecionado, por favor, selecione os tickers e o período de tempo.', icon=':material/info:')

