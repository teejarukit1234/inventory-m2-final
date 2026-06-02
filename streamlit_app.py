import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="M2 ระบบคลังสินค้า", layout="centered")

# --- High-Fidelity Soft UI CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    :root {
        --bg: #f3f4f7; 
        --card-bg: #f3f4f7; 
        --white: #ffffff;
        --shadow-dark: rgba(163, 177, 198, 0.5);
        --shadow-light: rgba(255, 255, 255, 0.8);
        --accent: linear-gradient(135deg, #4b91ff 0%, #2b62ff 100%);
        --text-main: #2d3436; 
        --text-muted: #86868b;
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
        color: var(--text-main); 
        font-size: 3rem !important; 
        text-align: center; 
        margin-top: 2rem !important; 
    }
    
    .subtitle { 
        color: var(--text-muted); 
        text-align: center; 
        margin-bottom: 2rem; 
        font-size: 0.9rem; 
        font-weight: 500; 
    }
    
    .row-card { 
        background: var(--white); 
        border-radius: 20px; 
        padding: 18px 25px; 
        margin-bottom: 12px; 
        display: flex; 
        align-items: center; 
        justify-content: space-between; 
        box-shadow: 4px 4px 10px rgba(163, 177, 198, 0.15); 
        border: 1px solid rgba(255,255,255,0.8); 
    }
    
    .row-id { font-weight: 700; color: #4b91ff; font-size: 0.8rem; min-width: 40px; }
    .row-name { font-weight: 500; color: var(--text-main); flex-grow: 1; margin-left: 10px; font-size: 1rem; }
    .row-stock { font-weight: 700; font-size: 1.2rem; margin-right: 20px; color: #1d1d1f; min-width: 50px; text-align: right; }
    
    .badge { padding: 6px 15px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; min-width: 100px; text-align: center; }
    .badge-red { background: #ff3b30; color: white; }
    .badge-green { background: #34c759; color: white; }
    .badge-yellow { background: #ffcc00; color: #8a6d00; }
    
    .stat-container { display: flex; gap: 15px; margin-bottom: 25px; }
    .stat-item { flex: 1; background: var(--white); border-radius: 20px; padding: 15px; text-align: center; box-shadow: 5px 5px 10px var(--shadow-dark), -5px -5px 10px var(--shadow-light); }
    .stat-val { font-size: 1.5rem; font-weight: 700; color: #2b62ff; }
    .stat-label { font-size: 0.7rem; color: var(--text-muted); font-weight: 600; }
    
    .stTextInput>div>div>input { 
        background: var(--bg) !important; 
        border: none !important; 
        border-radius: 15px !important; 
        box-shadow: inset 3px 3px 6px var(--shadow-dark), inset -3px -3px 6px var(--shadow-light) !important; 
        padding: 12px 20px !important; 
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- OneDrive Direct Download Link ---
DIRECT_DOWNLOAD_URL = "https://onedrive.live.com/download?resid=D2F8D50D153D114E%21142512&authkey=!AAL-L-F6Z3uhcUC"

def download_excel():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(DIRECT_DOWNLOAD_URL, headers=headers, timeout=30)
        if response.status_code == 200:
            return pd.read_excel(io.BytesIO(response.content), engine='openpyxl')
        return None
    except Exception:
        return None

def main():
    st.markdown("<h1>คลังสินค้า M2</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>REAL-TIME CLOUD INVENTORY</p>", unsafe_allow_html=True)

    # แก้ไขปัญหา Accessibility Warning เรื่อง Empty Label
    search_query = st.text_input("ค้นหาชื่อสินค้าที่นี่", placeholder="🔍 ค้นชื่อสินค้าที่นี่...", key="search_input", label_visibility="collapsed")

    @st.fragment(run_every="60s")
    def render_content():
        df_wh = download_excel()
        last_update = datetime.now().strftime("%H:%M:%S")

        if df_wh is not None:
            try:
                # เลือกคอลัมน์ ลำดับ(0), ชื่อ(3), สต็อก(6)
                p_df = pd.DataFrame({
                    'seq': df_wh.iloc[:, 0],
                    'name': df_wh.iloc[:, 3],
                    'stock': df_wh.iloc[:, 6]
                })
                # กรองเอาเฉพาะรายการที่มีเลขลำดับ
                p_df['seq_n'] = pd.to_numeric(p_df['seq'], errors='coerce')
                p_df = p_df.dropna(subset=['seq_n']).dropna(subset=['name'])
                
                total_items = len(p_df)
                total_qty = int(pd.to_numeric(p_df['stock'], errors='coerce').sum() or 0)

                st.markdown(f"""
                    <div class="stat-container">
                        <div class="stat-item"><div class="stat-val">{total_items}</div><div class="stat-label">รายการ</div></div>
                        <div class="stat-item"><div class="stat-val">{total_qty:,}</div><div class="stat-label">ยอดรวมคลัง</div></div>
                        <div class="stat-item"><div class="stat-val">{last_update}</div><div class="stat-label">อัปเดตล่าสุด</div></div>
                    </div>
                """, unsafe_allow_html=True)

                if search_query:
                    mask = p_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)
                    p_df = p_df[mask]

                st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
                for _, row in p_df.iterrows():
                    try: stock_val = float(row['stock'])
                    except: stock_val = 0
                    
                    if stock_val <= 10:
                        badge_class, status_txt = "badge-red", "สินค้าใกล้หมด"
                    elif stock_val > 500:
                        badge_class, status_txt = "badge-yellow", "สต็อกเยอะพิเศษ"
                    else:
                        badge_class, status_txt = "badge-green", "ปกติ"
                    
                    st.markdown(f"""
                        <div class="row-card">
                            <div style="display: flex; align-items: center; flex-grow: 1;">
                                <span class="row-id">{int(row['seq_n'])}</span>
                                <span class="row-name">{row['name']}</span>
                            </div>
                            <div style="display: flex; align-items: center;">
                                <span class="row-stock">{int(stock_val):,}</span>
                                <span class="badge {badge_class}">{status_txt}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการประมวลผล: {e}")
        else:
            st.error("❌ ไม่สามารถดึงข้อมูลจาก OneDrive ได้ โปรดเช็คการเชื่อมต่อ")

    render_content()

if __name__ == "__main__":
    main()
