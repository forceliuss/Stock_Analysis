import pandas as pd
import numpy as np
import logging
import os
from datetime import date, datetime, timedelta

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_top_15_tickers():
    data_frame_top_15_industry = pd.read_csv(os.path.join(CURRENT_DIR, '../data/df_top_15_com_industry.csv'), sep=';')
    return data_frame_top_15_industry['TckrSymb'].tolist()

def get_all_tickers_with_sectors(selected_sector_key):
    # Read the CSV file
    df = pd.read_csv(os.path.join(CURRENT_DIR, '../data/filtered_tickers_sectors.csv'), sep=',')
    
    # Filter the DataFrame based on the selected sector
    key = selected_sector_key[0]
    if key == 'all':
        return df['ticker'].tolist()
    else:
        filtered_df = df[df['sector'] == key]
        return filtered_df['ticker'].tolist()

def format_number(number, decimal_places=2):
    """
    Format a number with thousands separator and specific decimal places.
    
    Args:
        number: The number to format
        decimal_places (int): Number of decimal places to show
        
    Returns:
        str: Formatted number string
    """
    try:
        if pd.isna(number) or number is None:
            return "N/A"
            
        if isinstance(number, (int, float)):
            return f"{number:,.{decimal_places}f}"
        
        return str(number)
    except Exception as e:
        logging.error(f"Error formatting number: {e}")
        return str(number)


def format_percentage(number, decimal_places=2):
    """
    Format a number as a percentage with specific decimal places.
    
    Args:
        number: The number to format (0.1 = 10%)
        decimal_places (int): Number of decimal places to show
        
    Returns:
        str: Formatted percentage string
    """
    try:
        if pd.isna(number) or number is None:
            return "N/A"
            
        if isinstance(number, (int, float)):
            return f"{number * 100:,.{decimal_places}f}%"
        
        return str(number + "%")
    except Exception as e:
        logging.error(f"Error formatting percentage: {e}")
        return str(number)

def format_currency(number):
    """
    Format large numbers in a more readable way (K, M, B, T).
    
    Args:
        number: The number to format
        
    Returns:
        str: Formatted number string
    """
    try:
        if pd.isna(number) or number is None:
            return "N/A"
            
        if not isinstance(number, (int, float)):
            return str(number)
            
        abs_num = abs(number)
        sign = "R$ "
        
        if abs_num < 1000000:
            return f"{sign}{abs_num:.2f}"
        elif abs_num < 1000000000:
            return f"{sign}{abs_num/1000000:.2f}M"
        elif abs_num < 1000000000000:
            return f"{sign}{abs_num/1000000000:.2f}B"
        else:
            return f"{sign}{abs_num/1000000000000:.2f}T"
    except Exception as e:
        logging.error(f"Error formatting large number: {e}")
        return str(number)

def format_large_number(number):
    """
    Format large numbers in a more readable way (K, M, B, T).
    
    Args:
        number: The number to format
        
    Returns:
        str: Formatted number string
    """
    try:
        if pd.isna(number) or number is None:
            return "N/A"
            
        if not isinstance(number, (int, float)):
            return str(number)
            
        abs_num = abs(number)
        sign = "-" if number < 0 else ""
        
        if abs_num < 1000:
            return f"{sign}{abs_num:.2f}"
        elif abs_num < 1000000:
            return f"{sign}{abs_num/1000:.2f}K"
        elif abs_num < 1000000000:
            return f"{sign}{abs_num/1000000:.2f}M"
        elif abs_num < 1000000000000:
            return f"{sign}{abs_num/1000000000:.2f}B"
        else:
            return f"{sign}{abs_num/1000000000000:.2f}T"
    except Exception as e:
        logging.error(f"Error formatting large number: {e}")
        return str(number)


def get_date_ranges():
    """
    Generate common date ranges for analysis.
    
    Returns:
        dict: Dictionary with date range names as keys and (start_date, end_date) tuples as values
    """
    today = date.today()
    
    # Calculate date ranges
    one_month_ago = today - timedelta(days=30)
    three_months_ago = today - timedelta(days=90)
    six_months_ago = today - timedelta(days=180)
    one_year_ago = today - timedelta(days=365)
    ytd_start = date(today.year, 1, 1)
    
    # Create dictionary of date ranges
    date_ranges = {
        "1 Month": (one_month_ago, today),
        "3 Months": (three_months_ago, today),
        "6 Months": (six_months_ago, today),
        "1 Year": (one_year_ago, today),
        "Year to Date": (ytd_start, today)
    }
    
    return date_ranges


def ensure_dir(directory):
    """
    Ensure that a directory exists, creating it if needed.
    
    Args:
        directory (str): Directory path
        
    Returns:
        bool: True if directory exists or was created, False otherwise
    """
    try:
        if not os.path.exists(directory):
            logging.info(f"Creating directory: {directory}")
            os.makedirs(directory)
        return True
    except Exception as e:
        logging.error(f"Error creating directory: {e}")
        return False


def get_trading_days(start_date, end_date, include_holidays=False):
    """
    Get a list of trading days (weekdays) between two dates.
    
    Args:
        start_date (date): Start date
        end_date (date): End date
        include_holidays (bool): Whether to include holidays (simplified)
        
    Returns:
        list: List of dates representing trading days
    """
    # Create a range of all dates
    all_dates = pd.date_range(start=start_date, end=end_date)
    
    # Filter to weekdays only (Monday=0, Sunday=6)
    weekdays = all_dates[all_dates.dayofweek < 5]
    
    # Convert to list of date objects
    trading_days = [date.fromordinal(d.toordinal()) for d in weekdays]
    
    # Note: This doesn't account for market holidays
    # For a more accurate calendar, a specialized library or API should be used
    
    return trading_days


def parse_date(date_str, default=None):
    """
    Parse a date string in various formats.
    
    Args:
        date_str (str): Date string to parse
        default: Default value to return if parsing fails
        
    Returns:
        date: Parsed date object or default value if parsing fails
    """
    try:
        # Try various date formats
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y', '%m-%d-%Y'):
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        # If all formats fail, try pandas to_datetime
        return pd.to_datetime(date_str).date()
    except Exception as e:
        logging.warning(f"Error parsing date '{date_str}': {e}")
        return default


def get_performance_summary(price_data, tickers, column='close'):
    """
    Calculate performance summary for selected tickers.
    
    Args:
        price_data (DataFrame): DataFrame containing stock price data
        tickers (list): List of ticker symbols
        column (str): Price column to use
        
    Returns:
        DataFrame: Performance summary DataFrame
    """
    try:
        # Filter data for selected tickers
        filtered_data = price_data[price_data['symbol'].isin(tickers)]
        
        # Pivot the DataFrame
        pivot_df = filtered_data.pivot(index='datetime', columns='symbol', values=column).sort_index()
        
        # Calculate performance metrics
        performance = []
        for ticker in tickers:
            ticker_data = pivot_df[ticker].dropna()
            
            if len(ticker_data) < 2:
                continue
                
            latest_price = ticker_data.iloc[-1]
            first_price = ticker_data.iloc[0]
            
            # Calculate performance over various periods
            daily_change = ticker_data.pct_change().iloc[-1] if len(ticker_data) > 1 else 0
            
            # Weekly change (last 5 trading days)
            week_ago_idx = max(0, len(ticker_data) - 6)
            weekly_change = (latest_price / ticker_data.iloc[week_ago_idx] - 1) if week_ago_idx < len(ticker_data) - 1 else 0
            
            # Monthly change (last 21 trading days)
            month_ago_idx = max(0, len(ticker_data) - 22)
            monthly_change = (latest_price / ticker_data.iloc[month_ago_idx] - 1) if month_ago_idx < len(ticker_data) - 1 else 0
            
            # Overall change
            overall_change = (latest_price / first_price - 1)
            
            # Calculate volatility (standard deviation of returns)
            returns = ticker_data.pct_change().dropna()
            
            # Get volatility (annualized)
            if len(returns) > 1:
                volatility = returns.std() * np.sqrt(252)
            else:
                volatility = 0
            
            performance.append({
                'ticker': ticker,
                'latest_price': latest_price,
                'daily_change': daily_change,
                'weekly_change': weekly_change,
                'monthly_change': monthly_change,
                'overall_change': overall_change,
                'volatility': volatility
            })
        
        if not performance:
            return pd.DataFrame()
            
        return pd.DataFrame(performance)
    except Exception as e:
        logging.error(f"Error calculating performance summary: {e}")
        return pd.DataFrame() 