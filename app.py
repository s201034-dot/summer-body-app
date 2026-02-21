import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- 基礎設置 ---
st.set_page_config(page_title="Summer Body 2026 - 全方位教練", page_icon="🥗", layout="wide")

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
    user = st.text_input("用戶名")
    pw = st.text_input("密碼", type="password")
    if st.button("進入私人中心"):
        if user and pw:
            st.session_state.logged_in = True
            st.session_state.username = user
            st.rerun()
else:
    # --- 側邊欄 ---
    st.sidebar.title(f"👤 {st.session_state.username}")
    if st.sidebar.button("登出"):
        st.session_state.logged_in = False
        st.rerun()

    # --- 主頁面標題 ---
    st.title(f"☀️ {st.session_state.username} 的夏季強化日誌")
    
    # 建立分頁
    tab1, tab2, tab3 = st.tabs(["📊 體態追蹤", "🥗 飲食建議", "📅 夏季作息"])

    with tab1:
        st.subheader("今日進度上傳")
        uploaded_file = st.file_uploader("上傳今日體態照", type=["jpg", "png"])
        if uploaded_file:
            st.image(Image.open(uploaded_file), width=300)
            st.success("照片已預覽！")

        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            h = st.number_input("身高 (cm)", value=170.0)
            w = st.number_input("體重 (kg)", value=60.0)
        with col2:
            age = st.number_input("年齡", value=25)
            mult = st.selectbox("夏季活動強度", [1.2, 1.375, 1.55, 1.725])

        if st.button("計算數據並儲存"):
            bmi = w / ((h/100)**2)
            tdee = (10 * w + 6.25 * h - 5 * age + 5) * mult
            st.session_state.last_tdee = tdee # 暫存用於飲食建議
            save_data(st.session_state.username, bmi, tdee)
            st.balloons()
            st.metric("您的 TDEE", f"{tdee:.0f} kcal")
            st.info(f"💡 建議每日攝取: {tdee-500:.0f} kcal (減脂期)")

    with tab2:
        st.subheader("🍴 推薦食材清單")
        target_cal = st.session_state.get('last_tdee', 2000) - 500
        
        st.write(f"針對您的目標熱量 **{target_cal:.0f} kcal**，建議採購：")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### 🥩 優質蛋白\n- 雞胸肉\n- 鯛魚片\n- 雞蛋\n- 希臘優格")
        with c2:
            st.markdown("### 🍠 低GI澱粉\n- 地瓜\n- 糙米\n- 燕麥\n- 南瓜")
        with c3:
            st.markdown("### 🥒 夏季蔬菜\n- 小黃瓜 (消暑)\n- 番茄\n- 綠花椰菜\n- 冬瓜 (利尿)")
            
        st.warning("⚠️ 提醒：夏天容易沒食欲，建議少量多餐，並確保補足蛋白質。")

    with tab3:
        st.subheader("⏰ 建議夏季作息表")
        
        routine = {
            "07:00": "起床 + 飲水 500ml (啟動代謝)",
            "07:30": "晨間伸展或室外快走 (避開高溫)",
            "08:30": "高蛋白早餐",
            "12:00": "原型食物午餐 (多吃消暑蔬菜)",
            "15:00": "補充水分 + 一小份水果",
            "18:00": "晚餐 (減少澱粉比例)",
            "20:00": "室內運動 / 力量訓練",
            "22:30": "放下手機，準備就寢",
            "23:00": "進入深度睡眠 (生長激素分泌)"
        }
        
        for time, task in routine.items():
            st.write(f"**{time}** : {task}")
        
        st.info("💡 貼心提醒：夏天排汗量大，作息中請隨時補充水分，每天建議飲水量為：體重 x 40ml")
