import streamlit as st
import pandas as pd
import requests
import io
import base64
import time
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="M2 Smart Inventory", layout="centered")

# --- Premium Glassmorphism UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg-gradient: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        --glass-bg: rgba(255, 255, 255, 0.75);
        --glass-border: rgba(255, 255, 255, 0.4);
        --text-main: #1d1d1f;
        --accent-blue: #007aff;
    }

    html, body, [class*="css"] {
        font-family: 'Sarabun', 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: var(--bg-gradient);
        background-attachment: fixed;
    }

    h1 {
        font-weight: 800;
        color: var(--text-main);
        font-size: 3.5rem !important;
        text-align: center;
        margin-top: 1.5rem !important;
        letter-spacing: -0.02em;
    }

    .subtitle {
        color: #515154;
        text-align: center;
        margin-bottom: 2.5rem;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: 0.15em;
    }

    /* Premium Stats Cards */
    .stat-container {
        display: flex;
        gap: 15px;
        margin-bottom: 30px;
    }
    .stat-item {
        flex: 1;
        background: var(--glass-bg);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid var(--glass-border);
        border-radius: 28px;
        padding: 25px 10px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        transition: all 0.4s ease;
    }
    .stat-val { font-size: 2rem; font-weight: 800; color: var(--accent-blue); display: block; }
    .stat-label { font-size: 0.8rem; color: #6e6e73; font-weight: 700; margin-top: 4px; }

    /* Category Header */
    .category-header {
        font-weight: 800;
        color: var(--text-main);
        font-size: 1.3rem;
        margin: 45px 0 15px 10px;
        display: flex;
        align-items: center;
    }
    .category-header::before {
        content: "📂";
        margin-right: 12px;
        font-size: 1.4rem;
    }

    /* Premium Product Card */
    .row-card {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 22px 28px;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }

    .row-card:hover {
        background: rgba(255, 255, 255, 0.95);
        transform: scale(1.02) translateY(-3px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.08);
    }

    .row-name {
        font-weight: 600;
        color: var(--text-main);
        flex-grow: 1;
        margin-left: 15px;
        font-size: 1.1rem;
    }
    
    .row-id {
        background: rgba(0, 122, 255, 0.1);
        color: var(--accent-blue);
        padding: 4px 12px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 0.85rem;
    }

    .row-stock {
        font-weight: 800;
        font-size: 1.5rem;
        margin-right: 25px;
        color: #1d1d1f;
        min-width: 80px;
        text-align: right;
    }

    /* Premium Status Badges */
    .badge {
        padding: 10px 18px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 700;
        min-width: 120px;
        text-align: center;
    }
    .badge-red { background: linear-gradient(135deg, #ff5e62, #ff9966); color: white; }
    .badge-yellow { background: linear-gradient(135deg, #f6d365, #fda085); color: #1d1d1f; }
    .badge-green { background: linear-gradient(135deg, #a8ff78, #78ffd6); color: #155724; }
    .badge-blue { background: linear-gradient(135deg, #2193b0, #6dd5ed); color: white; }

    /* Progress Bar */
    .progress-bg {
        width: 100%;
        height: 8px;
        background: rgba(0,0,0,0.05);
        border-radius: 10px;
        margin-top: 12px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 1.5s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Search Bar */
    .stTextInput>div>div>input {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 35px !important;
        padding: 18px 30px !important;
        font-size: 1.05rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03) !important;
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ลิงก์ OneDrive
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
        r = requests.get(url, headers=headers, timeout=25)
        if r.status_code == 200:
            return pd.read_excel(io.BytesIO(r.content), engine='openpyxl')
        return None
    except: return None

def main():
    st.markdown("<h1>คลังสินค้า M2</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>SMART CLOUD INVENTORY</p>", unsafe_allow_html=True)
    
    search = st.text_input("ค้นหา", placeholder="🔍 พิมพ์ชื่อสินค้าที่ต้องการค้นหา...", label_visibility="collapsed")

    @st.fragment(run_every="15s")
    def data_display():
        df_raw = load_data()
        last_time = datetime.now().strftime("%H:%M:%S")
        
        if df_raw is not None:
            try:
                categorized_data = []
                current_category = "ทั่วไป"
                total_items = 0
                total_stock = 0
                
                for _, row in df_raw.iterrows():
                    seq = row.iloc[0]
                    name = str(row.iloc[3]) if pd.notna(row.iloc[3]) else ""
                    stock = row.iloc[6]
                    if pd.isna(seq) or str(seq).strip() == "":
                        if name and name not in ["nan", "รายการ", "ลำดับ"]:
                            current_category = name
                        continue
                    try:
                        qty = float(pd.to_numeric(stock, errors='coerce') or 0)
                        item = {'cat': current_category, 'seq': int(pd.to_numeric(seq)), 'name': name, 'stock': qty}
                        total_items += 1
                        total_stock += qty
                        if not search or search.lower() in name.lower():
                            categorized_data.append(item)
                    except: continue

                st.markdown(f"""
                    <div class="stat-container">
                        <div class="stat-item"><span class="stat-val">{total_items}</span><span class="stat-label">รายการทั้งหมด</span></div>
                        <div class="stat-item"><span class="stat-val">{int(total_stock):,}</span><span class="stat-label">จำนวนรวมคลัง</span></div>
                        <div class="stat-item"><span class="stat-val">{last_time}</span><span class="stat-label">อัปเดตล่าสุด</span></div>
                    </div>
                """, unsafe_allow_html=True)

                if not categorized_data:
                    st.info("ไม่พบรายการที่ตรงกับคำค้นหา")
                else:
                    last_cat = None
                    for item in categorized_data:
                        if item['cat'] != last_cat:
                            st.markdown(f"<div class='category-header'>หมวด: {item['cat']}</div>", unsafe_allow_html=True)
                            last_cat = item['cat']
                        if item['stock'] <= 0:
                            b_cls, b_txt, p_color = "badge-red", "สินค้าหมด", "#ff5e62"
                        elif item['stock'] <= 50:
                            b_cls, b_txt, p_color = "badge-yellow", "สินค้าใกล้หมด", "#f6d365"
                        elif item['stock'] > 300:
                            b_cls, b_txt, p_color = "badge-blue", "สต็อกเยอะพิเศษ", "#2193b0"
                        else:
                            b_cls, b_txt, p_color = "badge-green", "ปกติ", "#a8ff78"
                        p_width = min((item['stock'] / 300) * 100, 100) if item['stock'] > 0 else 0
                        st.markdown(f"""
                            <div class="row-card">
                                <div style="display:flex; flex-direction:column; flex-grow:1;">
                                    <div style="display:flex; align-items:center;">
                                        <span class="row-id">{item['seq']}</span>
                                        <span class="row-name">{item['name']}</span>
                                    </div>
                                    <div class="progress-bg"><div class="progress-fill" style="width:{p_width}%; background:{p_color};"></div></div>
                                </div>
                                <div style="display:flex; align-items:center;">
                                    <span class="row-stock">{int(item['stock']):,}</span>
                                    <span class="badge {b_cls}">{b_txt}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as e: st.error(f"Error: {e}")
        else: st.warning("🔄 กำลังเชื่อมต่อข้อมูล...")

    data_display()

if __name__ == "__main__":
    main()
