import yfinance as yf
import pandas as pd

try:
    yf.set_tz_cache_location("yfinance_cache")
except:
    pass

def check_stock(ticker):
    print(f"--- Checking {ticker} ---")
    stock = yf.Ticker(ticker)
    info = stock.info
    
    keys = [
        "dividendYield",
        "revenueGrowth",
        "earningsGrowth",
        "returnOnAssets",
        "returnOnEquity",
        "profitMargins",
        "grossMargins",
        "operatingMargins"
    ]
    
    for k in keys:
        val = info.get(k)
        print(f"{k}: {val} (Type: {type(val)})")

stocks = ["AAV.BK", "ADVANC.BK", "PTT.BK"]
for s in stocks:
    check_stock(s)
