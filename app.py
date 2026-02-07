import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 基礎設置 ---
st.set_page_config(page_title="Summer Body - 私人隱私版", page_icon="🔒")

# --- 模擬簡單數據庫 (實際應用建議用資料庫) ---
# 這裡為了方便你操作，我們會建立一個本地 CSV 來模擬
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

# --- 登入介面 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌊 Summer Body 登入")
    user = st.text_input("用戶名 (隨便輸入一個名稱開始)")
    pw = st.text_input("密碼", type="password")
    
    if st.button("登入 / 註冊"):
        if user and pw: # 這裡做簡化：只要輸入就代表登入
            st.session_state.logged_in = True
            st.session_state.username = user
            st.rerun()
        else:
            st.error("請輸入用戶名與密碼")
else:
    # --- 登入後的私人空間 ---
    st.sidebar.title(f"👤 您好, {st.session_state.username}")
    if st.sidebar.button("登出"):
        st.session_state.logged_in = False
        st.rerun()

    st.title(f"🏃 {st.session_state.username} 的夏季體態計畫")
    
    # 輸入區
    col1, col2 = st.columns(2)
    with col1:
        h = st.number_input("身高 (cm)", value=170.0)
        w = st.number_input("體重 (kg)", value=60.0)
    with col2:
        age = st.number_input("年齡", value=25)
        mult = st.selectbox("活動量", [1.2, 1.375, 1.55, 1.725])

    if st.button("計算並存入私人紀錄"):
        bmi = w / ((h/100)**2)
        tdee = (10 * w + 6.25 * h - 5 * age + 5) * mult
        save_data(st.session_state.username, bmi, tdee)
        st.success("紀錄已存儲！")
        
        st.metric("您的 BMI", f"{bmi:.2f}")
        st.metric("您的 TDEE", f"{tdee:.0f} kcal")

    # --- 隱私核心：只顯示當前用戶的資料 ---
    st.subheader("📋 我的歷史紀錄 (其他用戶無法查看)")
    if os.path.exists(DATA_FILE):
        all_df = pd.read_csv(DATA_FILE)
        # 過濾功能：只抓取名字等於當前登入者的資料
        user_df = all_df[all_df["用戶"] == st.session_state.username]
        if not user_df.empty:
            st.table(user_df[["日期", "BMI", "TDEE"]])
        else:
            st.write("目前尚無紀錄。")
