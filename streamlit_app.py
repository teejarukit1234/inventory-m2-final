import streamlit as st
import pandas as pd
import requests
import io
import base64
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
    .subtitle { text-align: center; color: #86868b; font-size: 0.9rem; margin-bottom: 2rem; }
    .row-card { background: white; border-radius: 15px; padding: 15px 20px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); border: 1px solid rgba(255,255,255,0.7); }
    .badge { padding: 5px 12px; border-radius: 10px; font-size: 0.75rem; font-weight: 600; min-width: 90px; text-align: center; }
    .badge-red { background: #ff3b30; color: white; }
    .badge-green { background: #34c759; color: white; }
    .badge-yellow { background: #ffcc00; color: black; }
    .stTextInput>div>div>input { border-radius: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- OneDrive Direct Download Logic ---
# ลิงก์ที่แปลงจาก iframe embed ของคุณครับ
# Resid: D2F8D50D153D114E!142512
DIRECT_URL = "https://onedrive.live.com/download?cid=d2f8d50d153d114e&resid=D2F8D50D153D114E!142512&authkey=!AAL-L-F6Z3uhcUC"

def load_data():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(DIRECT_URL, headers=headers, timeout=30)
        if response.status_code == 200:
            return pd.read_excel(io.BytesIO(response.content), engine='openpyxl')
        return None
    except Exception as e:
        return None

def main():
    st.markdown("<h1>คลังสินค้า M2</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>ระบบจัดการสต็อกอัจฉริยะ (Sync OneDrive)</p>", unsafe_allow_html=True)
    
    search = st.text_input("ค้นหาชื่อสินค้า", placeholder="🔍 ค้นชื่อสินค้าที่นี่...", key="search_bar", label_visibility="collapsed")

    @st.fragment(run_every="60s")
    def render_content():
        df = load_data()
        last_update = datetime.now().strftime("%H:%M:%S")

        if df is not None:
            try:
                # เลือกคอลัมน์ A=0 (ลำดับ), D=3 (ชื่อ), G=6 (สต็อก)
                p_df = pd.DataFrame({
                    'seq': df.iloc[:, 0],
                    'name': df.iloc[:, 3],
                    'stock': df.iloc[:, 6]
                })
                
                # กรองเฉพาะรายการสินค้าจริงที่มีเลขลำดับ
                p_df['seq_n'] = pd.to_numeric(p_df['seq'], errors='coerce')
                p_df = p_df.dropna(subset=['seq_n', 'name'])

                if search:
                    p_df = p_df[p_df['name'].str.contains(search, case=False, na=False)]

                st.caption(f"อัปเดตล่าสุด: {last_update} (เชื่อมต่อสำเร็จ ✅)")

                st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
                for _, row in p_df.iterrows():
                    try: qty = float(row['stock'])
                    except: qty = 0
                    
                    if qty <= 10:
                        b_cls, b_txt = "badge-red", "สินค้าใกล้หมด"
                    elif qty > 500:
                        b_cls, b_txt = "badge-yellow", "เยอะพิเศษ"
                    else:
                        b_cls, b_txt = "badge-green", "ปกติ"
                    
                    st.markdown(f"""
                        <div class="row-card">
                            <div><b>{int(row['seq_n'])}</b>. {row['name']}</div>
                            <div style="display: flex; align-items: center;">
                                <span style="margin-right:15px; font-weight:bold; font-size:1.1rem;">{int(qty):,}</span>
                                <span class="badge {b_cls}">{b_txt}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการแสดงผลข้อมูล: {e}")
        else:
            st.error("❌ ไม่สามารถดึงข้อมูลได้ โปรดตรวจสอบว่าไฟล์ใน OneDrive ยังแชร์อยู่หรือไม่")

    render_content()

if __name__ == "__main__":
    main()
