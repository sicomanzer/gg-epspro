import yfinance as yf
import pandas as pd
import datetime

def check_stock(ticker):
    print(f"--- {ticker} ---")
    stock = yf.Ticker(ticker)
    try:
        financials = stock.financials
        print("Financials columns:", financials.columns)
        if "Basic EPS" in financials.index:
            eps = financials.loc["Basic EPS"]
            print("Basic EPS:")
            print(eps)
            
            # Simulate my logic
            current_year = datetime.datetime.now().year # 2026
            years_eps = [current_year - 4, current_year - 3, current_year - 2, current_year - 1, current_year]
            print(f"Target years: {years_eps}")
            
            eps_dict = {d.year: float(v) for d, v in eps.items() if not pd.isna(v)}
            print("EPS Dict:", eps_dict)
            
            eps_trend = []
            for y in years_eps:
                val = eps_dict.get(y)
                eps_trend.append(val)
            print("Resulting Trend:", eps_trend)
        else:
            print("No Basic EPS found")
    except Exception as e:
        print(f"Error: {e}")

check_stock("ADVANC.BK")
check_stock("PTT.BK")
