import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- 基礎設置 ---
st.set_page_config(page_title="Summer Body 2026 - 管理系統", page_icon="🛡️", layout="wide")

# --- 設定管理員邀請碼 ---
ADMIN_SECRET_KEY = "BOSS123" 

# --- 數據處理 ---
DATA_FILE = "user_data.csv"
USER_DB = "users.csv" # 用來存帳號身分

def save_record(username, bmi, tdee):
    new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), username, bmi, tdee]], 
                            columns=["日期", "用戶", "BMI", "TDEE"])
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, new_data], ignore_index=True)
    else:
        df = new_data
    df.to_csv(DATA_FILE, index=False)

# --- 登入與註冊邏輯 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌊 Summer Body 系統入口")
    
    choice = st.radio("選擇操作", ["登入", "新用戶註冊"])
    
    user = st.text_input("用戶名")
    pw = st.text_input("密碼", type="password")
    
    if choice == "新用戶註冊":
        admin_code = st.text_input("管理員邀請碼 (普通用戶請留空)", type="password")
        if st.button("完成註冊"):
            if user and pw:
                role = "admin" if admin_code == ADMIN_SECRET_KEY else "user"
                new_user = pd.DataFrame([[user, pw, role]], columns=['username', 'password', 'role'])
                if os.path.exists(USER_DB):
                    udf = pd.read_csv(USER_DB)
                    if user in udf['username'].values:
                        st.error("該用戶名已被佔用")
                    else:
                        pd.concat([udf, new_user]).to_csv(USER_DB, index=False)
                        st.success(f"註冊成功！身分：{role}")
                else:
                    new_user.to_csv(USER_DB, index=False)
                    st.success(f"註冊成功！身分：{role}")
            else:
                st.warning("請填寫帳號密碼")
                
    else: # 登入邏輯
        if st.button("立即進入"):
            if os.path.exists(USER_DB):
                udf = pd.read_csv(USER_DB)
                match = udf[(udf['username'] == user) & (udf['password'] == pw)]
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.session_state.role = match.iloc[0]['role']
                    st.rerun()
                else:
                    st.error("帳號或密碼錯誤")
            else:
                st.error("目前尚無任何帳號，請先註冊")

else:
    # --- 登入後介面 ---
    st.sidebar.title(f"👤 {st.session_state.username}")
    st.sidebar.info(f"權限層級：{st.session_state.role.upper()}")
    if st.sidebar.button("安全登出"):
        st.session_state.logged_in = False
        st.rerun()

    # 定義分頁 (根據身分決定要不要顯示管理員分頁)
    tabs_list = ["📊 體態追蹤", "🥗 飲食建議", "📅 夏季作息"]
    if st.session_state.role == "admin":
        tabs_list.append("🔑 管理員後台")
    
    tabs = st.tabs(tabs_list)

    # --- Tab 1: 體態追蹤 ---
    with tabs[0]:
        st.subheader("我的進度紀錄")
        h = st.number_input("身高 (cm)", value=165.0)
        w = st.number_input("體重 (kg)", value=55.0)
        age = st.number_input("年齡", value=25)
        mult = st.selectbox("活動強度", [1.2, 1.375, 1.55, 1.725])
        
        if st.button("計算並儲存"):
            bmi = w / ((h/100)**2)
            # 女性 BMR 計算公式
            bmr = (10 * w) + (6.25 * h) - (5 * age) - 161
            tdee = bmr * mult
            st.session_state.last_tdee = tdee
            save_record(st.session_state.username, bmi, tdee)
            st.success(f"已儲存！您的 BMI: {bmi:.2f}")
            st.metric("TDEE 消耗", f"{tdee:.0f} kcal")

    # --- Tab 2: 飲食建議 ---
    with tabs[1]:
        st.subheader("客製化飲食清單")
        target = st.session_state.get('last_tdee', 1800)
        st.write(f"目前建議每日攝取：**{target-400:.0f} kcal**")
        st.markdown("- 🥩 **蛋白質**：雞肉、豆腐、海鮮\n- 🥦 **纖維**：小黃瓜、花椰菜\n- 🍠 **澱粉**：地瓜、糙米")

    # --- Tab 3: 夏季作息 ---
    with tabs[2]:
        st.subheader("建議作息表")
        st.write("- **07:00** 起床飲水\n- **12:30** 清淡午餐\n- **20:00** 居家運動\n- **23:00** 美容睡眠")

    # --- 管理員專屬 Tab ---
    if st.session_state.role == "admin":
        with tabs[3]:
            st.header("🔑 管理員數據中心")
            if os.path.exists(DATA_FILE):
                all_records = pd.read_csv(DATA_FILE)
                st.subheader("📋 全體用戶詳細紀錄")
                st.dataframe(all_records, use_container_width=True)
                
                # 下載按鈕
                csv_data = all_records.to_csv(index=False).encode('utf-8')
                st.download_button("下載數據報表 (CSV)", data=csv_data, file_name="user_data.csv")
            else:
                st.info("目前尚無量測數據。")
