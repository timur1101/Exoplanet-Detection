import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.set_page_config(page_title="ExoHunter 🪐", layout="centered")

# Загрузка 
@st.cache_resource
def load_all():
    model = joblib.load("exoplanet_model.pkl")
    medians = joblib.load("medians.pkl")
    features = joblib.load("features.pkl")
    return model, medians, features

model, medians, features = load_all()

st.title("🪐 ExoHunter")
st.caption("ML поиск экзопланет")

st.divider()

threshold = st.slider("Порог", 0.0, 1.0, 0.3)

# Ввод 
col1, col2 = st.columns(2)

with col1:
    koi_period = st.number_input("Период", 0.0, 1000.0, 10.0)
    koi_prad = st.number_input("Радиус планеты", 0.0, 50.0, 1.0)

with col2:
    koi_srad = st.number_input("Радиус звезды", 0.0, 10.0, 1.0)
    koi_insol = st.number_input("Инсоляция", 0.0, 10000.0, 100.0)

# Предсказание 
if st.button("🔍 Предсказать", use_container_width=True):

    # берём медианы
    input_data = medians.copy()

    # подставляем пользовательские значения
    input_data["koi_period"] = koi_period
    input_data["koi_prad"] = koi_prad
    input_data["koi_srad"] = koi_srad
    input_data["koi_insol"] = koi_insol

    # пересчитываем engineered признаки
    input_data["log_period"] = np.log1p(koi_period)
    input_data["planet_star_radius_ratio"] = koi_prad / koi_srad if koi_srad > 0 else 0
    input_data["log_insol"] = np.log1p(koi_insol)

    # превращаем в DataFrame с правильным порядком колонок
    input_df = pd.DataFrame([input_data])[features]

    proba = model.predict_proba(input_df)[0,1]
    pred = int(proba >= threshold)

    st.divider()

    if pred:
        st.success("✅ Экзопланета")
    else:
        st.error("❌ Ложный сигнал")

    st.metric("Вероятность", f"{proba:.2%}")
    st.progress(float(proba))
