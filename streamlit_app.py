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
    .badge { padding: 5px 12px; border-radius: 10px; font-size: 0.7rem; font-weight: 600; min-width: 80px; text-align: center; }
    .badge-red { background: #ff3b30; color: white; }
    .badge-green { background: #34c759; color: white; }
    .badge-yellow { background: #ffcc00; color: black; }
    .stTextInput>div>div>input { border-radius: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- OneDrive Link Conversion Logic ---
def get_direct_link(sharing_url):
    try:
        base64_bytes = base64.b64encode(sharing_url.encode("utf-8"))
        base64_string = base64_bytes.decode("utf-8").replace('=', '').replace('/', '_').replace('+', '-')
        return f"https://api.onedrive.com/v1.0/shares/u!{base64_string}/root/content"
    except:
        return None

# ลิงก์ OneDrive ล่าสุดที่คุณส่งมา
SHARING_URL = "https://1drv.ms/x/c/d2f8d50d153d114e/IQSAAXold6FxQIxpxIaMxT-PAdT1pxyXFJ93CbYZ5YUghms"

def load_data():
    direct_url = get_direct_link(SHARING_URL)
    if not direct_url:
        return None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(direct_url, headers=headers, timeout=25)
        if response.status_code == 200:
            return pd.read_excel(io.BytesIO(response.content), engine='openpyxl')
        return None
    except Exception as e:
        return None

def main():
    st.markdown("<h1>คลังสินค้า M2</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>REAL-TIME CLOUD INVENTORY</p>", unsafe_allow_html=True)
    
    search = st.text_input("ค้นหาสินค้า", placeholder="🔍 พิมพ์ชื่อสินค้าที่นี่...", key="search_bar", label_visibility="collapsed")

    @st.fragment(run_every="60s")
    def render_content():
        df = load_data()
        if df is not None:
            try:
                # เลือกคอลัมน์ ลำดับ(0), ชื่อ(3), สต็อก(6)
                p_df = pd.DataFrame({
                    'seq': df.iloc[:, 0],
                    'name': df.iloc[:, 3],
                    'stock': df.iloc[:, 6]
                })
                
                # กรองเฉพาะรายการที่มีเลขลำดับ
                p_df['seq_n'] = pd.to_numeric(p_df['seq'], errors='coerce')
                p_df = p_df.dropna(subset=['seq_n', 'name'])

                if search:
                    p_df = p_df[p_df['name'].str.contains(search, case=False, na=False)]

                last_update = datetime.now().strftime("%H:%M:%S")
                st.caption(f"อัปเดตล่าสุด: {last_update} (เชื่อมต่อสำเร็จ ✅)")

                st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
                for _, row in p_df.iterrows():
                    try: qty = float(row['stock'])
                    except: qty = 0
                    
                    if qty <= 10:
                        b_cls, b_txt = "badge-red", "ใกล้หมด"
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
                st.error(f"โครงสร้างไฟล์ Excel ไม่ถูกต้อง: {e}")
        else:
            st.error("❌ ไม่สามารถดึงข้อมูลได้ โปรดเช็คสิทธิ์การแชร์ไฟล์ใน OneDrive")

    render_content()

if __name__ == "__main__":
    main()
