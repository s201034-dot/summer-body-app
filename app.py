import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image # 處理圖片的套件

# --- 基礎設置 ---
st.set_page_config(page_title="Summer Body - 進度追蹤版", page_icon="📸")

# --- 模擬數據庫 ---
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
    if st.button("登入 / 註冊"):
        if user and pw:
            st.session_state.logged_in = True
            st.session_state.username = user
            st.rerun()
else:
    # --- 登入後的私人空間 ---
    st.sidebar.title(f"👤 {st.session_state.username}")
    if st.sidebar.button("登出"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📸 夏季體態紀錄")

    # --- 1. 照片上載功能 ---
    st.subheader("上傳今天的體態照")
    uploaded_file = st.file_uploader("選擇照片...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        # 顯示上傳的照片
        st.image(image, caption=f"{st.session_state.username} 的今日進度", use_container_width=True)
        st.success("照片預覽成功！")

    st.divider()

    # --- 2. 數據計算與紀錄 ---
    st.subheader("數據更新")
    col1, col2 = st.columns(2)
    with col1:
        h = st.number_input("身高 (cm)", value=170.0)
        w = st.number_input("體重 (kg)", value=60.0)
    with col2:
        age = st.number_input("年齡", value=25)
        mult = st.selectbox("活動量", [1.2, 1.375, 1.55, 1.725])

    if st.button("計算並存入紀錄"):
        bmi = w / ((h/100)**2)
        tdee = (10 * w + 6.25 * h - 5 * age + 5) * mult
        save_data(st.session_state.username, bmi, tdee)
        st.balloons()
        st.success(f"紀錄已儲存！BMI: {bmi:.2f}")

    # --- 3. 隱私歷史紀錄 ---
    st.subheader("📋 我的私人歷史數據")
    if os.path.exists(DATA_FILE):
        all_df = pd.read_csv(DATA_FILE)
        user_df = all_df[all_df["用戶"] == st.session_state.username]
        if not user_df.empty:
            st.dataframe(user_df[["日期", "BMI", "TDEE"]], use_container_width=True)
        else:
            st.info("尚無紀錄，開始你的第一天吧！")
