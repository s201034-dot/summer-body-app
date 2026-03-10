import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# --- 基礎設置 ---
st.set_page_config(page_title="Summer Body 2026 - 安全強化版", page_icon="🔐", layout="wide")

# --- 設定管理員註冊用的邀請碼 ---
ADMIN_SECRET_KEY = "BOSS123" 

# --- 數據處理函數 ---
DATA_FILE = "user_data.csv"
USER_DB = "users.csv" 

def save_record(username, bmi, tdee):
    new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), username, bmi, tdee]], 
                            columns=["日期", "用戶", "BMI", "TDEE"])
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
    st.title("🌊 Summer Body 安全系統")
    
    choice = st.radio("請選擇操作", ["帳號登入", "新用戶註冊"])
    
    st.divider()
    
    # 共用輸入欄位
    user = st.text_input("用戶名 (Username)")
    pw = st.text_input("密碼 (Password)", type="password")
    v_code = st.text_input("個人驗證碼 (Verification Code)", type="password", help="登入時必須輸入正確的驗證碼")

    if choice == "新用戶註冊":
        admin_code = st.text_input("管理員邀請碼 (選填)", type="password")
        if st.button("確認註冊"):
            if user and pw and v_code:
                role = "admin" if admin_code == ADMIN_SECRET_KEY else "user"
                # 建立新用戶資料，包含驗證碼欄位
                new_user = pd.DataFrame([[user, pw, role, v_code]], 
                                       columns=['username', 'password', 'role', 'v_code'])
                
                if os.path.exists(USER_DB):
                    udf = pd.read_csv(USER_DB)
                    if user in udf['username'].values:
                        st.error("❌ 該用戶名已被使用，請換一個。")
                    else:
                        pd.concat([udf, new_user]).to_csv(USER_DB, index=False)
                        st.success(f"✅ 註冊成功！您的身分是：{role}")
                        st.info("💡 請記住您的驗證碼，下次登入需要用到。")
                else:
                    new_user.to_csv(USER_DB, index=False)
                    st.success(f"✅ 註冊成功！身分：{role}")
            else:
                st.warning("⚠️ 請填寫所有必填欄位（帳號、密碼、驗證碼）")
                
    else: # 登入邏輯
        if st.button("立即登入"):
            if os.path.exists(USER_DB):
                udf = pd.read_csv(USER_DB)
                # 同時檢查 帳號、密碼、驗證碼 三者是否匹配
                match = udf[(udf['username'] == user) & 
                            (udf['password'] == pw) & 
                            (udf['v_code'].astype(str) == str(v_code))]
                
                if not match.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.session_state.role = match.iloc[0]['role']
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ 登入失敗：帳號、密碼或驗證碼不正確。")
            else:
                st.error("❌ 系統中尚無帳號資料，請先切換到註冊頁面。")

else:
    # --- 登入後的私人後台 ---
    st.sidebar.title(f"👤 {st.session_state.username}")
    st.sidebar.info(f"當前權限：{st.session_state.role.upper()}")
    if st.sidebar.button("安全登出"):
        st.session_state.logged_in = False
        st.rerun()

    # 定義功能分頁
    tabs_list = ["📊 體態追蹤", "🥗 飲食建議", "📅 夏季作息"]
    if st.session_state.role == "admin":
        tabs_list.append("🔑 管理員總覽")
    
    tabs = st.tabs(tabs_list)

    with tabs[0]:
        st.subheader("我的健康紀錄")
        h = st.number_input("身高 (cm)", value=165.0)
        w = st.number_input("體重 (kg)", value=55.0)
        age = st.number_input("年齡", value=25)
        mult = st.selectbox("活動強度", [1.2, 1.375, 1.55, 1.725])
        
        if st.button("計算並儲存數據"):
            bmi = w / ((h/100)**2)
            bmr = (10 * w) + (6.25 * h) - (5 * age) - 161
            tdee = bmr * mult
            st.session_state.last_tdee = tdee
            save_record(st.session_state.username, bmi, tdee)
            st.success("✅ 數據已更新！")
            st.metric("您的 BMI", f"{bmi:.2f}")
            st.metric("TDEE (每日所需)", f"{tdee:.0f} kcal")

    with tabs[1]:
        st.subheader("🍴 夏季飲食建議")
        tdee_val = st.session_state.get('last_tdee', 1800)
        st.write(f"目標每日攝取：**{tdee_val-400:.0f} kcal**")
        st.info("多吃高纖維蔬菜，補充優質蛋白質（如雞胸、魚肉）。")

    with tabs[2]:
        st.subheader("☀️ 夏季生活規律")
        st.write("1. 每天飲水 2000cc 以上\n2. 晚上 11 點前入睡\n3. 保持心情愉快！")

    if st.session_state.role == "admin":
        with tabs[3]:
            st.header("🔑 管理員控制台")
            if os.path.exists(DATA_FILE):
                all_records = pd.read_csv(DATA_FILE)
                st.subheader("全體用戶量測紀錄")
                st.dataframe(all_records, use_container_width=True)
                
                csv_data = all_records.to_csv(index=False).encode('utf-8')
                st.download_button("匯出所有數據 (CSV)", data=csv_data, file_name="master_data.csv")
            else:
                st.info("目前還沒有用戶儲存過數據。")
