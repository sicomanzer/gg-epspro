import requests
import time

def test_backend_logic():
    base_url = "http://127.0.0.1:5000"
    
    print(f"--- Testing System at {base_url} ---")
    
    # 1. Test /api/stocks
    try:
        resp = requests.get(f"{base_url}/api/stocks")
        if resp.status_code == 200:
            stocks = resp.json()
            print(f"1. Stocks Loaded: {len(stocks)} stocks found.")
        else:
            print(f"1. Failed to load stocks: {resp.status_code}")
            return
    except Exception as e:
        print(f"1. Connection Error: {e}")
        return

    # 2. Test /api/data (Sample)
    # Since fetching all takes time, we can't easily fetch just one via API unless we modify backend or just wait.
    # However, let's try to add a specific test stock and see.
    # Actually, let's just use the `get_stock_data` function directly by importing app? 
    # No, better to test the running server if possible, or unit test the function.
    # Importing app might trigger server run if not careful, but we have `if __name__ == '__main__':`.
    
    print("2. Verifying Calculations via internal function import...")
    try:
        from app import get_stock_data
        
        test_ticker = "ADVANC"
        print(f"   Fetching data for {test_ticker}...")
        data = get_stock_data(test_ticker)
        
        if "error" in data:
            print(f"   Error fetching {test_ticker}: {data['error']}")
        else:
            print(f"   Symbol: {data['symbol']}")
            print(f"   Price: {data['price']}")
            print(f"   P/E: {data['pe_trailing']}")
            print(f"   P/BV: {data['details']['price_to_book']}")
            print(f"   ROE: {data['details']['roe']}")
            print(f"   D/E (BS): {data['details']['debt_to_equity']}")
            print(f"   Dividend Yield: {data['dividend_yield']}%")
            print(f"   DDM Value: {data['ddm_value']}")
            print(f"   Score: {data['score']}/7 (Grade {data['grade']})")
            print(f"   Score Details: {data['score_details']}")
            
            # Basic Assertions
            if data['score'] is not None:
                print("   [PASS] Score calculation exists.")
            if data['ddm_value'] != "-":
                print("   [PASS] DDM calculation exists.")
            
    except Exception as e:
        print(f"   Test Failed: {e}")

if __name__ == "__main__":
    test_backend_logic()
