import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- 基礎設置 (必須在最開頭) ---
st.set_page_config(page_title="Summer Body 2026 - 女神計畫", page_icon="🧚‍♀️", layout="wide")

# ---  CSS 背景魔法函數 ---
def add_bg_from_url():
    # 這裡替換成你想要的背景圖片連結
    # 注意：建議使用橫向、高解析度的照片
    # 範例連結是 Unsplash 上隨機抓取的女性健身照片
    bg_image_url = "https://images.unsplash.com/photo-1518611012118-696072aa579a?q=80&w=1920&auto=format&fit=crop"

    st.markdown(
        f"""
         <style>
         /* 設定整體 App 的背景圖 */
         .stApp {{
             background-image: url("{bg_image_url}");
             background-attachment: fixed;
             background-size: cover;
             background-position: center center;
         }}
         
         /* 為了讓文字看清楚，把主要內容區塊加上半透明白色底 */
         [data-testid="stMainBlockContainer"] {{
             background-color: rgba(255, 255, 255, 0.85); /* 0.85 是透明度，越小越透明 */
             padding: 2rem;
             border-radius: 15px;
             box-shadow: 0 4px 6px rgba(0,0,0,0.1);
         }}

         /* 調整一下標題顏色，讓它更顯眼 */
         h1 {{
            color: #0077be;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
         }}
         </style>
         """,
        unsafe_allow_html=True
    )

# --- 啟動背景 ---
add_bg_from_url()

# --- 數據模擬 ---
DATA_FILE = "user_data.csv"

def save_data(username, bmi, tdee):
    new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), username, bmi, tdee]], 
                            columns=["日期", "用戶", "BMI", "TDEE"])
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data
    df.to_csv(DATA_FILE, index=False)

# --- 登入系統 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌊 Summer Body 登入")
    st.markdown("### 開啟你的女神塑身之旅 💪")
    user = st.text_input("用戶名")
    pw = st.text_input("密碼", type="password")
    if st.button("進入私人中心"):
        if user and pw:
            st.session_state.logged_in = True
            st.session_state.username = user
            st.rerun()
else:
    # --- 側邊欄 (保持簡潔，不加背景以免太亂) ---
    st.sidebar.title(f"👤 {st.session_state.username}")
    if st.sidebar.button("登出"):
        st.session_state.logged_in = False
        st.rerun()

    # --- 主頁面標題 ---
    st.title(f"🧚‍♀️ {st.session_state.username} 的女神強化日誌")
    
    # 建立分頁
    tab1, tab2, tab3 = st.tabs(["📊 體態追蹤", "🥗 飲食建議", "📅 夏季作息"])

    with tab1:
        st.subheader("今日進度上傳")
        uploaded_file = st.file_uploader("上傳今日體態照", type=["jpg", "png"])
        if uploaded_file:
            st.image(Image.open(uploaded_file), width=300)
            st.success("照片已預覽！離目標更進一步了！")

        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            h = st.number_input("身高 (cm)", value=165.0) # 調整預設值更貼近女性
            w = st.number_input("體重 (kg)", value=55.0)
        with col2:
            age = st.number_input("年齡", value=25)
            mult = st.selectbox("夏季活動強度", [1.2, 1.375, 1.55, 1.725])

        if st.button("計算數據並儲存"):
            bmi = w / ((h/100)**2)
            # BMR 公式微調為更適合女性的參數 (Mifflin-St Jeor Formula for women)
            bmr = (10 * w) + (6.25 * h) - (5 * age) - 161
            tdee = bmr * mult
            
            st.session_state.last_tdee = tdee 
            save_data(st.session_state.username, bmi, tdee)
            st.balloons()
            st.metric("您的 BMI", f"{bmi:.2f}")
            st.metric("您的 TDEE (每日消耗)", f"{tdee:.0f} kcal")
            st.info(f"💡 建議每日攝取: {tdee-300:.0f} ~ {tdee-500:.0f} kcal (溫和減脂)")

    with tab2:
        st.subheader("🥗 輕盈食材清單")
        target_cal = st.session_state.get('last_tdee', 1800) - 400
        
        st.write(f"針對您的目標熱量約 **{target_cal:.0f} kcal**，建議採購：")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### 🦐 優質輕蛋白\n- 鮮蝦/海鮮\n- 雞胸肉\n- 嫩豆腐\n- 無糖希臘優格")
        with c2:
            st.markdown("### 🌽 纖維與澱粉\n- 藜麥\n- 地瓜\n- 鷹嘴豆\n- 莓果類 (抗氧化)")
        with c3:
            st.markdown("### 🥬 消水腫蔬菜\n- 菠菜 (補鐵)\n- 蘆筍\n- 小黃瓜\n- 海帶芽")
            
        st.success("🌟 小撇步：多吃富含維生素C的水果（如奇異果、芭樂），有助於合成膠原蛋白喔！")

    with tab3:
        st.subheader("⏰ 女神作息表")
        
        routine = {
            "07:00": "起床 + 溫檸檬水一杯 (美白代謝)",
            "07:30": "晨間瑜伽或伸展 (喚醒身體)",
            "08:30": "營養早餐 (優格+燕麥+雞蛋)",
            "12:30": "午餐 (大量蔬菜+適量蛋白)",
            "16:00": "下午茶 (堅果一小把 或 黑咖啡)",
            "18:30": "晚餐 (清淡為主，減少碳水)",
            "20:00": "有氧運動 / 核心訓練",
            "22:00": "泡澡放鬆 / 肌膚保養時光 ✨",
            "23:00": "美容覺 (睡滿7.5小時)"
        }
        
        for time, task in routine.items():
            st.write(f"**{time}** : {task}")
        
        st.info("💧 水嫩提醒：每天目標飲水量 2500ml 以上，讓皮膚水噹噹！")
