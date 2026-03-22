import streamlit as st
import numpy as np
import pandas as pd
import joblib
import plotly.express as px

# LOAD FILES
model = joblib.load("aqi_model.pkl")
scaler = joblib.load("scale.pkl")
city_data = joblib.load("city_avg_feature.pkl")

st.set_page_config(page_title="AQI Analyzer", layout="wide")

# TITLE
st.markdown("<h1 style='text-align:center;'>🌍 AQI Factory Impact Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align:center;'>Check if opening a factory is environmentally safe</h4>", unsafe_allow_html=True)

st.divider()

# INPUT SECTION
st.markdown("<h3 style='text-align:center;'>📥 Enter Environmental Details</h3>", unsafe_allow_html=True)
st.write("")

col1, col2, col3 = st.columns(3)

with col1:
    city = st.selectbox("📍 City", city_data.index)

    temp = st.number_input(
        "🌡️ Temperature (°C)",
        min_value=-20.0,
        max_value=50.0,
        value=25.0,
        step=1.0,
        help="Range: -20 to 50"
    )

    humidity = st.slider(
        "💧 Humidity (%)",
        0, 100, 5, 1
    )

with col2:
    pm25 = st.number_input(
        "PM2.5",
        0.0, 500.0, 50.0,
        help="Fine particles (0–500)"
    )

    pm10 = st.number_input(
        "PM10",
        0.0, 600.0, 80.0,
        help="Coarse particles (0–600)"
    )

    co = st.number_input(
        "CO",
        0, 2000, 50,
        help="Carbon monoxide (0–2000)"
    )

with col3:
    o3 = st.number_input(
        "O3",
        0, 900, 50,
        help="Ozone level (0–900)"
    )

    so2 = st.number_input(
        "🏭 SO2",
        0, 300, 50,
        help="Sulfur dioxide (0–300)"
    )

    no2 = st.number_input(
        "🚦 NO2",
        0, 300, 50,
        help="Nitrogen dioxide (0–300)"
    )

st.divider()

# AQI CATEGORY
def aqi_category(aqi):
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"

# RECOMMENDATION
def recommendation(factor):
    recs = {
        "PM2.5": "Use air filters & reduce emissions",
        "PM10": "Control dust pollution",
        "NO2": "Reduce vehicle usage",
        "SO2": "Install emission control systems",
        "CO": "Improve fuel combustion",
        "O3": "Control chemical emissions"
    }
    return recs.get(factor, "Monitor conditions")



# BUTTON
if st.button("🚀 Predict AQI"):

    input_data = np.array([[temp, humidity, pm25, pm10, co, o3, so2, no2]])
    input_scaled = scaler.transform(input_data)
    predicted_aqi = model.predict(input_scaled)[0]

    city_avg = city_data.loc[city]["AQI"]
    increase = predicted_aqi - city_avg

    st.divider()

    # RESULT CARDS
    st.subheader("📊 Results")
    st.write("")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Predicted AQI", round(predicted_aqi,2))
    c2.metric("City Avg AQI", round(city_avg,2))
    c3.metric("AQI Change", round(increase,2))

    category = aqi_category(predicted_aqi)
    c4.metric("AQI Category", (category))

    st.write("")
    st.write("")

    


    # FACTOR ANALYSIS
    input_values = {
        "PM2.5": pm25,
        "PM10": pm10,
        "CO": co,
        "O3": o3,
        "SO2": so2,
        "NO2": no2
    }

    city_avg_values = city_data.loc[city]

    affect = {}
    for i in input_values:
        if city_avg_values[i] != 0:
            affect[i] = (input_values[i] - city_avg_values[i]) / city_avg_values[i]

    top_factors = pd.Series(affect).sort_values(ascending=False).head(3)
    top_factors = top_factors.abs()


    col_left, col_right = st.columns([1,1])


    # DISPLAY FACTORS
    with col_left:
        st.subheader("⚡ Top Factors Affecting AQI")
        st.write("")

        if not top_factors.empty:
            fig_pie = px.pie(
                values=top_factors.values,
                names=top_factors.index
        )

            fig_pie.update_traces(
                textinfo='percent+label',
                textfont_size=13.5,
                textfont=dict(color='white', size=13, family="Arial Black")
            )

            fig_pie.update_layout(
                showlegend=False,
                height=180, # controls size
                
                margin=dict(t=20, b=20, l=20, r=20)
            )

            st.plotly_chart(fig_pie, use_container_width=False)

    

    #for f in top_factors.index:
        #st.write(f"🔺 {f}")

    # RECOMMENDATIONS
    with col_right:
        st.subheader("💡 Recommendations")
        st.write("")
        st.write("")

        for f in top_factors.index:
            st.write(f"✔️ {recommendation(f)}")




    # FINAL DECISION
    st.subheader("🧾 Final Decision")

    if predicted_aqi <= 100:
        st.balloons()
        st.success("✅ Safe to open factory")

    elif predicted_aqi <= 200 and increase < 30:
        st.warning("⚠️ Open with precautions")

    elif predicted_aqi <= 300:
        st.error("🚨 Risky – strict control needed")

    else:
        st.error("❌ Not recommended")

    
