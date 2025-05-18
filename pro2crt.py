import streamlit as st
import pandas as pd
import plotly.express as px

# Load Data
import pandas as pd

forest_df = pd.read_csv(r"C:\Users\Admin\Downloads\forest.csv")
grassland_df = pd.read_csv(r"C:\Users\Admin\Downloads\grassland.csv")

# Harmonize columns
common_cols = list(set(forest_df.columns) & set(grassland_df.columns))
df = pd.concat([forest_df[common_cols], grassland_df[common_cols]], ignore_index=True)

# Preprocessing
df['Date'] = pd.to_datetime(df['Date'])
df['Month'] = df['Date'].dt.month
df['Year'] = df['Date'].dt.year
df['Season'] = df['Month'].apply(lambda x: 'Spring' if x in [3, 4, 5] else (
                                  'Summer' if x in [6, 7, 8] else (
                                  'Fall' if x in [9, 10, 11] else 'Winter')))
df['Observer'] = df['Observer'].astype(str)

# Sidebar Filters
st.sidebar.header("🔍 Filters")
years = sorted(df['Year'].dropna().unique())
locations = df['Location_Type'].dropna().unique()
seasons = df['Season'].unique()

selected_year = st.sidebar.selectbox("Select Year", years)
selected_location = st.sidebar.selectbox("Select Location Type", locations)
selected_season = st.sidebar.selectbox("Select Season", seasons)

# Filtered Data
filtered_df = df[(df['Year'] == selected_year) &
                 (df['Location_Type'] == selected_location) &
                 (df['Season'] == selected_season)]

st.title("🕊️ Bird Monitoring Dashboard")
st.markdown(f"**Showing data for `{selected_location}` habitat in `{selected_season}` `{selected_year}`**")

# Show Table
st.dataframe(filtered_df)

# ===== 📍 Geographic Mapping (If location data exists) =====
if 'Latitude' in df.columns and 'Longitude' in df.columns:
    st.subheader("📍 Bird Observation Map")
    fig_map = px.scatter_mapbox(filtered_df,
                                lat='Latitude', lon='Longitude',
                                hover_name='Plot_Name',
                                hover_data=['Date', 'Temperature', 'Humidity'],
                                color='Location_Type',
                                zoom=4,
                                height=400)
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map)

# ===== 📊 Species Observation Count =====
if 'Plot_Name' in filtered_df.columns:
    st.subheader("📊 Observation Count per Plot")
    plot_counts = filtered_df['Plot_Name'].value_counts().reset_index()
    plot_counts.columns = ['Plot_Name', 'Observations']
    fig_bar = px.bar(plot_counts, x='Plot_Name', y='Observations',
                     title="Observations by Plot")
    st.plotly_chart(fig_bar)

# ===== 📅 Temporal Heatmap (Year vs Month) =====
st.subheader("📅 Temporal Heatmap (Year vs Month)")
heatmap_data = df.groupby(['Year', 'Month']).size().reset_index(name='Count')
fig_heatmap = px.density_heatmap(heatmap_data, x='Month', y='Year', z='Count',
                                 color_continuous_scale='Viridis',
                                 title="Monthly Observation Density")
st.plotly_chart(fig_heatmap)

# ===== 🌡️ Temperature vs Humidity by Plot =====
if 'Temperature' in filtered_df.columns and 'Humidity' in filtered_df.columns:
    st.subheader("🌡️ Temperature vs Humidity by Plot")
    fig_env = px.scatter(filtered_df, x='Temperature', y='Humidity',
                         color='Plot_Name',
                         hover_data=['Date', 'Observer'],
                         title="Environmental Conditions")
    st.plotly_chart(fig_env)

# ===== 🛡️ Conservation Insights =====
if 'PIF_Watchlist_Status' in filtered_df.columns:
    st.subheader("🛡️ Conservation Priority (PIF Watchlist)")
    pif_status = filtered_df['PIF_Watchlist_Status'].value_counts().reset_index()
    pif_status.columns = ['PIF_Watchlist_Status', 'Count']
    fig_pif = px.pie(pif_status, values='Count', names='PIF_Watchlist_Status',
                     title="PIF Watchlist Species Observations")
    st.plotly_chart(fig_pif)

# ===== 📍 High-Activity Zones by Season and Plot =====
st.subheader("📍 High Activity Zones")
activity = df.groupby(['Location_Type', 'Season']).size().reset_index(name='Observations')
fig_activity = px.bar(activity, x='Location_Type', y='Observations', color='Season',
                      title="Seasonal Observation Distribution by Habitat")
st.plotly_chart(fig_activity)
