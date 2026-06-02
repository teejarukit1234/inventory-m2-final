import streamlit as st
import pandas as pd
import requests
import io
import base64
import time
import os
import shutil
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="M2 Smart Inventory", layout="centered")

# --- High-Fidelity Responsive Glassmorphism UI CSS ---
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

    /* Header Styling */
    h1 {
        font-weight: 800;
        color: var(--text-main);
        font-size: 3.5rem !important;
        text-align: center;
        margin-top: 1rem !important;
        letter-spacing: -0.02em;
    }
    .subtitle {
        color: #515154;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 1rem;
        font-weight: 600;
    }

    /* Stats Section */
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
        border-radius: 24px;
        padding: 20px 10px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }
    .stat-val { font-size: 2rem; font-weight: 800; color: var(--accent-blue); display: block; }
    .stat-label { font-size: 0.75rem; color: #6e6e73; font-weight: 700; margin-top: 4px; }

    /* Category Header */
    .category-header {
        font-weight: 800;
        color: var(--text-main);
        font-size: 1.2rem;
        margin: 35px 0 15px 5px;
        display: flex;
        align-items: center;
    }
    .category-header::before { content: "📂"; margin-right: 10px; }

    /* Product Card */
    .row-card {
        background: var(--glass-bg);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 18px 22px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        transition: transform 0.2s ease;
    }
    .row-card:hover { transform: scale(1.01); background: rgba(255, 255, 255, 0.95); }

    .row-name { font-weight: 600; color: var(--text-main); flex-grow: 1; margin-left: 12px; font-size: 1.05rem; }
    .row-id { background: rgba(0, 122, 255, 0.1); color: var(--accent-blue); padding: 3px 10px; border-radius: 8px; font-weight: 800; font-size: 0.8rem; }
    .row-stock { font-weight: 800; font-size: 1.4rem; margin-right: 18px; color: #1d1d1f; min-width: 60px; text-align: right; }

    /* Badges */
    .badge { padding: 8px 15px; border-radius: 14px; font-size: 0.8rem; font-weight: 700; min-width: 110px; text-align: center; }
    .badge-red { background: linear-gradient(135deg, #ff5e62, #ff9966); color: white; }
    .badge-yellow { background: linear-gradient(135deg, #f6d365, #fda085); color: #1d1d1f; }
    .badge-green { background: linear-gradient(135deg, #a8ff78, #78ffd6); color: #155724; }
    .badge-blue { background: linear-gradient(135deg, #2193b0, #6dd5ed); color: white; }

    /* Progress Bar */
    .progress-bg { width: 100%; height: 6px; background: rgba(0,0,0,0.05); border-radius: 10px; margin-top: 10px; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 10px; transition: width 1.5s ease; }

    /* Search Bar */
    .stTextInput>div>div>input { border-radius: 30px !important; padding: 15px 25px !important; }

    /* MOBILE RESPONSIVE TWEAKS */
    @media (max-width: 640px) {
        h1 { font-size: 2.2rem !important; }
        .stat-container { flex-direction: column; gap: 10px; }
        .stat-item { padding: 15px; }
        .row-card { padding: 15px; flex-wrap: wrap; }
        .row-name { width: 100%; margin-left: 0; margin-top: 5px; font-size: 1rem; order: 1; }
        .row-id { order: 0; }
        .row-stock { order: 2; margin-right: 10px; font-size: 1.2rem; flex-grow: 1; text-align: left; margin-top: 10px; }
        .badge { order: 3; margin-top: 10px; min-width: 90px; padding: 6px 10px; font-size: 0.75rem; }
        .progress-bg { order: 4; margin-top: 15px; }
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ลิงก์ OneDrive (สำหรับการนำไปอัปโหลดขึ้น Cloud)
SHARING_URL = "https://1drv.ms/x/c/d2f8d50d153d114e/IQCAAXold6FxQIxpxIaMxT-PAaN1wjYtWRzPRAYo2ALha2s?e=TSbuBT"

def get_direct_link(sharing_url):
    try:
        base64_bytes = base64.b64encode(sharing_url.encode("utf-8"))
        base64_string = base64_bytes.decode("utf-8").replace('=', '').replace('/', '_').replace('+', '-')
        return f"https://api.onedrive.com/v1.0/shares/u!{base64_string}/root/content?t={time.time()}"
    except: return None

def load_data():
    # ตรวจสอบว่ารันบนเครื่อง Local หรือไม่
    LOCAL_PATH = r"C:\Users\Angelo\OneDrive\ทดสอบระบบ\ทดสอบฟอร์มคลังสินค้า\2.คลังใหญ่ (จัดหมวด).xlsx"
    if os.path.exists(LOCAL_PATH):
        try:
            temp_file = "temp_premium_responsive.xlsx"
            shutil.copy2(LOCAL_PATH, temp_file)
            df = pd.read_excel(temp_file)
            if os.path.exists(temp_file): os.remove(temp_file)
            return df
        except: pass
    
    # ดึงข้อมูลจาก Cloud (OneDrive)
    url = get_direct_link(SHARING_URL)
    if url:
        try:
            headers = {'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'}
            r = requests.get(url, headers=headers, timeout=25)
            return pd.read_excel(io.BytesIO(r.content), engine='openpyxl')
        except: return None
    return None

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

                # Stats Header
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
                                <div class="row-id">#{item['seq']}</div>
                                <div class="row-name">{item['name']}</div>
                                <div style="display:flex; align-items:center;">
                                    <span class="row-stock">{int(item['stock']):,}</span>
                                    <span class="badge {b_cls}">{b_txt}</span>
                                </div>
                                <div class="progress-bg"><div class="progress-fill" style="width:{p_width}%; background:{p_color};"></div></div>
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as e: st.error(f"Render Error: {e}")
        else: st.warning("🔄 กำลังเชื่อมต่อข้อมูล...")

    data_display()

if __name__ == "__main__":
    main()
