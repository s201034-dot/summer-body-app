import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 基礎設置 ---
st.set_page_config(page_title="Summer Body 2026 - 唯一帳號版", page_icon="🆔", layout="wide")

# --- 檔案路徑 ---
DATA_FILE = "user_data.csv"
USER_DB = "users.csv" 
FRIENDS_FILE = "friends.csv"
MESSAGES_FILE = "messages.csv"

# --- 數據初始化 ---
def init_files():
    if not os.path.exists(USER_DB):
        pd.DataFrame(columns=['username', 'password', 'role', 'v_code']).to_csv(USER_DB, index=False)
    if not os.path.exists(FRIENDS_FILE):
        pd.DataFrame(columns=["user1", "user2", "status"]).to_csv(FRIENDS_FILE, index=False)
    if not os.path.exists(MESSAGES_FILE):
        pd.DataFrame(columns=["sender", "receiver", "content", "time"]).to_csv(MESSAGES_FILE, index=False)

init_files()

# --- 登入與註冊介面 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌊 Summer Body 系統入口")
    choice = st.radio("請選擇操作", ["帳號登入", "新用戶註冊"])
    
    st.divider()
    user = st.text_input("用戶名 (ID)").strip() # .strip() 自動去掉前後空格
    pw = st.text_input("密碼", type="password")
    v_code = st.text_input("個人驗證碼", type="password")

    if choice == "新用戶註冊":
        if st.button("確認註冊並開啟計畫"):
            if user and pw and v_code:
                # 讀取現有用戶清單
                udf = pd.read_csv(USER_DB)
                
                # --- 核心邏輯：檢查名字是否重複 ---
                if user.lower() in udf['username'].str.lower().values:
                    st.error(f"❌ 名字 '{user}' 已經有人使用了！請換一個更有個性的名字。")
                else:
                    # 執行註冊
                    new_user = pd.DataFrame([[user, pw, "user", v_code]], 
                                           columns=['username', 'password', 'role', 'v_code'])
                    pd.concat([udf, new_user]).to_csv(USER_DB, index=False)
                    st.success(f"✅ 歡迎加入，{user}！現在請切換到「帳號登入」頁面。")
                    st.balloons()
            else:
                st.warning("⚠️ 所有欄位（名字、密碼、驗證碼）都必須填寫喔！")
                
    else: # 登入邏輯
        if st.button("立即進入私人後台"):
            udf = pd.read_csv(USER_DB)
            # 登入檢查 (精確匹配)
            match = udf[(udf['username'] == user) & 
                        (udf['password'] == pw) & 
                        (udf['v_code'].astype(str) == str(v_code))]
            
            if not match.empty:
                st.session_state.logged_in = True
                st.session_state.username = user
                st.session_state.role = match.iloc[0]['role']
                st.rerun()
            else:
                st.error("❌ 登入失敗：請檢查用戶名、密碼或驗證碼是否正確。")

else:
    # --- 登入後的畫面 (體態、飲食、聊天分頁) ---
    st.sidebar.title(f"👤 {st.session_state.username}")
    if st.sidebar.button("安全登出"):
        st.session_state.logged_in = False
        st.rerun()

    tabs = st.tabs(["📊 體態追蹤", "🥗 飲食與作息", "💬 健友社群"])

    with tabs[0]:
        st.subheader("我的進度紀錄")
        # (這裡放原本的計算功能...)
        st.info("數據計算功能已準備就緒。")

    with tabs[1]:
        st.subheader("每日建議")
        # (這裡放原本的飲食與有氧建議...)

    with tabs[2]:
        st.subheader("💬 聊天室")
        st.write("在這裡你可以透過 ID 搜尋並加入其他健身戰友。")
        # (這裡放原本的好友與聊天功能...)
