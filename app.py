import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- 基礎設置 ---
st.set_page_config(page_title="Summer Body 2026 - 全方位強化版", page_icon="🏃‍♀️", layout="wide")

# --- 管理員金鑰 ---
ADMIN_SECRET_KEY = "BOSS123" 

# --- 數據處理 ---
DATA_FILE = "user_data.csv"
USER_DB = "users.csv" 

def save_record(username, bmi, tdee, workouts_per_week):
    new_data = pd.DataFrame([[
        datetime.now().strftime("%Y-%m-%d %H:%M"), 
        username, bmi, tdee, f"一週 {workouts_per_week} 次"
    ]], columns=["日期", "用戶", "BMI", "TDEE", "運動頻率"])
    
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data
    df.to_csv(DATA_FILE, index=False)

# --- 登入與註冊介面 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌊 Summer Body 系統入口")
    choice = st.radio("操作", ["帳號登入", "新用戶註冊"])
    st.divider()
    user = st.text_input("用戶名")
    pw = st.text_input("密碼", type="password")
    v_code = st.text_input("個人驗證碼", type="password")

    if choice == "新用戶註冊":
        admin_code = st.text_input("管理員邀請碼 (選填)", type="password")
        if st.button("確認註冊"):
            if user and pw and v_code:
                role = "admin" if admin_code == ADMIN_SECRET_KEY else "user"
                new_user = pd.DataFrame([[user, pw, role, v_code]], columns=['username', 'password', 'role', 'v_code'])
                if os.path.exists(USER_DB):
                    udf = pd.read_csv(USER_DB)
                    if user in udf['username'].values:
                        st.error("❌ 名稱重複")
                    else:
                        pd.concat([udf, new_user]).to_csv(USER_DB, index=False)
                        st.success("✅ 註冊成功")
                else:
                    new_user.to_csv(USER_DB, index=False)
                    st.success("✅ 註冊成功")
    else:
        if st.button("立即登入"):
            if os.path.exists(USER_DB):
                udf = pd.read_csv(USER_DB)
                match = udf[(udf['username'] == user) & (udf['password'] == pw) & (udf['v_code'].astype(str) == str(v_code))]
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.session_state.role = match.iloc[0]['role']
                    st.rerun()
                else:
                    st.error("❌ 驗證失敗")

else:
    # --- 登入後介面 ---
    st.sidebar.title(f"👤 {st.session_state.username}")
    if st.sidebar.button("安全登出"):
        st.session_state.logged_in = False
        st.rerun()

    tabs = st.tabs(["📊 體態追蹤", "🥗 飲食與作息", "🔑 管理後台"] if st.session_state.role == "admin" else ["📊 體態追蹤", "🥗 飲食與作息"])

    with tabs[0]:
        st.subheader("📋 輸入今日數據")
        col1, col2 = st.columns(2)
        with col1:
            h = st.number_input("身高 (cm)", value=165.0)
            w = st.number_input("體重 (kg)", value=55.0)
        with col2:
            age = st.number_input("年齡", value=25)
            workouts = st.number_input("每週平均運動天數 (0-7天)", min_value=0, max_value=7, value=3, step=1)
        
        if st.button("計算並儲存紀錄"):
            if workouts == 0: mult = 1.2
            elif 1 <= workouts <= 2: mult = 1.375
            elif 3 <= workouts <= 5: mult = 1.55
            else: mult = 1.725
                
            bmi = w / ((h/100)**2)
            bmr = (10 * w) + (6.25 * h) - (5 * age) - 161
            tdee = bmr * mult
            st.session_state.last_tdee = tdee
            
            save_record(st.session_state.username, bmi, tdee, workouts)
            st.success(f"✅ 已儲存！您的 TDEE 為 {tdee:.0f} kcal")
            st.metric("BMI", f"{bmi:.2f}")

    with tabs[1]:
        st.subheader("🥗 夏季建議")
        tdee_val = st.session_state.get('last_tdee', 1800)
        
        col_diet, col_routine = st.columns(2)
        
        with col_diet:
            st.markdown("#### 🍴 飲食目標")
            st.write(f"🔥 減脂建議攝取：**{tdee_val-400:.0f} kcal**")
            st.markdown("- **優質蛋白**：雞肉、海鮮、豆漿\n- **消暑蔬菜**：小黃瓜、冬瓜、生菜\n- **多喝水**：目標每日 2500ml")
        
        with col_routine:
            st.markdown("#### ⏰ 建議作息與運動")
            st.write("**07:00** 起床飲水")
            st.write("**12:30** 輕食午餐")
            # --- 加入有氧運動 ---
            st.markdown("**20:00 🏃 有氧運動時間**")
            st.info("建議進行 30 分鐘有氧：\n- **室外**：慢跑、快走、騎單車\n- **室內**：開合跳 50下x3組、跳繩、波比跳")
            st.write("**23:00** 深度睡眠")

    if st.session_state.role == "admin":
        with tabs[2]:
            st.header("🔑 管理員數據總覽")
            if os.path.exists(DATA_FILE):
                st.dataframe(pd.read_csv(DATA_FILE), use_container_width=True)
