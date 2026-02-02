import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Summer Body 強化中心", page_icon="☀️")
st.title("🌊 Summer Body 強化中心")

# 夏季標題與倒數
summer_start = datetime(2026, 6, 21)
days_left = (summer_start - datetime.now()).days
st.info(f"☀️ 距離夏至目標還有：{days_left} 天")

# 輸入區
age = st.number_input("年齡", value=25)
gen = st.radio("性別 (1=男, 0=女)", options=[1, 0], format_func=lambda x: "男" if x==1 else "女")
h = st.number_input("身高 (cm)", value=170.0)
w = st.number_input("體重 (kg)", value=60.0)
mult = st.select_slider("夏季活動量", options=[1.2, 1.375, 1.55, 1.725], value=1.2)

if st.button("生成夏季塑身建議"):
    bmi = w / ((h/100)**2)
    bmr = (10 * w) + (6.25 * h) - (5 * age) + (5 if gen == 1 else -161)
    tdee = bmr * mult
    st.write(f"### BMI: {bmi:.2f}")
    st.write(f"### 每日消耗 TDEE: {tdee:.0f} kcal")
    st.success(f"💧 夏季建議補水: {w*40:.0f} ml")
    st.warning(f"🔥 夏季塑身建議熱量: {tdee-500:.0f} kcal")
