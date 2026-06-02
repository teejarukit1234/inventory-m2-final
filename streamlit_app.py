import streamlit as st
import pandas as pd
import requests
import io
import base64
import time
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="M2 ระบบคลังสินค้า", layout="centered")

# --- UI Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; background-color: #f3f4f7; }
    .stApp { max-width: 800px; margin: 0 auto; }
    h1 { text-align: center; color: #2d3436; font-weight: 800; margin-top: 1rem; }
    .row-card { background: white; border-radius: 15px; padding: 15px 20px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.7); }
    .badge { padding: 5px 12px; border-radius: 10px; font-size: 0.7rem; font-weight: 600; min-width: 85px; text-align: center; }
    .badge-red { background: #ff3b30; color: white; }
    .badge-green { background: #34c759; color: white; }
    .badge-yellow { background: #ffcc00; color: black; }
    .stTextInput>div>div>input { border-radius: 15px !important; }
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

# --- Main App Structure ---
def main():
    st.markdown("<h1>คลังสินค้า M2</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888; font-size:0.8rem; margin-bottom:1rem;'>ระบบจะอัปเดตตัวเลขเองอัตโนมัติ โดยไม่ต้องรีเฟรชหน้าจอ</p>", unsafe_allow_html=True)
    
    # ช่องค้นหา (อยู่นอก fragment เพื่อไม่ให้รีเฟรชรบกวนการพิมพ์)
    search = st.text_input("ค้นหาสินค้า", placeholder="🔍 พิมพ์ชื่อสินค้าเพื่อค้นหา...", label_visibility="collapsed")

    # ส่วนแสดงผล (ใช้ fragment เพื่ออัปเดตเฉพาะตัวเลขสต็อกโดยไม่เลื่อนหน้าจอขึ้นบน)
    @st.fragment(run_every="15s")
    def data_display():
        df = load_data()
        last_time = datetime.now().strftime("%H:%M:%S")
        
        if df is not None:
            try:
                p_df = pd.DataFrame({'seq': df.iloc[:, 0], 'name': df.iloc[:, 3], 'stock': df.iloc[:, 6]})
                p_df['seq_n'] = pd.to_numeric(p_df['seq'], errors='coerce')
                p_df = p_df.dropna(subset=['seq_n', 'name'])

                if search:
                    p_df = p_df[p_df['name'].str.contains(search, case=False, na=False)]

                st.caption(f"ดึงข้อมูลล่าสุดเมื่อ: {last_time} ✅")

                for _, row in p_df.iterrows():
                    qty = pd.to_numeric(row['stock'], errors='coerce') or 0
                    b_cls, b_txt = ("badge-red", "ใกล้หมด") if qty <= 10 else (("badge-yellow", "เยอะ") if qty > 500 else ("badge-green", "ปกติ"))
                    st.markdown(f"""
                        <div class="row-card">
                            <div><b>{int(row['seq_n'])}</b>. {row['name']}</div>
                            <div style="display: flex; align-items: center;">
                                <span style="margin-right:15px; font-weight:bold; color:#2b62ff; font-size:1.1rem;">{int(qty):,}</span>
                                <span class="badge {b_cls}">{b_txt}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            except: st.error("โครงสร้างไฟล์เปลี่ยน หรือกำลังซิงค์ไฟล์...")
        else:
            st.warning("กำลังซิงค์ข้อมูลใหม่จาก OneDrive...")

    data_display()

if __name__ == "__main__":
    main()
