import requests
import time
import pandas as pd
import statistics

def stress_test_system():
    base_url = "http://127.0.0.1:5000"
    print(f"--- 🦸 Superhuman Stress Test Initiated ---")
    
    # 1. Fetch All Data
    start_time = time.time()
    try:
        print("1. [Load] Fetching all stock data...")
        resp = requests.get(f"{base_url}/api/data")
        stocks = resp.json()
        duration = time.time() - start_time
        print(f"   -> Fetched {len(stocks)} stocks in {duration:.2f} seconds.")
    except Exception as e:
        print(f"   -> [CRITICAL FAIL] Server unreachable: {e}")
        return

    if not stocks:
        print("   -> [FAIL] No stocks returned.")
        return

    # 2. Data Integrity Analysis
    print("\n2. [Integrity] Checking Data Quality...")
    missing_pe = 0
    missing_pbv = 0
    missing_de = 0
    missing_ddm = 0
    missing_score = 0
    
    ddm_values = []
    prices = []
    scores = []
    
    for s in stocks:
        if s.get('pe_trailing') == "-": missing_pe += 1
        if s['details'].get('price_to_book') == "-": missing_pbv += 1
        if s['details'].get('debt_to_equity') == "-": missing_de += 1
        
        if s.get('ddm_value') == "-" or s.get('ddm_value') == 0: 
            missing_ddm += 1
        else:
            try:
                val = float(s['ddm_value'])
                price = float(s['price'])
                ddm_values.append(val)
                prices.append(price)
            except:
                pass
                
        if s.get('score') is None: missing_score += 1
        else: scores.append(s['score'])

    print(f"   -> Missing P/E: {missing_pe}/{len(stocks)} ({missing_pe/len(stocks)*100:.1f}%)")
    print(f"   -> Missing P/BV: {missing_pbv}/{len(stocks)} ({missing_pbv/len(stocks)*100:.1f}%)")
    print(f"   -> Missing D/E: {missing_de}/{len(stocks)} ({missing_de/len(stocks)*100:.1f}%)")
    print(f"   -> Missing/Zero DDM: {missing_ddm}/{len(stocks)} ({missing_ddm/len(stocks)*100:.1f}%) - [WEAKNESS] High failure rate in DDM?")

    # 3. Valuation Reality Check
    print("\n3. [Valuation] Reality Check (Price vs DDM)...")
    undervalued_count = 0
    for p, d in zip(prices, ddm_values):
        if p < d: undervalued_count += 1
    
    print(f"   -> Undervalued Stocks (Price < DDM): {undervalued_count}/{len(ddm_values)} ({undervalued_count/len(ddm_values)*100:.1f}% of valid DDMs)")
    
    if undervalued_count / len(ddm_values) > 0.8:
        print("   -> [WARNING] System is too OPTIMISTIC. 80%+ stocks are 'Buy'. Check Assumptions (g=3%, k=10%).")
    elif undervalued_count / len(ddm_values) < 0.1:
        print("   -> [WARNING] System is too PESSIMISTIC. <10% stocks are 'Buy'. Check Assumptions.")
    else:
        print("   -> [PASS] Balanced Valuation Distribution.")

    # 4. Score Distribution
    print("\n4. [Scoring] Grade Distribution...")
    grade_a = scores.count(6) + scores.count(7)
    grade_b = scores.count(4) + scores.count(5)
    grade_c = scores.count(2) + scores.count(3)
    grade_d = scores.count(0) + scores.count(1)
    
    print(f"   -> Grade A (6-7): {grade_a}")
    print(f"   -> Grade B (4-5): {grade_b}")
    print(f"   -> Grade C (2-3): {grade_c}")
    print(f"   -> Grade D (0-1): {grade_d}")
    
    if grade_a == 0:
        print("   -> [WEAKNESS] Criteria too strict? No Grade A stocks found.")

    # 5. Cyclical Trap Simulation
    print("\n5. [Simulation] Cyclical Trap Check (RCL - Shipping)...")
    rcl = next((s for s in stocks if "RCL" in s['symbol']), None)
    if rcl:
        print(f"   -> RCL Score: {rcl['score']} ({rcl['grade']})")
        print(f"   -> RCL P/E: {rcl['pe_trailing']}")
        print(f"   -> RCL Details: {rcl['score_details']}")
        if rcl['score'] >= 5:
            print("   -> [RISK] High Score for Cyclical Stock! Ensure user checks industry cycle.")
    else:
        print("   -> RCL not in list.")

if __name__ == "__main__":
    stress_test_system()
