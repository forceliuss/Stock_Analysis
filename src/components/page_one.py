import streamlit as st
import pandas as pd
import yfinance as yf
import time
#from yahooquery import get_symbols_by_exchange
from datetime import datetime, timedelta
import pytz
import ta
import os
from utils.helpers import format_currency, format_percentage, get_top_15_tickers, get_all_tickers_with_sectors

# Fetch stock data based on the ticker, period, and interval
def fetch_data_interval(ticker, period, interval):
    # For shorter periods, use the standard download method
    if period not in ['6mo', '1y', '5y', 'max']:
        return yf.download(ticker, period=period, interval=interval, multi_level_index=True)
    
    # For longer periods, break it into monthly chunks
    end_date = datetime.now()
    
    # Calculate start date based on period
    if period == '6mo':
        start_date = end_date - timedelta(days=180)
    elif period == '1y':
        start_date = end_date - timedelta(days=365)
    elif period == '5y':
        start_date = end_date - timedelta(days=365*5)
    elif period == 'max':
        # Using a reasonably long period - adjust if needed
        start_date = end_date - timedelta(days=365*20)
    
    # Convert to string format for yfinance
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Initialize an empty list to store monthly dataframes
    monthly_data = []
    current_date = start_date
    
    # Fetch data month by month
    while current_date < end_date:
        # Calculate next month date
        next_month = current_date + timedelta(days=30)  # Approximation of one month
        if next_month > end_date:
            next_month = end_date
        
        # Format dates for yfinance
        current_date_str = current_date.strftime('%Y-%m-%d')
        next_month_str = next_month.strftime('%Y-%m-%d')
        
        # Download data for this month
        print(f"Downloading data for {ticker} from {current_date_str} to {next_month_str}")
        monthly_chunk = yf.download(
            ticker, 
            start=current_date_str, 
            end=next_month_str, 
            interval=interval, 
            multi_level_index=True
        )
        
        # Add to our list if data is not empty
        if not monthly_chunk.empty:
            monthly_data.append(monthly_chunk)
        
        # Move to next month
        current_date = next_month
    
    # Combine all monthly chunks
    if monthly_data:
        combined_data = pd.concat(monthly_data)
        # Remove duplicate entries that might exist at month boundaries
        combined_data = combined_data[~combined_data.index.duplicated(keep='first')]
        return combined_data
    else:
        # Return empty DataFrame if no data was found
        return pd.DataFrame()

# Flatten the data to a single DataFrame
def flatten_data(data, tickers=None):
    # Check if we have a multi-index DataFrame
    if isinstance(data.columns, pd.MultiIndex):
        # Convert multi-level columns to a flat DataFrame
        # Create a new DataFrame to store the flattened data
        flattened_data = []
        
        # For each ticker in the second level of the multi-index
        for ticker in data.columns.levels[1]:
            # Get data for this ticker
            ticker_data = data.xs(ticker, axis=1, level=1).copy()
            
            # Ensure the index is timezone-aware
            if hasattr(ticker_data.index, 'tzinfo') and ticker_data.index.tzinfo is None:
                ticker_data.index = ticker_data.index.tz_localize('UTC')
                
            # Add a Ticker column
            ticker_data['Ticker'] = ticker
            # Add to the list
            flattened_data.append(ticker_data)
        
        # Concatenate all the ticker dataframes
        if flattened_data:
            data = pd.concat(flattened_data)
        else:
            # If there's only one ticker, it might not have a multi-level structure
            if tickers and len(tickers) > 0:
                data['Ticker'] = tickers[0]
    else:
        # If not a multi-index, assume it's a single ticker
        if 'Ticker' not in data.columns and tickers and len(tickers) > 0:
            data['Ticker'] = tickers[0]
    return data

# Process data to ensure it is timezone-aware and has the correct format
def process_data(data, period):
    # Continue with normal processing
    # Check if the index is timezone-naive and localize if needed
    if data.index.tzinfo is None:
        data.index = data.index.tz_localize('UTC')
    
    # Now convert to Sao Paulo timezone
    data.index = data.index.tz_convert('America/Sao_Paulo')
    data.reset_index(inplace=True)
    if period not in ['6mo', '1y', '5y', 'max']:
        data['Data'] = pd.to_datetime(data['Datetime']).dt.strftime('%d/%m/%Y %H:%M')
    else:
        data['Data'] = pd.to_datetime(data['Date']).dt.strftime('%d/%m/%Y %H:%M')

    data.rename(columns={
            "Open": "Abertura",
            "High": "Máxima",
            "Low": "Mínima",
            "Close": "Fechamento",
            "Volume": "Volume"
        }, inplace=True)
    return data

# Calculate basic metrics from the stock data
def calculate_metrics(data, ticker=None):
    # If a ticker is specified, filter the data for that ticker
    if ticker and 'Ticker' in data.columns:
        data = data[data['Ticker'] == ticker]
    
    last_close = data['Fechamento'].iloc[-1]
    prev_close = data['Fechamento'].iloc[0]
    change = last_close - prev_close
    pct_change = (change / prev_close) * 100
    high = data['Máxima'].max()
    low = data['Mínima'].min()
    volume = data['Volume'].sum()
    return last_close, change, pct_change, high, low, volume

# Add simple moving average (SMA) and exponential moving average (EMA) indicators
def add_technical_indicators(data):
    data['SMA_20'] = ta.trend.sma_indicator(data['Close'], window=20)
    data['EMA_20'] = ta.trend.ema_indicator(data['Close'], window=20)
    return data




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
    time_period_label = st.selectbox('Período de Tempo', ['1 dia', '5 dias', '1 mês', '6 meses', '1 ano', '5 anos', 'máximo'])

    # Sidebar information section
    st.subheader('Sobre')
    st.warning('As relações apresentadas não são recomendações de compra ou venda, mas sim uma ferramenta de visualização de dados.', icon=':material/warning:')


# 2B: MAIN CONTENT AREA ############

# Update the dashboard based on user input
if len(selected_tickers) > 0:
    st.header(f'Comparação último(s) {time_period_label}')

    with st.spinner('Carregando dados...'):
        try:
            time.sleep(2)
            data = fetch_data_interval(selected_tickers, time_period[time_period_label][0], time_period[time_period_label][1])
            #st.write(data)

            if data.empty:
                st.error('Nenhum dado encontrado para o período selecionado.', icon=':material/cancel:')
            else:
                data = process_data(data, time_period[time_period_label][0])
                flattened_data = flatten_data(data, selected_tickers)
                metrics = {}
                # Loop through all selected tickers
                ticker_cols = st.columns(len(selected_tickers))
                for i, ticker in enumerate(selected_tickers):
                    
                    # Filter data for the current ticker
                    data_ticker = flattened_data[flattened_data['Ticker'] == ticker]
                    
                    # Skip if no data for this ticker
                    if len(data_ticker) == 0:
                        continue
                        
                    # Calculate metrics for this ticker
                    metrics[ticker] = {
                        'last_close': data_ticker['Fechamento'].iloc[-1],
                        'last_open': data_ticker['Abertura'].iloc[-1],
                        'last_high': data_ticker['Máxima'].iloc[-1],
                        'last_low': data_ticker['Mínima'].iloc[-1],
                        'last_volume': data_ticker['Volume'].iloc[-1],
                        'time_average': data_ticker['Fechamento'].mean()
                    }
                    
                    # Calculate percentage change
                    var_delta = format_percentage(((metrics[ticker]['last_close'] - metrics[ticker]['last_open']) / metrics[ticker]['last_open']))
                    
                    # Display metrics for this ticker
                    with ticker_cols[i]:
                        with st.expander(ticker, expanded=True):
                            #st.metric(label="Ticker", value=ticker, label_visibility="hidden")
                            #st.markdown("<hr style='margin: 10px 0; opacity: 0.8;'>", unsafe_allow_html=True)
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(label="Última Abertura", value=format_currency(metrics[ticker]['last_open']))
                            with col2:
                                st.metric(label="Último Fechamento", value=format_currency(metrics[ticker]['last_close']), 
                                        delta=var_delta)
                            st.markdown("<hr style='margin: 10px 0; opacity: 0.8;'>", unsafe_allow_html=True)
                            st.metric(label="Fechamento Médio", value=format_currency(metrics[ticker]['time_average']))
                    
                    # Add a small space between tickers for better visual separation
                    # if i < len(selected_tickers) - 1:
                    #     st.markdown("<hr style='margin: 10px 0; opacity: 0.3;'>", unsafe_allow_html=True)
                
                # st.subheader(f'Gráfico Comparativo - {selected_tickers}')
                
                # Display historical data and technical indicators
                st.subheader('Dados Históricos')
                st.dataframe(data[['Data', 'Abertura', 'Máxima', 'Mínima', 'Fechamento', 'Volume']], use_container_width=True, hide_index=True)
                
                
        except Exception as e:
            #st.error(f'API Yahoo Finance: {str(e)}')
            st.info('Nada encontrado para o período selecionado. Tente selecionar um período de tempo diferente.', icon=':material/info:')
else:
    st.info('Nenhum dado selecionado, por favor, selecione os tickers e o período de tempo.', icon=':material/info:')
