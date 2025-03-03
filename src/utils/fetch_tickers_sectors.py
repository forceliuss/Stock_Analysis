import os
import pandas as pd
import yfinance as yf
from yfinance import EquityQuery
import time
from datetime import datetime

def fetch_all_tickers_with_sectors():
    """
    Fetches all tickers from the São Paulo exchange and their sectors,
    then saves them to a CSV file in the data directory.
    """
    print("Starting to fetch all tickers from São Paulo exchange...")
    
    # Path to save the CSV file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '../data')
    csv_path = os.path.join(data_dir, 'all_tickers_sectors.csv')
    
    # Create data directory if it doesn't exist
    os.makedirs(data_dir, exist_ok=True)
    
    # Initialize a list to store ticker data
    all_tickers_data = []
    
    # Total number of tickers to fetch (as mentioned in the query)
    total_tickers = 2093
    
    # Batch size
    batch_size = 250
    
    # Calculate number of batches needed
    num_batches = (total_tickers + batch_size - 1) // batch_size
    
    # Track progress
    processed_tickers = 0
    
    # Fetch tickers in batches
    for batch in range(num_batches):
        print(f"Processing batch {batch+1}/{num_batches}...")
        
        # Create query for São Paulo exchange
        q = EquityQuery('is-in', ['exchange', 'SAO'])
        
        # Calculate offset for pagination
        offset = batch * batch_size
        
        # Fetch batch of tickers
        try:
            response = yf.screen(q, sortField='percentchange', sortAsc=True, size=batch_size, offset=offset)
            
            # Check if we got any quotes
            if 'quotes' not in response or not response['quotes']:
                print(f"No quotes found in batch {batch+1}. Stopping.")
                break
            
            # Process each ticker in the batch
            for quote in response['quotes']:
                ticker_symbol = quote['symbol']
                processed_tickers += 1
                
                print(f"Processing ticker {processed_tickers}/{total_tickers}: {ticker_symbol}")
                
                # Try to fetch sector information
                sector = "Unknown"
                try:
                    ticker_info = yf.Ticker(ticker_symbol).get_info()
                    if 'sector' in ticker_info and ticker_info['sector']:
                        sector = ticker_info['sector']
                except Exception as e:
                    print(f"Error fetching sector for {ticker_symbol}: {str(e)}")
                
                # Add to our data list
                all_tickers_data.append({
                    'ticker': ticker_symbol,
                    'sector': sector
                })
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.2)
            
        except Exception as e:
            print(f"Error fetching batch {batch+1}: {str(e)}")
        
        # Save progress after each batch
        temp_df = pd.DataFrame(all_tickers_data)
        temp_df.to_csv(csv_path, index=False)
        print(f"Progress saved: {len(all_tickers_data)} tickers processed so far.")
        
        # Add a delay between batches to avoid rate limiting
        if batch < num_batches - 1:
            print("Waiting before next batch...")
            time.sleep(5)
    
    # Create final DataFrame and save to CSV
    tickers_df = pd.DataFrame(all_tickers_data)
    tickers_df.to_csv(csv_path, index=False)
    
    print(f"Completed! {len(all_tickers_data)} tickers saved to {csv_path}")
    return tickers_df

def filter_out_fraction_tickers():
    """
    Filters out fraction tickers (those ending with 'F.SA') from the all_tickers_sectors.csv file
    and saves the result to a new CSV file named 'filtered_tickers_sectors.csv'.
    
    Returns:
        pd.DataFrame: DataFrame containing the filtered tickers and their sectors.
    """
    print("Starting to filter out fraction tickers...")
    
    # Path to read the original CSV file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '../data')
    input_csv_path = os.path.join(data_dir, 'all_tickers_sectors.csv')
    output_csv_path = os.path.join(data_dir, 'filtered_tickers_sectors.csv')
    
    # Read the original CSV file
    try:
        df = pd.read_csv(input_csv_path)
        print(f"Read {len(df)} tickers from {input_csv_path}")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None
    
    # Filter out fraction tickers (those with 'F.SA' at the end)
    filtered_df = df[~df['ticker'].str.contains('F\.SA$')]
    
    # Count how many tickers were filtered out
    num_filtered_out = len(df) - len(filtered_df)
    print(f"Filtered out {num_filtered_out} fraction tickers")
    print(f"Remaining tickers: {len(filtered_df)}")
    
    # Save the filtered DataFrame to a new CSV file
    filtered_df.to_csv(output_csv_path, index=False)
    print(f"Filtered tickers saved to {output_csv_path}")
    
    return filtered_df

if __name__ == "__main__":
    # Record start time
    start_time = datetime.now()
    print(f"Script started at: {start_time}")
    
    # Run the function
    #fetch_all_tickers_with_sectors()
    
    # Filter out fraction tickers
    filter_out_fraction_tickers()

    # Record end time and calculate duration
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"Script completed at: {end_time}")
    print(f"Total duration: {duration}") 