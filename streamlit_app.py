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
    .stApp { max-width: 850px; margin: 0 auto; }
    h1 { text-align: center; color: #2d3436; font-weight: 800; margin-bottom: 0.5rem; }
    .subtitle { text-align: center; color: #86868b; font-size: 0.9rem; margin-bottom: 2rem; }
    
    /* Category Header Styling */
    .category-header {
        background: linear-gradient(90deg, #4b91ff 0%, #2b62ff 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 12px;
        margin: 25px 0 15px 0;
        font-weight: 700;
        font-size: 1.1rem;
        box-shadow: 0 4px 10px rgba(43, 98, 255, 0.2);
    }

    /* Product Card Styling */
    .row-card { 
        background: white; 
        border-radius: 15px; 
        padding: 15px 22px; 
        margin-bottom: 10px; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.04); 
        border: 1px solid rgba(255,255,255,0.8);
        transition: transform 0.2s;
    }
    .row-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    
    .badge { padding: 5px 12px; border-radius: 10px; font-size: 0.75rem; font-weight: 600; min-width: 90px; text-align: center; }
    .badge-red { background: #ff3b30; color: white; }
    .badge-green { background: #34c759; color: white; }
    .badge-yellow { background: #ffcc00; color: black; }
    
    .stTextInput>div>div>input { border-radius: 15px !important; padding: 12px 20px !important; }
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
    st.markdown("<p class='subtitle'>ระบบจัดการสต็อก แยกตามหมวดหมู่สินค้า</p>", unsafe_allow_html=True)
    
    # ช่องค้นหา (อยู่นอก fragment เพื่อความลื่นไหล)
    search = st.text_input("ค้นหาชื่อสินค้า", placeholder="🔍 พิมพ์ชื่อสินค้าที่ต้องการค้นหา...", label_visibility="collapsed")

    @st.fragment(run_every="20s")
    def data_display():
        df_raw = load_data()
        last_time = datetime.now().strftime("%H:%M:%S")
        
        if df_raw is not None:
            try:
                # เริ่มต้นประมวลผลแยกหมวดหมู่
                categorized_data = []
                current_category = "ทั่วไป"
                
                # วนลูปเช็คทีละแถว (ข้ามหัวตารางแถวแรกๆ)
                for index, row in df_raw.iterrows():
                    seq = row.iloc[0]
                    name = str(row.iloc[3]) if pd.notna(row.iloc[3]) else ""
                    stock = row.iloc[6]
                    
                    # ถ้าช่องลำดับ (Col A) ว่าง แต่ช่องชื่อ (Col D) มีข้อความ -> นี่คือชื่อหมวด
                    if pd.isna(seq) or str(seq).strip() == "":
                        if name and name != "nan" and name != "รายการ" and name != "ลำดับ":
                            current_category = name
                        continue
                    
                    # ถ้าช่องลำดับมีตัวเลข -> นี่คือสินค้า
                    try:
                        seq_num = int(pd.to_numeric(seq))
                        qty = pd.to_numeric(stock, errors='coerce') or 0
                        
                        # เก็บข้อมูลลง list
                        categorized_data.append({
                            'category': current_category,
                            'seq': seq_num,
                            'name': name,
                            'stock': qty
                        })
                    except:
                        continue # ข้ามแถวที่แปลงเลขลำดับไม่ได้

                # กรองตามคำค้นหา
                if search:
                    categorized_data = [item for item in categorized_data if search.lower() in item['name'].lower()]

                st.caption(f"อัปเดตสต็อกล่าสุดเมื่อ: {last_time} ✅ (รีเฟรชทุก 20 วินาที)")

                # แสดงผลแยกตามหมวดหมู่
                if not categorized_data:
                    st.info("ไม่พบรายการที่ตรงกับคำค้นหา")
                else:
                    last_cat = None
                    for item in categorized_data:
                        # ถ้าเป็นหมวดใหม่ ให้แสดงหัวข้อหมวด
                        if item['category'] != last_cat:
                            st.markdown(f"<div class='category-header'>📂 หมวด: {item['category']}</div>", unsafe_allow_html=True)
                            last_cat = item['category']
                        
                        # กำหนดสถานะสี
                        if item['stock'] <= 10:
                            b_cls, b_txt = "badge-red", "ใกล้หมด"
                        elif item['stock'] > 500:
                            b_cls, b_txt = "badge-yellow", "เยอะพิเศษ"
                        else:
                            b_cls, b_txt = "badge-green", "ปกติ"

                        st.markdown(f"""
                            <div class="row-card">
                                <div><b>{item['seq']}</b>. {item['name']}</div>
                                <div style="display: flex; align-items: center;">
                                    <span style="margin-right:15px; font-weight:700; color:#2b62ff; font-size:1.1rem;">{int(item['stock']):,}</span>
                                    <span class="badge {b_cls}">{b_txt}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการจัดหมวดหมู่: {e}")
        else:
            st.warning("🔄 กำลังซิงค์ข้อมูลล่าสุดจาก OneDrive...")

    data_display()

if __name__ == "__main__":
    main()
