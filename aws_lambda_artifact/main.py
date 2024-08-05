from fastapi import FastAPI
from mangum import Mangum
from typing import List
import yfinance as yf
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
handler = Mangum(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your frontend domain if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to check if the market is open
def is_market_open():
    current_time = datetime.now()
    market_open = current_time.replace(hour=6, minute=30, second=0, microsecond=0)
    market_close = current_time.replace(hour=13, minute=0, second=0, microsecond=0)
    return market_open <= current_time <= market_close

# Function to check for Kicker patterns in batch
def check_kicker_patterns(df, ticker):
    if len(df[ticker]) < 2:
        return "None"
    
    bullish_kicker = (
        (df[ticker]['Close'].iloc[-2] < df[ticker]['Open'].iloc[-2]) and
        (df[ticker]['Open'].iloc[-1] > df[ticker]['Close'].iloc[-2]) and
        (df[ticker]['Close'].iloc[-1] > df[ticker]['Open'].iloc[-1]) and
        (df[ticker]['Open'].iloc[-1] >= df[ticker]['High'].iloc[-2])
    )
    
    bearish_kicker = (
        (df[ticker]['Close'].iloc[-2] > df[ticker]['Open'].iloc[-2]) and
        (df[ticker]['Open'].iloc[-1] < df[ticker]['Close'].iloc[-2]) and
        (df[ticker]['Close'].iloc[-1] < df[ticker]['Open'].iloc[-1]) and
        (df[ticker]['Open'].iloc[-1] <= df[ticker]['Low'].iloc[-2])
    )
    
    if bullish_kicker:
        return "Bullish Kicker"
    elif bearish_kicker:
        return "Bearish Kicker"
    else:
        return "None"

# Function to detect an Outside Bar pattern in batch
def detect_outside_bar(df, ticker):
    try:
        if df[ticker].empty or df[ticker].shape[0] < 2:
            return "None"

        # Outside Bar logic: Current bar's high is higher and low is lower than the previous bar
        outside_bar = (
            df[ticker]['High'].iloc[-1] > df[ticker]['High'].iloc[-2] and
            df[ticker]['Low'].iloc[-1] < df[ticker]['Low'].iloc[-2]
        )
        
        return "Outside Bar" if outside_bar else "None"
    
    except Exception as e:
        return f"Failed: {e}"

# Function to check for 2-1 Candle Pattern and Inside Bar in batch
def check_candle_patterns(df, ticker):
    try:
        if len(df[ticker]) < 3:
            return "None", "None"
        
        last_day = -1
        second_last_day = -2

        is_two_up = (df[ticker]['High'].iloc[second_last_day] > df[ticker]['High'].iloc[second_last_day-1]) and (df[ticker]['Low'].iloc[second_last_day] > df[ticker]['Low'].iloc[second_last_day-1])
        is_two_down = (df[ticker]['High'].iloc[second_last_day] < df[ticker]['High'].iloc[second_last_day-1]) and (df[ticker]['Low'].iloc[second_last_day] < df[ticker]['Low'].iloc[second_last_day-1])
        
        is_inside_bar = (
            (df[ticker]['High'].iloc[last_day] < df[ticker]['High'].iloc[second_last_day]) and
            (df[ticker]['Low'].iloc[last_day] > df[ticker]['Low'].iloc[second_last_day])
        )

        two_one_result = "2 Up Inside Bar" if is_two_up and is_inside_bar else "2 Down Inside Bar" if is_two_down and is_inside_bar else "None"
        
        return two_one_result, "Inside Bar" if is_inside_bar else "None"
    
    except Exception as e:
        return f"Failed 2-1: {e}", f"Failed Inside Bar: {e}"

# Define the API endpoint for checking patterns for a list of tickers
@app.post("/check_patterns/")
def check_patterns(tickers: List[str]):
    results = []
    
    # Download data for all tickers in one batch
    df_daily = yf.download(tickers, period="1y", interval="1d", group_by='ticker')
    df_weekly = yf.download(tickers, period="1y", interval="1wk", group_by='ticker')
    df_monthly = yf.download(tickers, period="1mo", interval="1d", group_by='ticker')
    
    for ticker in tickers:
        kicker_result = check_kicker_patterns(df_daily, ticker)
        outside_bar_result = detect_outside_bar(df_weekly, ticker)
        two_one_result, inside_bar_result = check_candle_patterns(df_daily, ticker)
        
        results.append({
            "ticker": ticker,
            "two_one_result": two_one_result,
            "inside_bar_result": inside_bar_result,
            "kicker_result": kicker_result,
            "outside_bar_result": outside_bar_result
        })
    
    return results

# Define the API endpoint for checking if the market is open
@app.get("/market_status")
def market_status():
    return {"market_open": is_market_open()}

@app.get('/')
def market_scanner():
    return "Welcome to the Market Scanner API!"