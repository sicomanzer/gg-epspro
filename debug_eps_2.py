import yfinance as yf
import pandas as pd
import datetime

# Set cache
try:
    yf.set_tz_cache_location("yfinance_cache")
except:
    pass

def check_stock(ticker):
    print(f"--- {ticker} ---")
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
        print(f"Trailing EPS: {info.get('trailingEps')}")
        print(f"Forward EPS: {info.get('forwardEps')}")
        
        financials = stock.financials
        if "Basic EPS" in financials.index:
            eps = financials.loc["Basic EPS"]
            print("Basic EPS from Financials:")
            print(eps)
    except Exception as e:
        print(f"Error: {e}")

check_stock("ADVANC.BK")
check_stock("PTT.BK")
