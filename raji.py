import streamlit as st
import pandas as pd
import pymysql


connection = pymysql.connect(
    host="localhost",
    user="root",
    password="",
    port=3306,
    database="tennis"
)
cursor = connection.cursor()

# Sidebar by filter
st.sidebar.header('Search & Filter Competitors')

# Search by name
search_name = st.sidebar.text_input('Search Competitor by Name')

# Filter by rank range
rank_min = st.sidebar.slider('Minimum Rank', 1, 100, 1)
rank_max = st.sidebar.slider('Maximum Rank', 1, 100, 100)

# Filter by points threshold
points_min = st.sidebar.slider('Minimum Points', 0, 10000, 0)
points_max = st.sidebar.slider('Maximum Points', 0, 10000, 10000)

# Filter by country
cursor.execute('SELECT DISTINCT country FROM competitors')
country_list = ['All'] + [row[0] for row in cursor.fetchall()]
country_filter = st.sidebar.selectbox('Select Country', country_list)

# SQL Query with JOIN
query = """
SELECT 
    c.competitor_id,
    c.name,
    c.country,
    r.rank,
    r.points,
    r.competitions_played
FROM competitors c
JOIN rankingsss1 r ON c.competitor_id = r.competitor_id
WHERE 1=1
"""

# Apply filters
if search_name:
    query += f" AND c.name LIKE '%{search_name}%'"
if country_filter != 'All':
    query += f" AND c.country = '{country_filter}'"
query += f" AND r.rank BETWEEN {rank_min} AND {rank_max}"
query += f" AND r.points BETWEEN {points_min} AND {points_max}"

# Execute query
competitors_df = pd.read_sql(query, connection)


st.title('TENNIS RANKING EXPLORER')

# Summary Stats
st.subheader('RANKINGS DASHBOARD')
if not competitors_df.empty:
    total_competitors = len(competitors_df)
    num_countries = competitors_df['country'].nunique()
    highest_points = competitors_df['points'].max()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Competitors", total_competitors)
    col2.metric("Countries Represented", num_countries)
    col3.metric("Highest Points", highest_points)
else:
    st.warning("No competitors match the selected filters.")

# Competitor List
st.subheader('📝 Competitor List')
st.dataframe(competitors_df)

# Country-wise analysis
country_analysis_query = """
SELECT
    c.country,
    COUNT(*) AS num_competitors,
    AVG(r.points) AS avg_points,
    MIN(r.rank) AS highest_rank,
    MAX(r.competitions_played) AS max_competitions_played
FROM competitors c
LEFT JOIN rankingsss1 r
    ON c.competitor_id = r.competitor_id
GROUP BY c.country
ORDER BY avg_points DESC
"""
country_data = pd.read_sql(country_analysis_query, connection)
st.subheader('🌍 Country-Wise Analysis')
st.dataframe(country_data)

# Competitor Detail Viewer
if not competitors_df.empty:
    st.subheader('🔍 Competitor Details')
    competitor_name = st.selectbox('Select Competitor', competitors_df['name'].unique())

    if competitor_name:
        competitor = competitors_df[competitors_df['name'] == competitor_name].iloc[0]
        st.write(f"**Name:** {competitor['name']}")
        st.write(f"**Rank:** {competitor['rank']}")
        st.write(f"**Points:** {competitor['points']}")
        st.write(f"**Competitions Played:** {competitor['competitions_played']}")
        st.write(f"**Country:** {competitor['country']}")

# Leaderboards
st.subheader('🏅 Leaderboard - Top Ranked Competitors')
top_ranked_query = """
SELECT c.name, c.country, r.rank, r.points
FROM competitors c
JOIN rankingsss1 r ON c.competitor_id = r.competitor_id
ORDER BY r.rank ASC LIMIT 10
"""
top_ranked_df = pd.read_sql(top_ranked_query, connection)
st.dataframe(top_ranked_df)

st.subheader('🔥 Leaderboard - Highest Points')
top_points_query = """
SELECT c.name, c.country, r.rank, r.points
FROM competitors c
JOIN rankingsss1 r ON c.competitor_id = r.competitor_id
ORDER BY r.points DESC LIMIT 10
"""
top_points_df = pd.read_sql(top_points_query, connection)
st.dataframe(top_points_df)

# Close connection
connection.close()