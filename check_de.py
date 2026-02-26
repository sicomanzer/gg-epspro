
import yfinance as yf

ticker = "ADVANC.BK"
stock = yf.Ticker(ticker)
info = stock.info
print(f"Total Debt: {info.get('totalDebt')}")
print(f"Total Liabilities: {info.get('totalLiabilities')}") # Check if this exists
print(f"Total Equity: {info.get('totalStockholderEquity')}") # Check if this exists
print(f"Book Value: {info.get('bookValue')}")
print(f"Shares: {info.get('sharesOutstanding')}")
