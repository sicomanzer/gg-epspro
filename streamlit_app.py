import os
import re
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import streamlit as st

# Reuse data logic from Flask app
from app import get_stock_data, load_stocks, save_stocks

st.set_page_config(page_title="GG EPS Pro (Streamlit)", layout="wide")

st.title("GG EPS Pro")
st.caption("วิเคราะห์หุ้นไทยอย่างรวดเร็ว: ราคา อัตราส่วนหลัก DDM ค่า RSI คะแนนคุณภาพ และแนวโน้มกำไร/ปันผล")

# Sidebar: Manage stock list
with st.sidebar:
    st.header("จัดการรายชื่อหุ้น")
    tickers_text = st.text_area(
        "เพิ่มหุ้น (บรรทัดละ 1 ชื่อ หรือคั่นด้วย ,)",
        placeholder="AAV\nADVANC\nPTT\nKBANK",
        height=150,
    )
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        add_btn = st.button("เพิ่มหุ้น", use_container_width=True)
    with col_a2:
        clear_btn = st.button("ลบรายชื่อทั้งหมด", use_container_width=True)

    st.divider()
    st.header("ตั้งค่าเก็บข้อมูล")
    st.write("ตำแหน่งไฟล์รายชื่อหุ้น")
    st.code(os.environ.get("STOCKS_FILE_PATH", "stocks.json"), language=None)
    st.caption("บน Streamlit Cloud ไฟล์อาจไม่ถาวร แนะนำใช้ Render หากต้องการเก็บข้อมูลยาวๆ")

def parse_tickers(text: str):
    if not text:
        return []
    tickers = re.split(r"[,\s\n]+", text.strip())
    return [t.strip().upper() for t in tickers if t.strip()]

stocks = load_stocks()

if add_btn:
    new_ones = parse_tickers(tickers_text)
    added_any = False
    for t in new_ones:
        if t and t not in stocks:
            stocks.append(t)
            added_any = True
    if added_any:
        save_stocks(stocks)
        st.success(f"เพิ่มหุ้นแล้ว: {', '.join(new_ones)}")
        st.experimental_rerun()
    else:
        st.info("ไม่มีหุ้นใหม่ที่จะเพิ่ม")

if clear_btn:
    save_stocks([])
    st.warning("ลบรายชื่อหุ้นทั้งหมดแล้ว")
    st.experimental_rerun()

st.subheader("รายชื่อหุ้น")
if not stocks:
    st.info("ยังไม่มีหุ้นในรายการ เพิ่มจากแถบด้านซ้ายได้เลย")
    st.stop()

@st.cache_data(ttl=900, show_spinner=False)
def fetch_all(_stocks_tuple):
    tickers = list(_stocks_tuple)
    with ThreadPoolExecutor(max_workers=10) as ex:
        data = list(ex.map(get_stock_data, tickers))
    return data

refresh = st.button("รีเฟรชข้อมูล", help="ดึงข้อมูลล่าสุดและเคลียร์แคช")
if refresh:
    fetch_all.clear()

with st.spinner("กำลังดึงข้อมูล..."):
    data = fetch_all(tuple(stocks))

# Build table
def as_float(v):
    try:
        if v in ("-", None):
            return None
        return float(v)
    except Exception:
        return None

rows = []
for it in data:
    if "error" in it:
        continue
    d = it
    rows.append(
        {
            "Symbol": d["symbol"],
            "Name": d["name"],
            "Price": as_float(d["price"]),
            "P/E": as_float(d["pe_trailing"]),
            "P/E Fwd": as_float(d["pe_forward"]),
            "P/BV": as_float(d["details"]["price_to_book"]),
            "D/E": as_float(d["details"]["debt_to_equity"]),
            "ROA %": as_float(d["details"]["roa"]) * 100 if as_float(d["details"]["roa"]) is not None and abs(as_float(d["details"]["roa"])) < 1 else as_float(d["details"]["roa"]),
            "ROE %": as_float(d["details"]["roe"]) * 100 if as_float(d["details"]["roe"]) is not None and abs(as_float(d["details"]["roe"])) < 1 else as_float(d["details"]["roe"]),
            "Mkt Cap": as_float(d["market_cap"]),
            "Yield %": as_float(d["dividend_yield"]),
            "Div/Share": as_float(d["dividend_rate"]),
            "DDM": as_float(d["ddm_value"]),
            "Target": as_float(d["target_price"]),
            "RSI": as_float(d["rsi"]),
            "MOS %": as_float(d["mos"]),
            "Beta": as_float(d["beta"]),
            "52W High": as_float(d["high_52"]),
            "52W Low": as_float(d["low_52"]),
            "BVPS": as_float(d["bvps"]),
            "Rev Growth %": as_float(d["revenue_growth"]),
            "Earn Growth %": as_float(d["ebitda_growth"]),
            "Score": d["score"],
            "Grade": d["grade"],
            "Score Details": "\n".join(d.get("score_details", [])),
        }
    )

if not rows:
    st.error("ดึงข้อมูลไม่สำเร็จ")
    st.stop()

df = pd.DataFrame(rows)

# Summary
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("จำนวนหุ้น", len(df))
with col2:
    st.metric("ค่าเฉลี่ย P/E", f'{df["P/E"].dropna().mean():.2f}' if df["P/E"].notna().any() else "N/A")
with col3:
    st.metric("ค่าเฉลี่ย Yield", f'{df["Yield %"].dropna().mean():.2f}%' if df["Yield %"].notna().any() else "N/A")
with col4:
    if df["Mkt Cap"].notna().any():
        total_mcap = df["Mkt Cap"].dropna().sum() / 1_000_000_000_000
        st.metric("มูลค่ารวม (T)", f"{total_mcap:.2f}")
    else:
        st.metric("มูลค่ารวม (T)", "N/A")

# Filters
with st.expander("ตัวกรองขั้นสูง", expanded=False):
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    pe_max = c1.number_input("P/E ≤", value=50.0, min_value=0.0, step=1.0)
    pbv_max = c2.number_input("P/BV ≤", value=10.0, min_value=0.0, step=0.1)
    de_max = c3.number_input("D/E ≤", value=2.0, min_value=0.0, step=0.1)
    roe_min = c4.number_input("ROE ≥ %", value=10.0, min_value=0.0, step=1.0)
    yield_min = c5.number_input("Yield ≥ %", value=0.0, min_value=0.0, step=0.5)
    mcap_min_b = c6.number_input("Mkt Cap ≥ (B)", value=0.0, min_value=0.0, step=1.0)

    def pass_filter(x):
        def ok(v, pred):
            try:
                return pred(float(v))
            except Exception:
                return False
        conds = [
            ok(x["P/E"], lambda v: v <= pe_max) if pe_max > 0 else True,
            ok(x["P/BV"], lambda v: v <= pbv_max) if pbv_max > 0 else True,
            ok(x["D/E"], lambda v: v <= de_max) if de_max > 0 else True,
            ok(x["ROE %"], lambda v: v >= roe_min) if roe_min > 0 else True,
            ok(x["Yield %"], lambda v: v >= yield_min) if yield_min > 0 else True,
            ok(x["Mkt Cap"], lambda v: (v / 1_000_000_000) >= mcap_min_b) if mcap_min_b > 0 else True,
        ]
        return all(conds)

    if st.checkbox("เปิดใช้ตัวกรอง", value=False):
        df = df[df.apply(pass_filter, axis=1)]

# Remove stocks
with st.expander("ลบหุ้นออกจากรายการ"):
    to_remove = st.multiselect("เลือกหุ้นที่จะลบ", options=stocks)
    if st.button("ลบหุ้นที่เลือก"):
        if to_remove:
            new_list = [s for s in stocks if s not in to_remove]
            save_stocks(new_list)
            st.success(f"ลบแล้ว: {', '.join(to_remove)}")
            st.experimental_rerun()
        else:
            st.info("ยังไม่ได้เลือกหุ้น")

# Display table
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
)

st.caption("หมายเหตุ: ข้อมูลจาก yfinance อาจล่าช้า/ไม่ครบถ้วนในบางตัว")

