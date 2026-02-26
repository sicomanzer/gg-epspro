import yfinance as yf
import pandas as pd
import datetime

# Set cache
try:
    yf.set_tz_cache_location("yfinance_cache")
except:
    pass

def check_div_trend(ticker):
    print(f"--- {ticker} ---")
    stock = yf.Ticker(ticker)
    dividends = stock.dividends
    if not dividends.empty:
        div_yearly = dividends.resample('YE').sum()
        current_year = datetime.datetime.now().year
        div_dict = {ts.year: val for ts, val in div_yearly.items()}
        
        # Last 10 years ending at 2025
        trend = []
        years = []
        for y in range(current_year - 10, current_year):
            val = div_dict.get(y, 0.0)
            trend.append(float(val))
            years.append(y)
            
        print("Trend (2016-2025):", trend)
        
        # Analyze why it passed the filter
        # Logic 1: Avg Second Half > Avg First Half
        first_half = trend[:5]
        second_half = trend[5:]
        avg1 = sum(first_half)/len(first_half)
        avg2 = sum(second_half)/len(second_half)
        print(f"Avg First Half (2016-2020): {avg1:.4f}")
        print(f"Avg Second Half (2021-2025): {avg2:.4f}")
        print(f"Pass Avg Logic? {avg2 > avg1}")
        
        # Logic 2: Latest > First
        print(f"First (2016): {trend[0]}")
        print(f"Latest (2025): {trend[-1]}")
        print(f"Pass Simple Logic? {trend[-1] > trend[0]}")

stocks = ["DOHOME.BK", "CHG.BK", "CBG.BK", "BTG.BK", "BCH.BK", "BANPU.BK", "BAM.BK", "MTC.BK"]
for s in stocks:
    check_div_trend(s)
