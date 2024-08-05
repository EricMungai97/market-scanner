import yfinance as yf
import pandas as pd

# Define the list of tickers from your favorites
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "META", "NFLX", "NVDA", "AMD", "BABA",   "AI", "ABNB", "ADBE", "AFRM", "BTU", "BYON", "CLVT", "CART", "CVNA",
    "DASH", "HOOD", "IOT", "NIO", "PLTR", "RBLX", "ROKU", "SHOP",
    "SPOT", "SNOW", "UPST", "SQ", "TTD", "U", "W", "Z" ,
    "AMD", "AMAT", "ARM", "AVGO", "DELL", "GCT", "MRVL", "MU", "NVDA",
    "QCOM", "TSM", "INTC", "IBM", "SMCI", "STX", "ON", "COHR", "HPE"]
# Define a function to detect a weekly outside bar
def detect_outside_bar(ticker):
    try:
        # Fetch weekly data for the ticker
        df = yf.download(ticker, period="1y", interval="1wk")
        
        # If no data is returned, skip this ticker
        if df.empty:
            print(f"No data found for {ticker}. Skipping...")
            return False

        # Calculate if the current bar is an outside bar
        df['outside_bar'] = (df['High'] > df['High'].shift(1)) & (df['Low'] < df['Low'].shift(1))

        # Check if the last row has an outside bar
        if df.shape[0] < 2:  # Ensure there is at least one previous week to compare
            print(f"Not enough data for {ticker}. Skipping...")
            return False
        
        return df.iloc[-1]['outside_bar']
    
    except Exception as e:
        print(f"Failed to process {ticker}: {e}")
        return False

# Initialize an empty list to store tickers with outside bars
outside_bar_tickers = []

# Scan each ticker
for ticker in tickers:
    if detect_outside_bar(ticker):
        outside_bar_tickers.append(ticker)

# Output the results
if outside_bar_tickers:
    print("Tickers with a weekly outside bar:")
    for ticker in outside_bar_tickers:
        print(ticker)
else:
    print("No tickers with a weekly outside bar found.")