# Stock Analysis

A comprehensive stock analysis tool built with Streamlit that allows users to analyze stock data from the São Paulo exchange (B3). The application provides various features including stock price visualization, technical indicators, comparative analysis, and correlation matrices.

## Features

- **Stock Data Visualization**: View historical stock prices with customizable time periods and intervals
- **Technical Indicators**: Calculate and display various technical indicators for stock analysis
- **Comparative Analysis**: Compare multiple stocks on a normalized price basis
- **Correlation Matrix**: Analyze correlations between selected stocks
- **Sector-based Filtering**: Filter stocks by their respective sectors

## Installation

1. Clone the repository:

```bash
git clone https://github.com/forceliuss/Stock_Analysis.git
cd Stock_Analysis
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit application:

```bash
streamlit run src/app.py
```

## Project Structure

```
Stock_Analysis/
├── .git/
├── .streamlit/
├── local_storage/
├── src/
│   ├── app.py                    # Main application file
│   ├── components/
│   │   ├── page_one.py           # Home page component
│   │   └── page_two.py           # Graph page component
│   ├── data/
│   │   ├── all_tickers_sectors.csv       # All tickers with their sectors
│   │   ├── filtered_tickers_sectors.csv  # Filtered tickers with sectors
│   │   └── df_top_15_com_industry.csv    # Top 15 tickers with industry info
│   └── utils/
│       ├── helpers.py                    # Helper functions
│       └── fetch_tickers_sectors.py      # Functions to fetch ticker data
├── requirements.txt
└── .gitignore
```

## Libraries Used

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **yfinance**: Yahoo Finance API wrapper
- **Matplotlib**: Data visualization
- **Plotly**: Interactive data visualization
- **Seaborn**: Statistical data visualization
- **ta**: Technical analysis library

## Functions and Classes

### Main Application (app.py)

- `st.set_page_config()`: Configure the Streamlit page layout
- `st.Page()`: Define application pages
- `st.navigation()`: Set up navigation between pages

### Page One (page_one.py)

- `fetch_data_interval()`: Fetch stock data based on ticker, period, and interval
- `flatten_data()`: Flatten multi-index DataFrames
- `process_data()`: Process and prepare stock data
- `calculate_metrics()`: Calculate various financial metrics
- `add_technical_indicators()`: Add technical indicators to stock data

### Page Two (page_two.py)

- `fetch_data_timeframe()`: Fetch stock data for a specific timeframe
- `show_comparative_graph()`: Display comparative graph of multiple stocks
- `show_correlation_matrix()`: Display correlation matrix for selected stocks

### Helpers (helpers.py)

- `get_top_15_tickers()`: Get the top 15 tickers from the dataset
- `get_all_tickers_with_sectors()`: Get all tickers filtered by sector
- `format_number()`: Format numbers with thousands separator
- `format_percentage()`: Format numbers as percentages
- `format_currency()`: Format numbers as currency
- `format_large_number()`: Format large numbers with K/M/B suffixes
- `get_date_ranges()`: Get predefined date ranges
- `ensure_dir()`: Ensure a directory exists
- `get_trading_days()`: Get trading days between two dates
- `parse_date()`: Parse date strings
- `get_performance_summary()`: Get performance summary for selected tickers

### Fetch Tickers and Sectors (fetch_tickers_sectors.py)

_Separated file_

```bash
cd src/utils
python fetch_tickers_sectors.py
```

- `fetch_all_tickers_with_sectors()`: Fetch all tickers from São Paulo exchange with their sectors
- `filter_out_fraction_tickers()`: Filter out fraction tickers from the dataset
