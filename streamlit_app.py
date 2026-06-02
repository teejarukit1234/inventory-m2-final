import streamlit as st
import pandas as pd
import requests
import io
import base64
import time
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="คลังสินค้า M2", layout="centered")

# --- High-Fidelity Soft UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg: #f3f4f7;
        --card-bg: #ffffff;
        --text-main: #2d3436;
        --text-muted: #86868b;
        --accent-blue: #4b91ff;
    }

    html, body, [class*="css"] {
        font-family: 'Sarabun', 'Plus Jakarta Sans', sans-serif;
        background-color: var(--bg);
        color: var(--text-main);
    }
    
    .stApp {
        background-color: var(--bg);
        max-width: 900px;
        margin: 0 auto;
    }

    h1 {
        font-weight: 800;
        color: #2d3436;
        font-size: 3.5rem !important;
        text-align: center;
        margin-top: 2rem !important;
        margin-bottom: 0.5rem !important;
    }

    .subtitle {
        color: var(--text-muted);
        text-align: center;
        margin-bottom: 2rem;
        font-size: 0.9rem;
        font-weight: 600;
        letter-spacing: 0.1em;
    }

    /* Stats Cards */
    .stat-container {
        display: flex;
        gap: 20px;
        margin-bottom: 30px;
        justify-content: center;
    }
    .stat-item {
        flex: 1;
        background: var(--card-bg);
        border-radius: 25px;
        padding: 25px 15px;
        text-align: center;
        box-shadow: 10px 10px 20px rgba(163, 177, 198, 0.2), -10px -10px 20px rgba(255, 255, 255, 0.7);
    }
    .stat-val { font-size: 1.8rem; font-weight: 800; color: #2b62ff; }
    .stat-label { font-size: 0.75rem; color: var(--text-muted); font-weight: 700; margin-top: 5px; }

    /* Category Header */
    .category-header {
        font-weight: 800;
        color: #2b62ff;
        font-size: 1.1rem;
        margin: 30px 0 15px 10px;
        display: flex;
        align-items: center;
    }
    .category-header::before {
        content: "";
        display: inline-block;
        width: 4px;
        height: 1.2rem;
        background: #2b62ff;
        margin-right: 10px;
        border-radius: 2px;
    }

    /* Row Card Styling */
    .row-card {
        background: var(--card-bg);
        border-radius: 20px;
        padding: 18px 25px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 6px 6px 15px rgba(163, 177, 198, 0.15);
        border: 1px solid rgba(255,255,255,0.8);
    }

    .row-id {
        font-weight: 700;
        color: var(--accent-blue);
        font-size: 0.85rem;
        min-width: 40px;
    }

    .row-name {
        font-weight: 500;
        color: var(--text-main);
        flex-grow: 1;
        margin-left: 10px;
        font-size: 1.05rem;
    }

    .row-stock {
        font-weight: 800;
        font-size: 1.3rem;
        margin-right: 25px;
        color: #1d1d1f;
        min-width: 60px;
        text-align: right;
    }

    /* Status Badges */
    .badge {
        padding: 8px 18px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 700;
        min-width: 110px;
        text-align: center;
    }
    .badge-red { background: #ff3b30; color: white; box-shadow: 0 4px 10px rgba(255, 59, 48, 0.2); }
    .badge-yellow { background: #ffcc00; color: #1d1d1f; box-shadow: 0 4px 10px rgba(255, 204, 0, 0.2); }
    .badge-green { background: #34c759; color: white; box-shadow: 0 4px 10px rgba(52, 199, 89, 0.2); }
    .badge-blue { background: #007aff; color: white; box-shadow: 0 4px 10px rgba(0, 122, 255, 0.2); }

    /* Search Bar */
    .stTextInput>div>div>input {
        background: #ffffff !important;
        border: 1px solid #e1e1e1 !important;
        border-radius: 25px !important;
        padding: 15px 25px !important;
        box-shadow: 4px 4px 10px rgba(163, 177, 198, 0.1) !important;
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- OneDrive Data Logic ---
SHARING_URL = "https://1drv.ms/x/c/d2f8d50d153d114e/IQCAAXold6FxQIxpxIaMxT-PAaN1wjYtWRzPRAYo2ALha2s?e=TSbuBT"

def get_direct_link(sharing_url):
    try:
        base64_bytes = base64.b64encode(sharing_url.encode("utf-8"))
        base64_string = base64_bytes.decode("utf-8").replace('=', '').replace('/', '_').replace('+', '-')
        return f"https://api.onedrive.com/v1.0/shares/u!{base64_string}/root/content?t={time.time()}"
    except: return None

def load_data():
    url = get_direct_link(SHARING_URL)
    if not url: return None
    try:
        headers = {'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'}
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            return pd.read_excel(io.BytesIO(r.content), engine='openpyxl')
        return None
    except: return None

def main():
    st.markdown("<h1>คลังสินค้า M2</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>SMART INVENTORY MANAGEMENT SYSTEM</p>", unsafe_allow_html=True)
    
    search = st.text_input("ค้นหาชื่อสินค้า", placeholder="🔍 ค้นหาชื่อสินค้า หรือ รหัสสินค้า...", label_visibility="collapsed")

    @st.fragment(run_every="15s")
    def data_display():
        df_raw, source = load_data()
        last_time = datetime.now().strftime("%H:%M:%S")
        
        if df_raw is not None:
            try:
                categorized_data = []
                current_category = "ทั่วไป"
                total_items_count = 0
                total_qty_sum = 0
                
                for _, row in df_raw.iterrows():
                    seq = row.iloc[0]
                    name = str(row.iloc[3]) if pd.notna(row.iloc[3]) else ""
                    stock = row.iloc[6]
                    
                    if pd.isna(seq) or str(seq).strip() == "":
                        if name and name not in ["nan", "รายการ", "ลำดับ", "หมายเหตุ"]:
                            current_category = name
                        continue
                    
                    try:
                        seq_num = int(pd.to_numeric(seq))
                        qty = float(pd.to_numeric(stock, errors='coerce') or 0)
                        
                        item = {'category': current_category, 'seq': seq_num, 'name': name, 'stock': qty}
                        total_items_count += 1
                        total_qty_sum += qty
                        
                        if search:
                            if search.lower() in name.lower():
                                categorized_data.append(item)
                        else:
                            categorized_data.append(item)
                    except: continue

                # Header Stats
                st.markdown(f"""
                    <div class="stat-container">
                        <div class="stat-item"><div class="stat-val">{total_items_count}</div><div class="stat-label">รายการ</div></div>
                        <div class="stat-item"><div class="stat-val">{int(total_qty_sum):,}</div><div class="stat-label">ยอดรวมคลัง</div></div>
                        <div class="stat-item"><div class="stat-val">{last_time}</div><div class="stat-label">อัปเดตล่าสุด</div></div>
                    </div>
                """, unsafe_allow_html=True)

                if not categorized_data:
                    st.info("ไม่พบรายการที่ตรงกับคำค้นหา")
                else:
                    last_cat = None
                    for item in categorized_data:
                        if item['category'] != last_cat:
                            st.markdown(f"<div class='category-header'>หมวด: {item['category']}</div>", unsafe_allow_html=True)
                            last_cat = item['category']
                        
                        # Updated Logic: 0 = หมด (แดง), 1-50 = ใกล้หมด (เหลือง), >500 = เยอะ (ฟ้า), else = ปกติ (เขียว)
                        if item['stock'] <= 0:
                            b_cls, b_txt = "badge-red", "สินค้าหมด"
                        elif item['stock'] <= 50:
                            b_cls, b_txt = "badge-yellow", "สินค้าใกล้หมด"
                        elif item['stock'] > 500:
                            b_cls, b_txt = "badge-blue", "สต็อกเยอะพิเศษ"
                        else:
                            b_cls, b_txt = "badge-green", "ปกติ"

                        st.markdown(f"""
                            <div class="row-card">
                                <div style="display:flex; align-items:center; flex-grow:1;">
                                    <span class="row-id">{item['seq']}</span>
                                    <span class="row-name">{item['name']}</span>
                                </div>
                                <div style="display:flex; align-items:center;">
                                    <span class="row-stock">{int(item['stock']):,}</span>
                                    <span class="badge {b_cls}">{b_txt}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("❌ กำลังพยายามซิงค์ข้อมูลจาก OneDrive...")

    data_display()

if __name__ == "__main__":
    main()
