import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 基礎設置 ---
st.set_page_config(page_title="Summer Body 2026 - 全功能社群版", page_icon="🏋️‍♀️", layout="wide")

# --- 檔案路徑與初始化 ---
USER_DB = "users.csv"
DATA_FILE = "user_data.csv"
FRIENDS_FILE = "friends.csv"
MESSAGES_FILE = "messages.csv"

def init_files():
    if not os.path.exists(USER_DB):
        pd.DataFrame(columns=['username', 'password', 'role', 'v_code']).to_csv(USER_DB, index=False)
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=["日期", "用戶", "BMI", "TDEE", "運動頻率"]).to_csv(DATA_FILE, index=False)
    if not os.path.exists(FRIENDS_FILE):
        pd.DataFrame(columns=["user1", "user2", "status"]).to_csv(FRIENDS_FILE, index=False)
    if not os.path.exists(MESSAGES_FILE):
        pd.DataFrame(columns=["sender", "receiver", "content", "time"]).to_csv(MESSAGES_FILE, index=False)

init_files()

# --- 邏輯函數 ---
def save_record(username, bmi, tdee, workouts):
    new_data = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d %H:%M"), username, f"{bmi:.2f}", f"{tdee:.0f}", f"一週{workouts}次"]], 
                            columns=["日期", "用戶", "BMI", "TDEE", "運動頻率"])
    df = pd.read_csv(DATA_FILE)
    pd.concat([df, new_data], ignore_index=True).to_csv(DATA_FILE, index=False)

# --- 登入/註冊頁面 ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌊 Summer Body 2026")
    mode = st.radio("模式", ["登入", "註冊新帳號"])
    user_input = st.text_input("用戶名 (ID)").strip()
    pw_input = st.text_input("密碼", type="password")
    v_input = st.text_input("個人驗證碼", type="password")

    if mode == "註冊新帳號":
        if st.button("完成註冊"):
            udf = pd.read_csv(USER_DB)
            if user_input.lower() in udf['username'].str.lower().values:
                st.error("❌ 這個名字已經被拿走了！")
            elif user_input and pw_input and v_input:
                new_u = pd.DataFrame([[user_input, pw_input, "user", v_input]], columns=udf.columns)
                pd.concat([udf, new_u]).to_csv(USER_DB, index=False)
                st.success("✅ 註冊成功！請切換到登入模式。")
            else:
                st.warning("⚠️ 請填寫完整資料")
    else:
        if st.button("立即登入"):
            udf = pd.read_csv(USER_DB)
            match = udf[(udf['username'] == user_input) & (udf['password'] == pw_input) & (udf['v_code'].astype(str) == str(v_input))]
            if not match.empty:
                st.session_state.logged_in = True
                st.session_state.username = user_input
                st.rerun()
            else:
                st.error("❌ 帳號、密碼或驗證碼錯誤")

else:
    # --- 登入後主界面 ---
    st.sidebar.title(f"👤 {st.session_state.username}")
    if st.sidebar.button("登出系統"):
        st.session_state.logged_in = False
        st.rerun()

    tabs = st.tabs(["📊 體態計算頁", "🥗 飲食與有氧", "💬 健友社群"])

    # --- Tab 1: 計算頁 ---
    with tabs[0]:
        st.header("⚖️ 體態數據分析")
        col1, col2 = st.columns(2)
        with col1:
            h = st.number_input("身高 (cm)", value=165.0, step=0.1)
            w = st.number_input("體重 (kg)", value=55.0, step=0.1)
        with col2:
            age = st.number_input("年齡", value=25, step=1)
            workouts = st.number_input("每週平均運動天數", min_value=0, max_value=7, value=3)

        if st.button("開始計算並存檔"):
            # TDEE 邏輯
            if workouts == 0: m = 1.2
            elif 1 <= workouts <= 2: m = 1.375
            elif 3 <= workouts <= 5: m = 1.55
            else: m = 1.725
            
            bmi = w / ((h/100)**2)
            bmr = (10 * w) + (6.25 * h) - (5 * age) - 161 # 女性公式
            tdee = bmr * m
            st.session_state.tdee = tdee
            
            save_record(st.session_state.username, bmi, tdee, workouts)
            
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("您的 BMI", f"{bmi:.2f}")
            c2.metric("基礎代謝 BMR", f"{bmr:.0f} kcal")
            c3.metric("每日總消耗 TDEE", f"{tdee:.0f} kcal")
            st.balloons()

    # --- Tab 2: 飲食與作息 ---
    with tabs[1]:
        st.header("🥗 每日生活指南")
        t_val = st.session_state.get('tdee', 1800)
        
        c_diet, c_ex = st.columns(2)
        with c_diet:
            st.subheader("🍴 飲食建議")
            st.write(f"🔥 減脂建議攝取：**{t_val-400:.0f} kcal**")
            st.markdown("- **食材**：雞胸肉、小黃瓜、冬瓜、雞蛋\n- **水分**：每天飲用 2500ml")
        with c_ex:
            st.subheader("🏃 有氧運動建議")
            st.markdown("**晚上 20:00 推薦項目：**")
            st.info("1. **開合跳**：50下為一組，共3組\n2. **跑步**：慢跑 30 分鐘\n3. **跳繩**：累計 500 下")

    # --- Tab 3: 聊天功能 ---
    with tabs[2]:
        st.header("💬 健友社群")
        c_f, c_m = st.columns([1, 2])
        
        with c_f:
            st.subheader("👥 好友")
            target = st.text_input("輸入對方 ID 申請好友")
            if st.button("發送"):
                f_df = pd.read_csv(FRIENDS_FILE)
                if target != st.session_state.username:
                    new_f = pd.DataFrame([[st.session_state.username, target, 'pending']], columns=f_df.columns)
                    pd.concat([f_df, new_f]).to_csv(FRIENDS_FILE, index=False)
                    st.success("申請已送出")
            
            st.write("---")
            st.write("📩 待處理")
            f_df = pd.read_csv(FRIENDS_FILE)
            incoming = f_df[(f_df['user2'] == st.session_state.username) & (f_df['status'] == 'pending')]
            for _, row in incoming.iterrows():
                if st.button(f"接受 {row['user1']}", key=row['user1']):
                    f_df.loc[(f_df['user1']==row['user1']) & (f_df['user2']==st.session_state.username), 'status'] = 'accepted'
                    f_df.to_csv(FRIENDS_FILE, index=False)
                    st.rerun()

        with c_m:
            st.subheader("💌 私訊")
            f_df = pd.read_csv(FRIENDS_FILE)
            friends = []
            f_rows = f_df[((f_df['user1']==st.session_state.username) | (f_df['user2']==st.session_state.username)) & (f_df['status']=='accepted')]
            for _, r in f_rows.iterrows():
                friends.append(r['user2'] if r['user1']==st.session_state.username else r['user1'])
            
            if friends:
                chat_with = st.selectbox("跟誰聊天?", friends)
                msg_df = pd.read_csv(MESSAGES_FILE)
                history = msg_df[((msg_df['sender']==st.session_state.username) & (msg_df['receiver']==chat_with)) | 
                                 ((msg_df['sender']==chat_with) & (msg_df['receiver']==st.session_state.username))]
                
                for _, m in history.iterrows():
                    st.write(f"**{m['sender']}**: {m['content']} ({m['time']})")
                
                with st.form("send_msg", clear_on_submit=True):
                    txt = st.text_input("輸入訊息")
                    if st.form_submit_button("傳送"):
                        new_m = pd.DataFrame([[st.session_state.username, chat_with, txt, datetime.now().strftime("%H:%M")]], columns=msg_df.columns)
                        pd.concat([msg_df, new_m]).to_csv(MESSAGES_FILE, index=False)
                        st.rerun()
