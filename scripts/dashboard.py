# ================================================
# Air Pollution Analysis Dashboard
# Tool: Streamlit
# ================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import numpy as np

# ------------------------------------------------
# Page Configuration
# ------------------------------------------------
st.set_page_config(
    page_title="Air Pollution Analysis India",
    page_icon="🌫️",
    layout="wide"
)

# ------------------------------------------------
# Load Data
# ------------------------------------------------
@st.cache_data
def load_data():
    city_aqi = pd.read_csv("/workspaces/air-pollution-project/results/city_aqi.csv",
                           names=["City", "Avg_AQI"])
    top10 = pd.read_csv("/workspaces/air-pollution-project/results/top10_cities.csv",
                        names=["City", "Avg_AQI"])
    year_aqi = pd.read_csv("/workspaces/air-pollution-project/results/year_aqi.csv",
                           names=["Year", "Avg_AQI"])
    month_aqi = pd.read_csv("/workspaces/air-pollution-project/results/month_aqi.csv",
                            names=["Month", "Avg_AQI"])
    aqi_cat = pd.read_csv("/workspaces/air-pollution-project/results/aqi_category.csv",
                          names=["Category", "Count"])
    severe = pd.read_csv("/workspaces/air-pollution-project/results/severe_days.csv",
                         names=["City", "Severe_Days"])
    corr = pd.read_csv("/workspaces/air-pollution-project/results/correlation.csv",
                       names=["Pollutant", "Correlation"])
    city_month = pd.read_csv("/workspaces/air-pollution-project/results/city_month_aqi.csv",
                             names=["City", "Month", "Avg_AQI"])
    cleaned = pd.read_csv("/workspaces/air-pollution-project/data/cleaned/cleaned_data.csv",
                          names=["City", "Date", "Year", "Month",
                                 "PM25", "PM10", "NO", "NO2", "NOx",
                                 "NH3", "CO", "SO2", "O3",
                                 "Benzene", "Toluene", "Xylene",
                                 "AQI", "AQI_Bucket"])
    return city_aqi, top10, year_aqi, month_aqi, aqi_cat, severe, corr, city_month, cleaned

city_aqi, top10, year_aqi, month_aqi, aqi_cat, severe, corr, city_month, cleaned = load_data()

# Clean numeric columns
city_aqi["Avg_AQI"] = pd.to_numeric(city_aqi["Avg_AQI"], errors="coerce")
top10["Avg_AQI"] = pd.to_numeric(top10["Avg_AQI"], errors="coerce")
year_aqi["Avg_AQI"] = pd.to_numeric(year_aqi["Avg_AQI"], errors="coerce")
month_aqi["Avg_AQI"] = pd.to_numeric(month_aqi["Avg_AQI"], errors="coerce")
aqi_cat["Count"] = pd.to_numeric(aqi_cat["Count"], errors="coerce")
severe["Severe_Days"] = pd.to_numeric(severe["Severe_Days"], errors="coerce")
corr["Correlation"] = pd.to_numeric(corr["Correlation"], errors="coerce")
city_month["Avg_AQI"] = pd.to_numeric(city_month["Avg_AQI"], errors="coerce")
city_month["Month"] = pd.to_numeric(city_month["Month"], errors="coerce")

# Drop header rows
city_aqi = city_aqi[city_aqi["City"] != "City"].dropna()
top10 = top10[top10["City"] != "City"].dropna()
year_aqi = year_aqi[year_aqi["Year"] != "Year"].dropna()
month_aqi = month_aqi[month_aqi["Month"] != "Month"].dropna()
aqi_cat = aqi_cat[aqi_cat["Category"] != "Category"].dropna()
severe = severe[severe["City"] != "City"].dropna()
corr = corr[corr["Pollutant"] != "Pollutant"].dropna()
city_month = city_month[city_month["City"] != "City"].dropna()
cleaned = cleaned[cleaned["City"] != "City"].dropna()

# Month names
month_names = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr",
               5:"May", 6:"Jun", 7:"Jul", 8:"Aug",
               9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}

# AQI Category
def get_aqi_color(aqi):
    if aqi <= 50: return "🟢 Good"
    elif aqi <= 100: return "🟡 Satisfactory"
    elif aqi <= 200: return "🟠 Moderate"
    elif aqi <= 300: return "🔴 Poor"
    elif aqi <= 400: return "🔴 Very Poor"
    else: return "⚫ Severe"

def get_health_message(aqi):
    if aqi <= 50:
        return "✅ Air quality is Good. Safe for everyone!"
    elif aqi <= 100:
        return "✅ Air quality is Satisfactory. Safe for most people."
    elif aqi <= 200:
        return "⚠️ Moderate pollution. Sensitive people should limit outdoor activity."
    elif aqi <= 300:
        return "⚠️ Poor air quality. Everyone may feel health effects."
    elif aqi <= 400:
        return "🚨 Very Poor! Serious health effects for everyone."
    else:
        return "🚨 Severe! Emergency conditions. Avoid all outdoor activity!"

# ------------------------------------------------
# Train ML Model
# ------------------------------------------------
@st.cache_resource
def train_model():
    df = cleaned.copy()
    df["PM25"] = pd.to_numeric(df["PM25"], errors="coerce")
    df["PM10"] = pd.to_numeric(df["PM10"], errors="coerce")
    df["NO2"] = pd.to_numeric(df["NO2"], errors="coerce")
    df["CO"] = pd.to_numeric(df["CO"], errors="coerce")
    df["SO2"] = pd.to_numeric(df["SO2"], errors="coerce")
    df["NO"] = pd.to_numeric(df["NO"], errors="coerce")
    df["AQI"] = pd.to_numeric(df["AQI"], errors="coerce")
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce")

    le = LabelEncoder()
    df["City_Index"] = le.fit_transform(df["City"].astype(str))

    features = ["City_Index", "Month", "PM25", "PM10", "NO", "NO2", "CO", "SO2"]
    df = df[features + ["AQI"]].dropna()

    X = df[features]
    y = df["AQI"]

    model = LinearRegression()
    model.fit(X, y)

    return model, le

model, le = train_model()

# ------------------------------------------------
# Header
# ------------------------------------------------
st.title("🌫️ Air Pollution Analysis Dashboard")
st.markdown("**India Air Quality Analysis 2015-2020 | Hadoop Ecosystem Project**")
st.markdown("---")

# ------------------------------------------------
# Tabs
# ------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🏙️ City Analysis",
    "📈 Trends",
    "🔬 Pollutants",
    "🔮 Predict AQI"
])

# ------------------------------------------------
# Tab 1: Overview
# ------------------------------------------------
with tab1:
    st.header("📊 Project Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Most Polluted City",
                  city_aqi.loc[city_aqi["Avg_AQI"].idxmax(), "City"],
                  f"AQI {city_aqi['Avg_AQI'].max():.0f}")
    with col2:
        st.metric("Cleanest City",
                  city_aqi.loc[city_aqi["Avg_AQI"].idxmin(), "City"],
                  f"AQI {city_aqi['Avg_AQI'].min():.0f}")
    with col3:
        st.metric("Average AQI India",
                  f"{city_aqi['Avg_AQI'].mean():.0f}",
                  "Moderate Range")
    with col4:
        st.metric("Cities Analyzed", "26", "2015-2020")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Average AQI by City")
        fig = px.bar(
            city_aqi.sort_values("Avg_AQI", ascending=True),
            x="Avg_AQI", y="City",
            orientation="h",
            color="Avg_AQI",
            color_continuous_scale="RdYlGn_r",
            title="Average AQI by City"
        )
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("AQI Category Distribution")
        aqi_colors = {
            "Good": "#00B050",
            "Satisfactory": "#92D050",
            "Moderate": "#FFFF00",
            "Poor": "#FF7C00",
            "Very Poor": "#FF0000",
            "Severe": "#7030A0"
        }
        fig = px.pie(
            aqi_cat,
            values="Count",
            names="Category",
            color="Category",
            color_discrete_map=aqi_colors,
            title="AQI Category Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Tab 2: City Analysis
# ------------------------------------------------
with tab2:
    st.header("🏙️ City Analysis")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Most Polluted Cities")
        fig = px.bar(
            top10.sort_values("Avg_AQI", ascending=False),
            x="City", y="Avg_AQI",
            color="Avg_AQI",
            color_continuous_scale="Reds",
            text="Avg_AQI",
            title="Top 10 Most Polluted Cities"
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Severe Pollution Days by City")
        fig = px.bar(
            severe.sort_values("Severe_Days", ascending=True),
            x="Severe_Days", y="City",
            orientation="h",
            color="Severe_Days",
            color_continuous_scale="Reds",
            text="Severe_Days",
            title="Severe + Very Poor Pollution Days"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("City vs Month AQI Heatmap")
    city_month_pivot = city_month.copy()
    city_month_pivot["Month_Name"] = city_month_pivot["Month"].map(month_names)
    pivot_table = city_month_pivot.pivot_table(
        index="City",
        columns="Month_Name",
        values="Avg_AQI"
    )
    month_order = ["Jan","Feb","Mar","Apr","May","Jun",
                   "Jul","Aug","Sep","Oct","Nov","Dec"]
    pivot_table = pivot_table.reindex(columns=month_order)
    fig = px.imshow(
        pivot_table,
        color_continuous_scale="RdYlGn_r",
        title="City vs Month AQI Heatmap",
        aspect="auto"
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Tab 3: Trends
# ------------------------------------------------
with tab3:
    st.header("📈 AQI Trends")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Year-wise AQI Trend")
        fig = px.line(
            year_aqi,
            x="Year", y="Avg_AQI",
            markers=True,
            title="Year-wise AQI Trend (2015-2020)",
            color_discrete_sequence=["steelblue"]
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Monthly AQI Trend")
        month_aqi_copy = month_aqi.copy()
        month_aqi_copy["Month"] = pd.to_numeric(
            month_aqi_copy["Month"], errors="coerce")
        month_aqi_copy = month_aqi_copy.dropna()
        month_aqi_copy = month_aqi_copy.sort_values("Month")
        month_aqi_copy["Month_Name"] = month_aqi_copy["Month"].map(month_names)
        fig = px.line(
            month_aqi_copy,
            x="Month_Name", y="Avg_AQI",
            markers=True,
            title="Monthly AQI Trend (Seasonal Patterns)",
            color_discrete_sequence=["darkgreen"]
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("City Specific Monthly Trend")
    selected_city = st.selectbox(
        "Select City:",
        sorted(city_month["City"].unique()),
        key="trend_city"
    )
    city_data = city_month[city_month["City"] == selected_city].copy()
    city_data = city_data.sort_values("Month")
    city_data["Month_Name"] = city_data["Month"].map(month_names)
    fig = px.line(
        city_data,
        x="Month_Name", y="Avg_AQI",
        markers=True,
        title=f"Monthly AQI Trend — {selected_city}",
        color_discrete_sequence=["red"]
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Tab 4: Pollutants
# ------------------------------------------------
with tab4:
    st.header("🔬 Pollutant Analysis")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Pollutant Correlation with AQI")
        fig = px.bar(
            corr.sort_values("Correlation", ascending=True),
            x="Correlation", y="Pollutant",
            orientation="h",
            color="Correlation",
            color_continuous_scale="RdBu",
            title="Pollutant Correlation with AQI"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("PM2.5 vs AQI Scatter Plot")
        cleaned_numeric = cleaned.copy()
        cleaned_numeric["PM25"] = pd.to_numeric(
            cleaned_numeric["PM25"], errors="coerce")
        cleaned_numeric["AQI"] = pd.to_numeric(
            cleaned_numeric["AQI"], errors="coerce")
        cleaned_numeric = cleaned_numeric[
            (cleaned_numeric["PM25"] > 0) &
            (cleaned_numeric["PM25"] <= 500) &
            (cleaned_numeric["AQI"] > 0) &
            (cleaned_numeric["AQI"] <= 500)
        ].dropna()
        fig = px.scatter(
            cleaned_numeric.sample(2000),
            x="PM25", y="AQI",
            color="City",
            trendline="ols",
            title="PM2.5 vs AQI Scatter Plot"
        )
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Tab 5: Predict AQI
# ------------------------------------------------
with tab5:
    st.header("🔮 Predict AQI")
    st.markdown("Enter pollutant values to predict AQI")

    col1, col2 = st.columns(2)

    with col1:
        city = st.selectbox(
            "Select City:",
            sorted(cleaned["City"].unique()),
            key="predict_city"
        )
        month = st.selectbox(
            "Select Month:",
            options=list(month_names.keys()),
            format_func=lambda x: month_names[x],
            key="predict_month"
        )
        pm25 = st.slider("PM2.5", 0, 500, 100)
        pm10 = st.slider("PM10", 0, 600, 150)

    with col2:
        no = st.slider("NO", 0, 200, 20)
        no2 = st.slider("NO2", 0, 200, 30)
        co = st.slider("CO", 0, 200, 10)
        so2 = st.slider("SO2", 0, 100, 10)

    if st.button("🔮 Predict AQI", type="primary"):
        try:
            city_index = le.transform([city])[0]
        except:
            city_index = 0

        input_data = np.array([[
            city_index, month,
            pm25, pm10, no, no2, co, so2
        ]])

        predicted_aqi = model.predict(input_data)[0]
        predicted_aqi = max(0, min(500, predicted_aqi))

        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Predicted AQI", f"{predicted_aqi:.0f}")
        with col2:
            st.metric("Category", get_aqi_color(predicted_aqi))
        with col3:
            st.metric("City", city)

        st.info(get_health_message(predicted_aqi))

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=predicted_aqi,
            title={"text": f"Predicted AQI — {city}"},
            gauge={
                "axis": {"range": [0, 500]},
                "bar": {"color": "darkred"},
                "steps": [
                    {"range": [0, 50],    "color": "#00B050"},
                    {"range": [50, 100],  "color": "#92D050"},
                    {"range": [100, 200], "color": "#FFFF00"},
                    {"range": [200, 300], "color": "#FF7C00"},
                    {"range": [300, 400], "color": "#FF0000"},
                    {"range": [400, 500], "color": "#7030A0"}
                ],
                "threshold": {
                    "line": {"color": "black", "width": 4},
                    "thickness": 0.75,
                    "value": predicted_aqi
                }
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# Footer
# ------------------------------------------------
st.markdown("---")
st.markdown("**Air Pollution Analysis | Hadoop Ecosystem Project | R + Spark + Pig + HDFS**")