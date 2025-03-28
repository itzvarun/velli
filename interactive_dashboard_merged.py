
# --------------------------------------------------------
# Import Required Libraries
# --------------------------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --------------------------------------------------------
# Load Dataset
# --------------------------------------------------------
# Define file path
file_path = "AllLocationSchemeCollectionPending.csv"

# Check if file exists
if os.path.exists(file_path):
    df = pd.read_csv(file_path)
else:
    st.error(f"File not found at: {file_path}")
    st.stop()

# Clean and filter data
df = df.dropna(subset=['Location', 'Maturity Date', 'RSOEmp', 'Status', 'Balance Due'])
df['Balance Due'] = pd.to_numeric(df['Balance Due'], errors='coerce')

# --------------------------------------------------------
# Sidebar Configuration
# --------------------------------------------------------
st.sidebar.header("Filter Options")
locations = st.sidebar.multiselect("Select Location", df['Location'].unique())
status_filter = st.sidebar.multiselect("Select Status", df['Status'].unique())

# Apply filters
if locations:
    df = df[df['Location'].isin(locations)]
if status_filter:
    df = df[df['Status'].isin(status_filter)]

# --------------------------------------------------------
# Summary Metrics
# --------------------------------------------------------
st.title("Scheme Collection Dashboard")
if not df.empty:
    st.metric("Total Records", len(df))
    st.metric("Total Balance Due", f"₹ {df['Balance Due'].sum():,.2f}")

    # Grouped data
    grouped_df = df.groupby(['Location', 'Status']).agg({'Balance Due': 'sum'}).reset_index()

    # --------------------------------------------------------
    # Bar Chart for Balance Due by Location and Status
    # --------------------------------------------------------
    st.subheader("Balance Due by Location and Status")
    fig_bar = px.bar(grouped_df, x='Location', y='Balance Due', color='Status', barmode='group')
    st.plotly_chart(fig_bar)

    # --------------------------------------------------------
    # Pie Chart for Scheme Status Distribution (Corrected)
    # --------------------------------------------------------
    st.subheader("Scheme Status Distribution")
    status_counts = df['Status'].value_counts().reset_index()
    status_counts.columns = ["Status", "count"]
    fig_pie = px.pie(status_counts, names='Status', values='count', title='Status Distribution')
    st.plotly_chart(fig_pie)

    # --------------------------------------------------------
    # Tamil Nadu Interactive Map Visualization
    # --------------------------------------------------------
    st.subheader("Tamil Nadu Location Map")

    # Check if latitude and longitude columns are available
    if "Latitude" in df.columns and "Longitude" in df.columns:
        fig_map_tn = px.scatter_geo(
            df,
            lat="Latitude",
            lon="Longitude",
            text="Location",
            size="Balance Due",
            title="Interactive Tamil Nadu Map - Location Wise",
            template="plotly",
            scope="asia"
        )
        fig_map_tn.update_geos(
            center={"lat": 11.1271, "lon": 78.6569},
            projection_scale=6.5
        )
        st.plotly_chart(fig_map_tn)
    else:
        st.warning("Latitude and Longitude columns not found. Using predefined coordinates.")

    # --------------------------------------------------------
    # Map Visualization with Predefined Locations
    # --------------------------------------------------------
    st.subheader("Location-wise Distribution")
    location_df = df.groupby('Location').agg({'Balance Due': 'sum'}).reset_index()
    location_coords = {
        "Sivakasi": [11.67, 78.13],
        "Tirunelveli": [8.73, 77.70],
        "TENKASI": [8.96, 77.30]
    }
    location_df[['lat', 'lon']] = location_df['Location'].apply(lambda x: pd.Series(location_coords.get(x, [None, None])))
    location_df = location_df.dropna(subset=['lat', 'lon'])
    fig_map = px.scatter_geo(location_df, 
                             lat='lat',
                             lon='lon',
                             text='Location',
                             size='Balance Due',
                             title='Location-wise Scheme Balance Due')
    st.plotly_chart(fig_map)

    # --------------------------------------------------------
    # Data Table View
    # --------------------------------------------------------
    st.subheader("Filtered Data Table")
    st.dataframe(df[['Location', 'Maturity Date', 'RSOEmp', 'Status', 'Customer Name', 'Balance Due']])
else:
    st.warning("No data available. Please adjust your filters.")
